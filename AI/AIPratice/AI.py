import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import json
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from transformers import BertTokenizer, BertModel, get_linear_schedule_with_warmup


# ====================== 配置参数（优化版）=====================
class Config:
    bert_path = "bert-base-chinese"  # 自动下载官方模型
    save_model_path = "D:\\GridFriend\\AI\\LoadModels\\best_emotion_model.pth"
    max_len = 128  # 文本最大长度
    batch_size = 32  # 降低batch_size，提升稳定性
    epochs = 10  # 增加训练轮次
    lr = 2e-5  # 降低学习率，避免震荡
    weight_decay = 1e-4  # 权重衰减防过拟合
    warmup_ratio = 0.2  # 延长预热时间
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    emotion_num = 7  # 情绪类别数
    trend_num = 4  # 趋势类别数
    intent_num = 8  # 意图类别数（含新增的"求回应"）


config = Config()

# ====================== 标签映射（确保完整）=====================
emotion2id = {
    "甜蜜": 0, "撒娇": 1, "委屈": 2, "小生气": 3,
    "心动": 4, "思念": 5, "中性": 6
}
trend2id = {"上升": 0, "下降": 1, "平稳": 2, "波动": 3}
intent2id = {
    "求互动": 0, "求关注": 1, "求安慰": 2, "求见面": 3,
    "表达不满": 4, "表达": 5, "撒娇调侃": 6, "求回应": 7
}

label_mappings = {
    "emotion2id": emotion2id,
    "id2emotion": {v: k for k, v in emotion2id.items()},
    "trend2id": trend2id,
    "id2trend": {v: k for k, v in trend2id.items()},
    "intent2id": intent2id,
    "id2intent": {v: k for k, v in intent2id.items()}
}


# ====================== 数据集类（修复文本处理）=====================
class EmotionalDataset(Dataset):
    def __init__(self, data, tokenizer, label_mappings):
        self.data = data
        self.tokenizer = tokenizer
        self.emotion2id = label_mappings["emotion2id"]
        self.trend2id = label_mappings["trend2id"]
        self.intent2id = label_mappings["intent2id"]

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        row = self.data.iloc[idx]
        trigger_event = row["trigger_event"]

        # 稳定解析上下文和当前文本（容错处理）
        if " | 当前文本：" in trigger_event:
            context_part, current_text = trigger_event.split(" | 当前文本：", 1)
            try:
                context = json.loads(context_part.replace("上下文：", ""))
            except:
                context = []  # 解析失败时用空上下文
        else:
            context = []
            current_text = trigger_event  # 格式错误时直接用原文

        # 增强文本格式，突出上下文与当前文本的区别
        text = "[CTX] " + " [SEP] ".join(context) + " [SEP] [CUR] " + current_text

        # 文本编码
        encoding = self.tokenizer(
            text,
            max_length=config.max_len,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
        input_ids = encoding["input_ids"].flatten()
        attention_mask = encoding["attention_mask"].flatten()

        # 标签编码
        emotion_id = torch.tensor(self.emotion2id[row["emotion_label"]], dtype=torch.long)
        trend_id = torch.tensor(self.trend2id[row["emotion_trend"]], dtype=torch.long)
        intent_id = torch.tensor(self.intent2id[row["user_intent"]], dtype=torch.long)
        strength = torch.tensor(row["emotion_strength"], dtype=torch.float32)

        return {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "emotion": emotion_id,
            "trend": trend_id,
            "intent": intent_id,
            "strength": strength
        }


# ====================== 模型定义（增强容量）=====================
class ContextEmotionModel(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.bert = BertModel.from_pretrained(config.bert_path)
        self.hidden_size = self.bert.config.hidden_size
        self.dropout = nn.Dropout(0.3)  # 提高dropout增强泛化

        # 新增共享特征层，提升分类能力
        self.shared_fc = nn.Linear(self.hidden_size, 256)

        # 分类头（基于共享特征）
        self.emotion_classifier = nn.Linear(256, config.emotion_num)
        self.trend_classifier = nn.Linear(256, config.trend_num)
        self.intent_classifier = nn.Linear(256, config.intent_num)

        # 强度回归头（基于共享特征）
        self.strength_regressor = nn.Sequential(
            nn.Linear(256, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, 1)
        )

    def forward(self, input_ids, attention_mask):
        # Bert编码
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        cls_emb = outputs.last_hidden_state[:, 0, :]  # [batch_size, hidden_size]
        cls_emb = self.dropout(cls_emb)

        # 共享特征提取
        shared_feat = self.shared_fc(cls_emb)
        shared_feat = nn.ReLU()(shared_feat)  # 增加非线性表达

        # 分类输出
        emotion_logits = self.emotion_classifier(shared_feat)
        trend_logits = self.trend_classifier(shared_feat)
        intent_logits = self.intent_classifier(shared_feat)

        # 强度回归输出
        strength_pred = self.strength_regressor(shared_feat).squeeze(-1)

        return emotion_logits, trend_logits, intent_logits, strength_pred


# ====================== 训练函数（优化损失和早停）=====================
def train_model(model, train_loader, val_loader, config):
    # 损失函数
    ce_loss = nn.CrossEntropyLoss()
    mse_loss = nn.MSELoss()

    # 优化器（改用PyTorch原生，消除警告）
    optimizer = optim.AdamW(
        model.parameters(),
        lr=config.lr,
        weight_decay=config.weight_decay
    )

    # 学习率调度器
    total_steps = len(train_loader) * config.epochs
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=int(total_steps * config.warmup_ratio),
        num_training_steps=total_steps
    )

    model.to(config.device)
    best_val_emotion_acc = 0.0
    early_stop_count = 0
    early_stop_patience = 3  # 延长早停耐心

    for epoch in range(config.epochs):
        print(f"\n===== Epoch {epoch + 1}/{config.epochs} =====")
        model.train()
        total_loss = 0.0

        for batch_idx, batch in enumerate(train_loader):
            # 数据移到设备
            input_ids = batch["input_ids"].to(config.device)
            attention_mask = batch["attention_mask"].to(config.device)
            emotion = batch["emotion"].to(config.device)
            trend = batch["trend"].to(config.device)
            intent = batch["intent"].to(config.device)
            strength = batch["strength"].to(config.device)

            # 前向传播
            emotion_logits, trend_logits, intent_logits, strength_pred = model(input_ids, attention_mask)

            # 计算损失（优化权重，优先情绪分类）
            loss_emotion = ce_loss(emotion_logits, emotion)
            loss_trend = ce_loss(trend_logits, trend)
            loss_intent = ce_loss(intent_logits, intent)
            loss_strength = mse_loss(strength_pred, strength)

            # 总损失：核心任务权重更高
            total_batch_loss = (
                    2.0 * loss_emotion  # 情绪分类（核心）
                    + 1.0 * loss_trend  # 趋势分类
                    + 1.0 * loss_intent  # 意图分类
                    + 0.5 * loss_strength  # 强度回归（辅助）
            )

            # 反向传播
            optimizer.zero_grad()
            total_batch_loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)  # 梯度裁剪
            optimizer.step()
            scheduler.step()

            total_loss += total_batch_loss.item()

            # 打印进度
            if (batch_idx + 1) % 50 == 0:
                avg_loss = total_loss / (batch_idx + 1)
                print(f"Batch {batch_idx + 1}, Avg Loss: {avg_loss:.4f}")

        # 验证
        val_emotion_acc, val_strength_mse = evaluate_model(model, val_loader, config)
        print(f"Val Emotion Acc: {val_emotion_acc:.4f}, Val Strength MSE: {val_strength_mse:.4f}")

        # 保存最优模型+早停判断
        if val_emotion_acc > best_val_emotion_acc:
            best_val_emotion_acc = val_emotion_acc
            os.makedirs(os.path.dirname(config.save_model_path), exist_ok=True)
            torch.save(model.state_dict(), config.save_model_path)
            print(f"✅ 保存最优模型（Emotion Acc: {best_val_emotion_acc:.4f}）")
            early_stop_count = 0
        else:
            early_stop_count += 1
            print(f"⚠️  早停计数器：{early_stop_count}/{early_stop_patience}")
            if early_stop_count >= early_stop_patience:
                print(f"🛑 连续{early_stop_patience}轮未提升，提前停止训练！")
                break

    print(f"\n训练完成！最优验证情绪准确率：{best_val_emotion_acc:.4f}")


# ====================== 验证函数（保持稳定）=====================
def evaluate_model(model, val_loader, config):
    model.eval()
    emotion_correct = 0
    total = 0
    strength_preds = []
    strength_labels = []

    with torch.no_grad():
        for batch in val_loader:
            input_ids = batch["input_ids"].to(config.device)
            attention_mask = batch["attention_mask"].to(config.device)
            emotion = batch["emotion"].to(config.device)
            strength = batch["strength"].to(config.device)

            emotion_logits, _, _, strength_pred = model(input_ids, attention_mask)

            # 情绪准确率
            emotion_pred = torch.argmax(emotion_logits, dim=1)
            emotion_correct += (emotion_pred == emotion).sum().item()
            total += emotion.size(0)

            # 强度MSE
            strength_preds.extend(strength_pred.cpu().numpy())
            strength_labels.extend(strength.cpu().numpy())

    emotion_acc = emotion_correct / total
    strength_mse = mean_squared_error(strength_labels, strength_preds)
    return emotion_acc, strength_mse


# ====================== 主函数（增加数据检查）=====================
def main():
    # 1. 加载数据并检查分布
    print("📥 加载数据...")
    df = pd.read_csv("emotional_history_train_data.csv")

    # 检查情绪标签分布（确保无极端不平衡）
    print("\n情绪标签分布（占比）：")
    print(df["emotion_label"].value_counts(normalize=True).round(3))

    # 2. 分层拆分训练集和验证集（保持分布一致）
    train_df, val_df = train_test_split(
        df,
        test_size=0.1,
        random_state=42,
        stratify=df["emotion_label"]  # 按情绪标签分层
    )

    # 3. 初始化Tokenizer
    tokenizer = BertTokenizer.from_pretrained(config.bert_path)

    # 4. 创建数据集和DataLoader（关闭多进程，避免Windows下报错）
    train_dataset = EmotionalDataset(train_df, tokenizer, label_mappings)
    val_dataset = EmotionalDataset(val_df, tokenizer, label_mappings)

    train_loader = DataLoader(
        train_dataset,
        batch_size=config.batch_size,
        shuffle=True,
        num_workers=0  # Windows下建议设为0，避免多进程错误
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=config.batch_size,
        shuffle=False,
        num_workers=0
    )

    # 5. 初始化模型
    print("\n🔧 初始化模型...")
    model = ContextEmotionModel(config)

    # 6. 开始训练
    print("🚀 开始训练...")
    train_model(model, train_loader, val_loader, config)


if __name__ == "__main__":
    main()