using System;
using System.Collections.Generic;

namespace AiGame.Models;

public partial class Scene
{
    public int Id { get; set; }

    public string Name { get; set; } = null!;

    public string? Description { get; set; }

    public DateTime CreatedAt { get; set; }

    public string UserId { get; set; } = null!;

    public virtual User User { get; set; } = null!;
}
