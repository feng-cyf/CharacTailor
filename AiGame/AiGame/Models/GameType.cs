using System;
using System.Collections.Generic;

namespace AiGame.Models;

public partial class GameType
{
    public int Id { get; set; }

    public string Name { get; set; } = null!;

    public string? Description { get; set; }

    public virtual ICollection<GameDefinition> GameDefinitions { get; set; } = new List<GameDefinition>();
}
