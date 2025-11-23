using System;
using System.Collections.Generic;

namespace AiGame.Models;

public partial class DialogueHistory
{
    public string DialogueId { get; set; } = null!;

    public string UserMessage { get; set; } = null!;

    public string BotResponse { get; set; } = null!;

    public double EmotionalFeedback { get; set; }

    public DateTime CreatedAt { get; set; }

    public string PersonaId { get; set; } = null!;

    public string SessionId { get; set; } = null!;

    public string UserId { get; set; } = null!;

    public string EmotionType { get; set; } = null!;

    public double Confidence { get; set; }

    public string BotResponseType { get; set; } = null!;

    public string UserMessageType { get; set; } = null!;

    public string? BotFileUrl { get; set; }

    public string? UserFileUrl { get; set; }

    public string? BotAudioUrl { get; set; }

    public virtual Persona Persona { get; set; } = null!;

    public virtual Session Session { get; set; } = null!;

    public virtual User User { get; set; } = null!;
}
