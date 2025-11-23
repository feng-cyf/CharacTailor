using System;
using System.Collections.Generic;

namespace AiGame.Models;

public partial class UserPersonaMapping
{
    public int Id { get; set; }

    public bool IsDefault { get; set; }

    public DateTime CreatedAt { get; set; }

    public string PersonaId { get; set; } = null!;

    public string UserId { get; set; } = null!;

    public virtual Persona Persona { get; set; } = null!;

    public virtual User User { get; set; } = null!;
}
