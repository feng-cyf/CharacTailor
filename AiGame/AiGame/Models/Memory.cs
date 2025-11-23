using System;
using System.Collections.Generic;

namespace AiGame.Models;

public partial class Memory
{
    public int Id { get; set; }

    public string MemoryType { get; set; } = null!;

    public string Content { get; set; } = null!;

    public byte[]? EmbeddingVector { get; set; }

    public double ImportanceScore { get; set; }

    public double EmotionalWeight { get; set; }

    public DateTime CreatedAt { get; set; }

    public DateTime LastAccessed { get; set; }

    public int AccessCount { get; set; }

    public string? Metadata { get; set; }

    public string UserId { get; set; } = null!;

    public virtual User User { get; set; } = null!;
}
