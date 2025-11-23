using System;
using System.Collections.Generic;

namespace AiGame.Models;

public partial class Aerich
{
    public int Id { get; set; }

    public string Version { get; set; } = null!;

    public string App { get; set; } = null!;

    public string Content { get; set; } = null!;
}
