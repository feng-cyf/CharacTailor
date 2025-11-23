using Microsoft.AspNetCore.Mvc.ActionConstraints;

namespace AiGame.Attributes
{
    [AttributeUsage(AttributeTargets.Method, AllowMultiple = false)]
    public class WebSocketAttribute : Attribute, IActionConstraint
    {
        public int Order =>0;

        public bool Accept(ActionConstraintContext context)
        {
            return context.RouteContext.HttpContext.WebSockets.IsWebSocketRequest;
        }
    }
}
