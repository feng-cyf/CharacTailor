"""
日志模块
用于配置和管理多模块日志功能，每个模块单独一个日志文件，仅写入文件，不打印到控制台
"""

import logging
import logging.handlers
import os
from datetime import datetime

# 创建logs目录（如果不存在）
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'log')
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def setup_logger(name, log_file, level=logging.DEBUG):
    """
    为每个模块创建单独的日志器，仅写入日志文件，不输出到控制台

    Args:
        name (str): 日志器名称
        log_file (str): 日志文件路径
        level (int): 日志级别，默认INFO

    Returns:
        logging.Logger: 配置好的日志器
    """
    # 创建日志器
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False  # 关键：不传递给父级日志器，避免父级控制台输出

    # 避免重复添加处理器
    if logger.handlers:
        return logger

    # 创建格式器，包含详细信息
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 创建文件处理器
    log_file_path = os.path.join(LOG_DIR, log_file)
    file_handler = logging.handlers.TimedRotatingFileHandler(
        log_file_path, when='midnight', interval=1, backupCount=7,
        encoding='utf-8', delay=False
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

# 为不同模块创建单独的日志器
# 情感分析器日志
emotion_analyzer_logger = setup_logger('EmotionAnalyzerRefactored', 'emotion_analyzer.log', logging.DEBUG)

# 对话历史处理日志
dialog_history_logger = setup_logger('DialogHistory', 'dialog_history.log')

# 情感历史处理日志
emotional_history_logger = setup_logger('EmotionalHistory', 'emotional_history.log')

# 聊天API日志
chat_api_logger = setup_logger('ChatAPI', 'chat_api.log')

# 保持向后兼容性的别名
emotion_logger = emotion_analyzer_logger

if __name__ == "__main__":
    # 测试：各模块日志分别写入对应文件
    emotion_analyzer_logger.info("情感分析器日志初始化完成")
    dialog_history_logger.info("对话历史处理器日志初始化完成")
    emotional_history_logger.info("情感历史处理器日志初始化完成")
    chat_api_logger.info("聊天API日志初始化完成")