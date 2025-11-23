using System.Text.Json.Serialization;

namespace AiGame.HttpRequest.DTO
{
    public class SceneDTO
    {
        public int SceneId { get; set; }
        public string UserMessage { get; set; }
        public string Name { get; set; }
        public string Description { get; set; }
        [JsonIgnore]
        public string Token { get; set; }
    }
}
