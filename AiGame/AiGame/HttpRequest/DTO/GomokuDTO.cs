namespace AiGame.HttpRequest.DTO
{
    public class GomokuDTO
    {
        public int X { get; set; }
        public int Y { get; set; }
        public int[][] Board { get; set; } 
        public string PersonaId { get; set; }
        public string UserMessage { get; set; }
    }
}