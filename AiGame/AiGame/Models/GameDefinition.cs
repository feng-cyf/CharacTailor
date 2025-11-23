using System;
using System.Collections.Generic;

namespace AiGame.Models;

public partial class GameDefinition
{
    public int Id { get; set; }

    public string Name { get; set; } = null!;

    public int TypeIdId { get; set; }

    public virtual ICollection<GameSession> GameSessions { get; set; } = new List<GameSession>();

    public virtual GameType TypeId { get; set; } = null!;
}
