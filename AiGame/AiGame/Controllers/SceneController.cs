using AiGame.Context;
using AiGame.DataBaseDTO;
using AiGame.HttpRequest;
using AiGame.HttpRequest.DTO;
using AiGame.HttpRequest.RequestModel;
using AiGame.Models;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using System.Net.WebSockets;
using System.Security.Claims;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;

namespace AiGame.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class SceneController : Controller
    {
        private readonly AIGameContext _context;
        public SceneController(AIGameContext context)
        {
            _context = context;
        }
        [HttpGet("status")]
        public IActionResult GetStatus()
        {
            return Ok(new { status = "SceneController is running." });
        }
        [HttpGet("ws")]
        public async Task<IActionResult> WebSocketHandler()
        {
            Console.WriteLine(1);
            var token=HttpContext.Request.Query["token"].ToString();
            var sceneId=HttpContext.Request.Query["sceneId"].ToString();
            CancellationTokenSource cts = new CancellationTokenSource();
            var tokenCancel = cts.Token;
            if (!HttpContext.WebSockets.IsWebSocketRequest)
            {
                return BadRequest("Not a WebSocket request");
            }
            if (string.IsNullOrEmpty(token) || string.IsNullOrEmpty(sceneId))
            {
                return BadRequest("Missing token or sceneId");
            }
            using var webSocket = await HttpContext.WebSockets.AcceptWebSocketAsync();
            Console.WriteLine("Scene连接成功");
            var buffer = new byte[1024 * 4];
            while (webSocket.State == WebSocketState.Open && !tokenCancel.IsCancellationRequested)
            {
                WebSocketReceiveResult result;
                try
                {
                    result = await webSocket.ReceiveAsync(
                        new ArraySegment<byte>(buffer),
                        tokenCancel
                    );
                }
                catch (OperationCanceledException)
                {
                    break;
                }
                if (result.MessageType == WebSocketMessageType.Close)
                {
                    await webSocket.CloseAsync(WebSocketCloseStatus.NormalClosure, "Closing", CancellationToken.None);
                    Console.WriteLine("WebSocket connection closed by client");
                }
                if (result.Count == 0)
                {
                    continue;
                }
                var json = Encoding.UTF8.GetString(buffer, 0, result.Count);
                JsonDocument jsonDocument;
                try
                {
                    jsonDocument = JsonDocument.Parse(json);
                }
                catch (System.Text.Json.JsonException)
                {
                    Console.WriteLine("Invalid JSON received");
                    continue;
                }
                JsonElement root = jsonDocument.RootElement;
                var usrMessage = root.GetProperty("userMessage").GetString();
                var message = System.Text.Encoding.UTF8.GetString(buffer, 0, result.Count);
                Console.WriteLine($"Received message: {message}");
                var scene= await _context.Scenes.FindAsync(int.Parse(sceneId));
                Request<SceneDTO> sceneRequest = new Request<SceneDTO>
                {
                    Route = "game/scene",
                    Method = RestSharp.Method.Post,
                    Body = new SceneDTO
                    {
                        SceneId = int.Parse(sceneId),
                        UserMessage = usrMessage!,
                        Token = token,
                        Name=scene!.Name,
                        Description=scene!.Description
                    }
                };
                SceneRequest request = new SceneRequest();
                var responses = await request.SendSceneRequest(sceneRequest);

                // 直接把后端原始字符串透传给前端
                var raw = responses.data ?? string.Empty;
                var responseBytes = Encoding.UTF8.GetBytes(raw);
                await webSocket.SendAsync(new ArraySegment<byte>(responseBytes), WebSocketMessageType.Text, true, CancellationToken.None);
            }
            return new EmptyResult();
        }
        [HttpGet("GetScene")]
        [Authorize]
        public async Task<IActionResult> GetScene()
        {
            var UserId = User.FindFirstValue("user_id");
            if (string.IsNullOrEmpty(UserId))
            {
                return Unauthorized("User ID not found in token.");
            }
            var Scenes = await _context.Scenes
                .Where(s => s.UserId == UserId.ToString())
                .ToListAsync();
            return Ok(Scenes);
        }

        [HttpPost("createScene")]
        [Authorize]
        async public Task<IActionResult> CreateScene(CreatSceneDTO creatScene)
        {
            var userId = User.FindFirstValue("user_id");
            if (string.IsNullOrEmpty(userId))
            {
                return Unauthorized("User ID not found in token.");
            }
            await _context.Scenes.AddAsync(new Scene
            {
                Name=creatScene.SceneName,
                Description=creatScene.SceneDescription,
                UserId=userId,
            });
            await _context.SaveChangesAsync();
            return Ok("Scene created successfully.");
        }
    }
}
