# CharacTailor

## 项目概述

CharacTailor是一个基于**多语言架构**的智能AI交互后端系统，包含Python FastAPI AI服务端和C# ASP.NET Core游戏服务端。本项目展示了我在**后端架构设计**、**跨语言系统集成**和**微服务通信**方面的专业技能。

## 声明
由于项目涉及云端密钥和服务器配置，仓库中未包含完整运行所需的配置文件。当前仓库主要用于展示架构设计与核心代码。

## 技术架构

### 后端技术栈
- **Python FastAPI** - 高性能异步Web框架，AI服务核心
- **C# ASP.NET Core** - 企业级Web框架，游戏服务端
- **MySQL + Redis** - 数据存储与缓存
- **Tortoise-ORM** - 异步ORM框架
- **WebSocket + HTTP API** - 实时通信与数据交换

### 系统架构图
```
[前端应用] 
    ↓ (WebSocket)
[C#游戏服务端] (端口: 5000)
    ↓ (HTTP REST API)  
[Python AI服务端] (端口: 8000)
    ↓ (数据库操作)
[MySQL + Redis]
```

## 核心功能模块

### Python AI服务端 (`AI/`)
```
AI/
├── api/                 # API接口层
│   ├── AIChatApi.py     # AI对话核心API
│   ├── Game/Api/        # 游戏AI决策API
│   ├── UserApi.py       # 用户管理API
│   └── fileApi.py       # 文件上传API
├── core/                # 核心业务逻辑
│   ├── EmotionInteractionAnalyzer.py  # 情感交互分析
│   ├── SessionProcesser.py            # 会话处理
│   └── RedisProcess.py  # Redis缓存管理
├── database/            # 数据访问层
│   ├── mysql.py         # MySQL配置
│   └── Redis.py         # Redis客户端
├── models/              # 数据模型
│   └── model.py         # ORM模型定义
├── route/               # 路由配置
│   ├── AIChatRoute.py   # AI对话路由
│   ├── GameRoute/       # 游戏路由
│   └── UserRoute.py     # 用户路由
└── main.py              # 应用入口
```

### C#游戏服务端 (`AiGame/`)
```
AiGame/
├── Controllers/        # API控制器
│   ├── GomokuController.cs    # 五子棋控制器(WebSocket)
│   └── SceneController.cs     # 场景控制器
├── HttpRequest/       # HTTP请求处理
│   └── GomoluRequest.cs      # Python服务调用
├── Game/              # 游戏逻辑
│   └── GomokuGame.cs         # 五子棋游戏逻辑
└── Models/            # 数据模型
    └── GomokuDTO.cs          # 游戏数据传输对象
```

## 技术实现亮点

### 1. 跨语言HTTP API集成
```csharp
// C#端调用Python AI服务
public Response<JsonElement> GomoKuRequest(Request<GomokuDTO> request)
{
    var client = new RestClient("http://127.0.0.1:8000");
    var req = new RestRequest("game/gomoku", Method.Post);
    
    // 构建游戏状态数据
    var requestData = new {
        board = gameBoard,
        personaId = characterId,
        userMessage = playerInput
    };
    
    req.AddJsonBody(JsonSerializer.Serialize(requestData));
    var response = client.Execute(req);
    return JsonSerializer.Deserialize<Response<JsonElement>>(response.Content);
}
```

### 2. Python AI决策引擎
```python
async def gomoku_api(request):
    # 获取角色信息
    persona = await Persona.get_or_none(persona_id=request.personaId)
    
    # 构建AI提示词系统
    system_prompt = f"""
    你是{persona.persona_name}，五子棋高手。
    当前棋盘: {request.board}
    请分析并给出最佳落子决策。
    """
    
    # 调用AI模型
    ai = DouBaoLite()
    result = ai.get_message(system_message=system_prompt, user_message=request.userMessage)
    
    return {
        "best_x": result["best_x"],
        "best_y": result["best_y"], 
        "chat": result["chat"]
    }
```

### 3. WebSocket实时通信
```csharp
// C# WebSocket游戏会话管理
[HttpGet("ws")]
public async Task<IActionResult> WebSocketHander()
{
    if (!HttpContext.WebSockets.IsWebSocketRequest)
        return BadRequest("不是 WebSocket 请求");
        
    using var webSocket = await HttpContext.WebSockets.AcceptWebSocketAsync();
    
    // 实时游戏状态同步
    while (webSocket.State == WebSocketState.Open)
    {
        var result = await webSocket.ReceiveAsync(buffer, CancellationToken.None);
        // 处理玩家落子，调用Python AI决策
        await ProcessPlayerMove(webSocket, result);
    }
}
```

## 数据流设计

### 游戏决策数据流
```
玩家落子 → C#服务端验证 → HTTP调用Python AI → AI分析决策 → 返回游戏状态
    ↓           ↓              ↓               ↓            ↓
WebSocket   游戏逻辑处理   智能分析生成   决策结果解析   状态同步推送
```

### API通信协议
**请求格式:**
```json
{
    "board": [[0,1,2],[1,2,0],[0,0,0]],
    "personaId": "character_001",
    "userMessage": "这步棋怎么样？"
}
```

**响应格式:**
```json
{
    "best_x": 7,
    "best_y": 7,
    "chat": "这个位置很不错！"
}
```

## 性能优化策略

### 1. 异步处理架构
- **全链路异步IO**: Python async/await + C# async/await
- **数据库连接池**: MySQL连接复用管理
- **Redis缓存**: 会话状态和热点数据缓存

### 2. 连接管理
- **HTTP客户端池**: 跨服务调用连接复用
- **WebSocket连接池**: 实时连接状态管理
- **连接超时控制**: 防止资源泄漏

### 3. 内存优化
- **流式处理**: 大文件上传下载
- **对象池**: 频繁创建对象的复用
- **垃圾回收优化**: 内存使用监控

## 安全设计

### 1. 认证授权
- **JWT令牌**: 用户身份验证
- **角色权限**: 基于角色的访问控制
- **Token刷新**: 安全的会话管理

### 2. 输入验证
- **数据校验**: 请求参数完整性检查
- **SQL注入防护**: ORM参数化查询
- **文件安全**: 上传文件类型和大小限制

### 3. 通信安全
- **HTTPS支持**: 生产环境加密传输
- **CORS配置**: 跨域访问控制
- **请求限流**: API调用频率限制

## 部署架构

### 开发环境
```bash
# Python AI服务 (端口8000)
cd AI && python main.py

# C#游戏服务 (端口5000)  
cd AiGame && dotnet run

# 前端应用 (端口5173)
cd AI/frontend && npm run dev
```

### 生产环境建议
```yaml
# Docker多服务部署
version: '3.8'
services:
  python-ai:
    image: gridfriend-ai:latest
    ports: ["8000:8000"]
    environment:
      - DB_HOST=mysql
      - REDIS_HOST=redis

  csharp-game:
    image: gridfriend-game:latest  
    ports: ["5000:5000"]
    depends_on: 
      - python-ai
      - mysql
      - redis
```

## 项目价值体现

### 技术能力展示
- **微服务架构**: 清晰的服务边界和职责分离
- **跨语言集成**: Python与C#的无缝协作能力
- **实时通信**: WebSocket与HTTP API混合通信
- **数据库设计**: 多数据源的高效管理

### 工程实践能力
- **API设计**: RESTful接口规范设计
- **错误处理**: 跨服务异常传递机制
- **性能监控**: 服务健康检查和指标收集
- **代码质量**: 类型注解和单元测试

## 技术特色总结

1. **创新的双服务架构**: 游戏逻辑与AI决策分离，提高系统可维护性
2. **智能决策引擎**: 基于角色设定的个性化AI交互
3. **高性能实时通信**: WebSocket确保游戏状态实时同步
4. **企业级安全**: 完整的认证授权和安全防护机制

---
*本项目展示了现代后端开发中微服务架构、跨语言集成和实时通信技术的完整实践*
