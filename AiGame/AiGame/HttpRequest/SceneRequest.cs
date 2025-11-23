using AiGame.HttpRequest.DTO;
using AiGame.HttpRequest.RequestModel;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using RestSharp;
using System.Text;

namespace AiGame.HttpRequest
{
    public class SceneRequest
    {
        private readonly string _baseUrl = "http://127.0.0.1:8000";

        private readonly JsonSerializerSettings _jsonSettings = new JsonSerializerSettings
        {
            ContractResolver = new Newtonsoft.Json.Serialization.CamelCasePropertyNamesContractResolver(),
            Formatting = Formatting.None,
            NullValueHandling = NullValueHandling.Ignore
        };

        // 统一返回原始字符串（优先按 Response<string> 反序列化，失败则透传原文）
        public async Task<Response<string>> SendSceneRequest(Request<SceneDTO> request)
        {
            var req = new RestRequest(request.Route, request.Method);
            req.AddHeader("Authorization", $"Bearer {request.Body.Token}");

            var jsonBody = JsonConvert.SerializeObject(request.Body, _jsonSettings);
            req.AddStringBody(jsonBody, DataFormat.Json);

            var client = new RestClient(_baseUrl);
            var response = await client.ExecuteAsync(req);

            if (response.IsSuccessful)
            {
                if (!string.IsNullOrWhiteSpace(response.Content))
                {
                    try
                    {
                        var parsed = JsonConvert.DeserializeObject<Response<string>>(response.Content);
                        if (parsed != null)
                        {
                            return parsed;
                        }
                    }
                    catch (JsonException)
                    {
                    }

                    // 兜底：后端返回合法 JSON 但不是 Response<string>，或反序列化失败 -> 透传原文
                    return new Response<string>
                    {
                        statusCode = (int)response.StatusCode,
                        message = "ok",
                        data = response.Content
                    };
                }

                // 空内容时返回空字符串
                return new Response<string>
                {
                    statusCode = (int)response.StatusCode,
                    message = "ok",
                    data = string.Empty
                };
            }

            return new Response<string>
            {
                statusCode = (int)response.StatusCode,
                message = response.ErrorMessage ?? "Request failed",
                data = response.Content ?? string.Empty
            };
        }
    }
}