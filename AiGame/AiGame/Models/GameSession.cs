using System;
using System.Collections.Generic;

namespace AiGame.Models;

public partial class GameSession
{
    public int Id { get; set; }

    public DateTime StartTime { get; set; }

    public DateTime? EndTime { get; set; }

    public string? Winner { get; set; }

    public string? Loser { get; set; }

    public string Status { get; set; } = null!;

    public string PersonaId { get; set; } = null!;

    public string UserId { get; set; } = null!;

    public int GameIdId { get; set; }

    public string? GameConfig { get; set; }

    public int Score { get; set; }

    public virtual GameDefinition GameId { get; set; } = null!;

    public virtual Persona Persona { get; set; } = null!;

    public virtual User User { get; set; } = null!;
}
