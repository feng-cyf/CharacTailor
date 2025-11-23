# CharacTailor - 智能AI交互系统

## 1. 项目作用
**为AI角色扮演和智能游戏提供完整的后端支持系统，实现个性化对话和实时游戏交互。**

## 2. 核心功能列表
- **人设自定义与管理系统** - 支持创建、编辑、管理个性化AI角色
- **智能对话引擎** - 基于角色设定的个性化AI对话
- **情感交互分析** - 实时情感识别和趋势预测
- **多AI模型路由** - 支持本地Ollama和云端Ark模型切换
- **文件上传** - 支持图片和视频以及音频上传
- **实时游戏AI决策** - 五子棋等游戏的智能对战
- **跨语言服务集成** - Python与C#服务的无缝协作

## 3. 技术栈
- **后端框架**: Python FastAPI、C# ASP.NET Core
- **数据库**: MySQL、Redis
- **ORM**: Tortoise-ORM、Entity Framework Core
- **通信协议**: WebSocket、HTTP REST API
- **AI模型**: Ollama（本地）、火山引擎Ark（云端）
- **认证授权**: JWT Token
- **部署工具**: Docker、uvicorn、dotnet

## 4. 系统架构截图

1. **主界面截图** - 展示系统整体架构和服务状态
<img width="2559" height="1418" alt="image" src="https://github.com/user-attachments/assets/ebf8f15f-3737-4474-9e88-f8bba44b53c0" />

2. **人设管理界面** - 角色创建和配置界面
<img width="2557" height="1475" alt="image" src="https://github.com/user-attachments/assets/a62d0bf6-0225-4317-8d47-df4b4d3cc17f" />

3. **实时对话界面** - AI交互和游戏对战界面
<img width="2558" height="1455" alt="image" src="https://github.com/user-attachments/assets/8f27c8d7-bc49-49c2-9357-c2b267eb0890" />

## 5. 系统文件架构
```
GridFriend/
├── AI/                          # Python FastAPI AI服
务端
│   ├── api/                    # API接口层
│   │   ├── AIChatApi.py        # AI对话核心API
│   │   ├── PersonApi.py        # 人设管理API
│   │   └── Game/               # 游戏相关API
│   ├── core/                   # 核心业务逻辑
│   │   ├── EmotionInteractionAnalyzer.py  # 情感分析
│   │   ├── SessionProcesser.py  # 会话管理
│   │   └── RedisProcess.py     # 缓存管理
│   ├── models/                 # 数据模型
│   │   └── model.py           # ORM模型定义
│   ├── route/                  # 路由配置
│   └── main.py                # 应用入口
└── AiGame/                     # C# ASP.NET Core游戏
服务端
    ├── Controllers/            # API控制器
    │   ├── GomokuController.cs # 五子棋控制器
    │   └── SceneController.cs  # 场景控制器
    ├── HttpRequest/           # HTTP请求处理
    │   └── GomoluRequest.cs   # Python服务调用
    ├── Game/                  # 游戏逻辑
    └── Program.cs             # 应用入口
```

## 6. 项目现状
> 由于项目涉及云端AI服务密钥、数据库配置和内部部署环境，仓库不包含完整的生产环境配置文件，主要用于展示后端架构设计和核心业务逻辑实现。

---
