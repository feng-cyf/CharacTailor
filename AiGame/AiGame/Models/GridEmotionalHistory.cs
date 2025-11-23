using System;
using System.Collections.Generic;

namespace AiGame.Models;

public partial class GridEmotionalHistory
{
    public int Id { get; set; }

    public string EmotionLabel { get; set; } = null!;

    public double EmotionStrength { get; set; }

    public double EmotionConfidence { get; set; }

    public string EmotionTrend { get; set; } = null!;

    public double TrendConfidence { get; set; }

    public string UserIntent { get; set; } = null!;

    public double IntentConfidence { get; set; }

    public string? TriggerEvent { get; set; }

    public string Scene { get; set; } = null!;

    public DateTime CreatedAt { get; set; }

    public string SessionId { get; set; } = null!;

    public string UserId { get; set; } = null!;

    public virtual Session Session { get; set; } = null!;

    public virtual User User { get; set; } = null!;
}
