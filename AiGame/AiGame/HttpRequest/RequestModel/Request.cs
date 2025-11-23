namespace AiGame.HttpRequest.RequestModel
{
    public class Request<T>
    {
        public string Route { get; set; } = null!;
        public RestSharp.Method Method { get; set; }
        public T Body { get; set; }
        public string ContentType { get; set; } = "application/json";
    }
}
