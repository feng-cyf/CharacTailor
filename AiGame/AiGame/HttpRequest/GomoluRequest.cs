using AiGame.HttpRequest.DTO;
using AiGame.HttpRequest.RequestModel;
using RestSharp;
using System.Text.Encodings.Web;
using System.Text.Json;

namespace AiGame.HttpRequest
{
    public class GomoluRequest
    {
        private string BaseUrl= "http://127.0.0.1:8000";
        public Response<JsonElement> GomoKuRequest(Request<GomokuDTO> request)
        {
            var req= new RestRequest(request.Route,request.Method);
            var jsonOptions = new JsonSerializerOptions
            {
                PropertyNamingPolicy = JsonNamingPolicy.CamelCase, // 核心配置：PascalCase → camelCase
                Encoder = JavaScriptEncoder.UnsafeRelaxedJsonEscaping // 可选：避免特殊字符转义（如中文）
            };
            var json = JsonSerializer.Serialize(request.Body,jsonOptions);
            req.AddJsonBody(json);
            var client= new RestClient(BaseUrl);
            var responseTask = client.ExecuteAsync(req);
            responseTask.Wait();
            var response = responseTask.Result;
            if (response.IsSuccessful)
            {
                var res = JsonSerializer.Deserialize<Response<JsonElement>>(response.Content);
                return res;
            }
            else
            {
                return new Response<JsonElement>
                {
                    statusCode = 500,
                    message = "Request failed",
                    data = new JsonElement()
                };
            }
        }
    }
}
