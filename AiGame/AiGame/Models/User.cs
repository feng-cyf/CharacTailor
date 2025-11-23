using System;
using System.Collections.Generic;

namespace AiGame.Models;

public partial class User
{
    public string UserId { get; set; } = null!;

    public string Username { get; set; } = null!;

    public DateTime CreatedAt { get; set; }

    public DateTime? LastLogin { get; set; }

    public int TotalInteractionCount { get; set; }

    public int RelationshipLevel { get; set; }

    public string Pwd { get; set; } = null!;

    public virtual ICollection<DialogueHistory> DialogueHistories { get; set; } = new List<DialogueHistory>();

    public virtual ICollection<EmotionalHistory> EmotionalHistories { get; set; } = new List<EmotionalHistory>();

    public virtual ICollection<GameSession> GameSessions { get; set; } = new List<GameSession>();

    public virtual ICollection<GridEmotionalHistory> GridEmotionalHistories { get; set; } = new List<GridEmotionalHistory>();

    public virtual ICollection<Memory> Memories { get; set; } = new List<Memory>();

    public virtual ICollection<Scene> Scenes { get; set; } = new List<Scene>();

    public virtual ICollection<Session> Sessions { get; set; } = new List<Session>();

    public virtual ICollection<UserPersonaMapping> UserPersonaMappings { get; set; } = new List<UserPersonaMapping>();
}
