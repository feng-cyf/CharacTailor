using AiGame.Attributes;
using AiGame.Game;
using AiGame.HttpRequest;
using AiGame.HttpRequest.DTO;
using AiGame.HttpRequest.RequestModel;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using System.Net.WebSockets;
using System.Text;
using System.Text.Json;

namespace AiGame.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class GomokuController:Controller
    {
        [HttpGet("/test")]
        public IActionResult test()
        {
            return Ok("1");
        }
        //[WebSocket]
        [HttpGet("ws")]
        public async Task<IActionResult> WebSocketHander()
        {
            var game = new GomokuGame();
            // 定义取消令牌，用于优雅终止循环
            using var cts = CancellationTokenSource.CreateLinkedTokenSource(HttpContext.RequestAborted);
            var token = cts.Token;

            try
            {
                // 1. Token 验证（保持不变）
                var jwtToken = HttpContext.Request.Query["token"].ToString();
                var personaId= HttpContext.Request.Query["persona_id"].ToString();
                //if (!string.IsNullOrEmpty(jwtToken))
                //{
                //    var jwtHelper = new Helper.JwtHelper();
                //    var claims = jwtHelper.ValidateToken(jwtToken);
                //}

                // 2. 接受 WebSocket 连接
                if (!HttpContext.WebSockets.IsWebSocketRequest)
                {
                    return BadRequest("不是 WebSocket 请求");
                }
                using var webSocket = await HttpContext.WebSockets.AcceptWebSocketAsync();
                Console.WriteLine("WebSocket 连接建立成功");

                var buffer = new byte[1024 * 4];
                while (webSocket.State == WebSocketState.Open && !token.IsCancellationRequested)
                {
                    WebSocketReceiveResult result;
                    try
                    {
                        // 3. 接收消息（带取消令牌，支持优雅终止）
                        result = await webSocket.ReceiveAsync(
                            new ArraySegment<byte>(buffer),
                            token
                        );
                    }
                    catch (OperationCanceledException)
                    {
                        // 取消令牌触发（比如页面刷新/关闭），直接退出循环
                        Console.WriteLine("WebSocket 连接被优雅终止（可能是页面刷新/关闭）");
                        break;
                    }

                    // 4. 处理关闭消息
                    if (result.MessageType == WebSocketMessageType.Close)
                    {
                        Console.WriteLine("收到客户端关闭请求");
                        await webSocket.CloseAsync(
                            WebSocketCloseStatus.NormalClosure,
                            "客户端主动关闭",
                            CancellationToken.None
                        );
                        game.ClearBoard();
                        break;
                    }

                    // 5. 过滤空消息
                    if (result.Count == 0)
                    {
                        Console.WriteLine("收到空消息，跳过解析");
                        continue;
                    }

                    // 6. 解析消息（保持之前的安全解析逻辑）
                    var str = Encoding.UTF8.GetString(buffer, 0, result.Count).Trim();
                    if (string.IsNullOrWhiteSpace(str))
                    {
                        Console.WriteLine("收到空白消息，跳过解析");
                        continue;
                    }

                    JsonDocument json;
                    try
                    {
                        json = JsonDocument.Parse(str);
                    }
                    catch (JsonException ex)
                    {
                        Console.WriteLine($"JSON 解析失败：{ex.Message}，原始数据：{str}");
                        var errorMsg = Encoding.UTF8.GetBytes("消息格式错误（非合法 JSON）");
                        await webSocket.SendAsync(new ArraySegment<byte>(errorMsg), WebSocketMessageType.Text, true, CancellationToken.None);
                        continue;
                    }
                    using (json)
                    {
                        // 7. 处理落子和 AI 调用（保持之前的安全逻辑）
                        JsonElement root = json.RootElement;
                        if (!root.TryGetProperty("x", out var xProp) || !root.TryGetProperty("y", out var yProp))
                        {
                            var errorMsg = Encoding.UTF8.GetBytes("消息缺少 x 或 y 字段");
                            await webSocket.SendAsync(new ArraySegment<byte>(errorMsg), WebSocketMessageType.Text, true, CancellationToken.None);
                            continue;
                        }
                        string UserMessage = root.GetProperty("userMessage").GetString() ?? "";
                        int x = xProp.GetInt32();
                        int y = yProp.GetInt32();
                        Console.WriteLine($"Received move: x={x}, y={y}");

                        if (!game.IsValidMove(x, y))
                        {
                            var errorMsg = Encoding.UTF8.GetBytes("该位置已落子或超出棋盘范围");
                            await webSocket.SendAsync(new ArraySegment<byte>(errorMsg), WebSocketMessageType.Text, true, CancellationToken.None);
                            continue;
                        }

                        var user=game.MakeMove(x, y, 1);
                        if (user!= 0)
                        {
                            byte[] msg = Encoding.UTF8.GetBytes($"玩家{user}获胜");
                            await webSocket.SendAsync(new ArraySegment<byte>(msg, 0, msg.Length), WebSocketMessageType.Text, true, CancellationToken.None);
                            continue;
                        }

                        // AI 调用逻辑
                        GomoluRequest gomoluRequest = new GomoluRequest();
                        Request<GomokuDTO> request = new Request<GomokuDTO>
                        {
                            Method = RestSharp.Method.Post,
                            Route = "game/gomoku",
                            Body = new GomokuDTO
                            {
                                Board = game.GetBoardState().Board,
                                PersonaId = personaId,
                                UserMessage = UserMessage
                            },
                        };
                        var response = gomoluRequest.GomoKuRequest(request);
                        var data = response.data;

                        if (!data.TryGetProperty("best_x", out var bestXProp) || !data.TryGetProperty("best_y", out var bestYProp))
                        {
                            var errorMsg = Encoding.UTF8.GetBytes("AI 返回数据缺少 best_x 或 best_y 字段");
                            await webSocket.SendAsync(new ArraySegment<byte>(errorMsg), WebSocketMessageType.Text, true, CancellationToken.None);
                            continue;
                        }

                        int bestX = bestXProp.GetInt32();
                        int bestY = bestYProp.GetInt32();
                        string chat = data.GetProperty("chat").GetString() ?? "";
                        int winner = game.MakeMove(bestX, bestY, 2);
                        if (winner != 0)
                        {
                            byte[] msg = Encoding.UTF8.GetBytes($"玩家{winner}获胜");
                            await webSocket.SendAsync(new ArraySegment<byte>(msg, 0, msg.Length), WebSocketMessageType.Text, true, CancellationToken.None);
                        }
                        else
                        {
                            Coordinates coordinates = new Coordinates
                            {
                                BestX = bestX,
                                BestY = bestY,
                                chat=chat
                            };
                            byte[] xyBytes = Encoding.UTF8.GetBytes(System.Text.Json.JsonSerializer.Serialize(coordinates));
                            await webSocket.SendAsync(new ArraySegment<byte>(xyBytes, 0, xyBytes.Length), WebSocketMessageType.Text, true, CancellationToken.None);
                        }
                    }
                }

                Console.WriteLine("WebSocket 连接已正常关闭");
            }
            catch (Exception ex)
            {
                // 8. 一场捕获所有异常，避免服务崩溃
                Console.WriteLine($"WebSocket 连接异常：{ex.Message}");
                // 可选：记录详细日志（比如用日志框架）
                // _logger.LogError(ex, "WebSocket 处理异常");
            }
            return new EmptyResult();
        }
        public class Coordinates
        {
            public int BestX { get; set; }
            public int BestY { get; set; }
            public string chat { get; set; }
        }
    }
}