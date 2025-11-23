using System;
using System.Collections.Generic;

namespace AiGame.Models;

public partial class Session
{
    public string SessionId { get; set; } = null!;

    public string? ConnectionInfo { get; set; }

    public bool? IsActive { get; set; }

    public DateTime CreatedAt { get; set; }

    public DateTime LastActivity { get; set; }

    public string? EmotionalContext { get; set; }

    public string CurrentPersonaId { get; set; } = null!;

    public string UserId { get; set; } = null!;

    public string? SessionName { get; set; }

    public string? ParentSessionId { get; set; }

    public virtual Persona CurrentPersona { get; set; } = null!;

    public virtual ICollection<DialogueHistory> DialogueHistories { get; set; } = new List<DialogueHistory>();

    public virtual ICollection<EmotionalHistory> EmotionalHistories { get; set; } = new List<EmotionalHistory>();

    public virtual ICollection<GridEmotionalHistory> GridEmotionalHistories { get; set; } = new List<GridEmotionalHistory>();

    public virtual User User { get; set; } = null!;
}
