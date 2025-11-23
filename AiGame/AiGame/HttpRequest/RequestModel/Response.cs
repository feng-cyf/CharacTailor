namespace AiGame.HttpRequest.RequestModel
{
    public class Response<T>
    {
        public int statusCode { get; set; }
        public string message { get; set; } = null!;
        public T data { get; set; }
    }
}
