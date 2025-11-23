using System;
using System.Collections.Generic;

namespace AiGame.Models;

public partial class Persona
{
    public string PersonaId { get; set; } = null!;

    public string PersonaName { get; set; } = null!;

    public string? Description { get; set; }

    public string Tone { get; set; } = null!;

    public string? SpeechCharacteristics { get; set; }

    public string FunctionalScene { get; set; } = null!;

    public string? EmotionalBias { get; set; }

    public DateTime CreatedAt { get; set; }

    public bool? IsActive { get; set; }

    public string DeployType { get; set; } = null!;

    public virtual ICollection<DialogueHistory> DialogueHistories { get; set; } = new List<DialogueHistory>();

    public virtual ICollection<GameSession> GameSessions { get; set; } = new List<GameSession>();

    public virtual ICollection<Session> Sessions { get; set; } = new List<Session>();

    public virtual ICollection<UserPersonaMapping> UserPersonaMappings { get; set; } = new List<UserPersonaMapping>();
}
