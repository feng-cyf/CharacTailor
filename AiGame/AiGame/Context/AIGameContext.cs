using System;
using System.Collections.Generic;
using AiGame.Models;
using Microsoft.EntityFrameworkCore;
using Pomelo.EntityFrameworkCore.MySql.Scaffolding.Internal;

namespace AiGame.Context;

public partial class AIGameContext : DbContext
{
    public AIGameContext()
    {
    }

    public AIGameContext(DbContextOptions<AIGameContext> options)
        : base(options)
    {
    }

    public virtual DbSet<Aerich> Aeriches { get; set; }

    public virtual DbSet<DialogueHistory> DialogueHistories { get; set; }

    public virtual DbSet<Efmigrationshistory> Efmigrationshistories { get; set; }

    public virtual DbSet<EmotionalHistory> EmotionalHistories { get; set; }

    public virtual DbSet<GameDefinition> GameDefinitions { get; set; }

    public virtual DbSet<GameSession> GameSessions { get; set; }

    public virtual DbSet<GameType> GameTypes { get; set; }

    public virtual DbSet<GridEmotionalHistory> GridEmotionalHistories { get; set; }

    public virtual DbSet<Memory> Memories { get; set; }

    public virtual DbSet<Persona> Personas { get; set; }

    public virtual DbSet<Scene> Scenes { get; set; }

    public virtual DbSet<Session> Sessions { get; set; }

    public virtual DbSet<User> Users { get; set; }

    public virtual DbSet<UserPersonaMapping> UserPersonaMappings { get; set; }

    protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
        => optionsBuilder.UseMySql("name=Mysql", Microsoft.EntityFrameworkCore.ServerVersion.Parse("8.0.42-mysql"));

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder
            .UseCollation("utf8mb4_0900_ai_ci")
            .HasCharSet("utf8mb4");

        modelBuilder.Entity<Aerich>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("PRIMARY");

            entity.ToTable("aerich");

            entity.Property(e => e.Id).HasColumnName("id");
            entity.Property(e => e.App)
                .HasMaxLength(100)
                .HasColumnName("app");
            entity.Property(e => e.Content)
                .HasColumnType("json")
                .HasColumnName("content");
            entity.Property(e => e.Version)
                .HasMaxLength(255)
                .HasColumnName("version");
        });

        modelBuilder.Entity<DialogueHistory>(entity =>
        {
            entity.HasKey(e => e.DialogueId).HasName("PRIMARY");

            entity.ToTable("dialogue_history");

            entity.HasIndex(e => e.PersonaId, "idx_dialogue_hi_persona_8af913");

            entity.HasIndex(e => new { e.UserId, e.SessionId }, "idx_dialogue_hi_user_id_a64a2d");

            entity.HasIndex(e => new { e.SessionId, e.BotResponse }, "sessions_botResponse").HasAnnotation("MySql:IndexPrefixLength", new[] { 0, 50 });

            entity.Property(e => e.DialogueId)
                .HasMaxLength(100)
                .HasColumnName("dialogue_id");
            entity.Property(e => e.BotAudioUrl)
                .HasMaxLength(100)
                .HasColumnName("bot_audio_url");
            entity.Property(e => e.BotFileUrl)
                .HasMaxLength(100)
                .HasColumnName("bot_file_url");
            entity.Property(e => e.BotResponse)
                .HasColumnType("longtext")
                .HasColumnName("bot_response");
            entity.Property(e => e.BotResponseType)
                .HasMaxLength(10)
                .HasDefaultValueSql("'text'")
                .HasColumnName("bot_response_type");
            entity.Property(e => e.Confidence).HasColumnName("confidence");
            entity.Property(e => e.CreatedAt)
                .HasMaxLength(6)
                .HasDefaultValueSql("CURRENT_TIMESTAMP(6)")
                .HasColumnName("created_at");
            entity.Property(e => e.EmotionType)
                .HasMaxLength(10)
                .HasColumnName("emotion_type");
            entity.Property(e => e.EmotionalFeedback)
                .HasDefaultValueSql("'0.5'")
                .HasColumnName("emotional_feedback");
            entity.Property(e => e.PersonaId)
                .HasMaxLength(50)
                .HasColumnName("persona_id");
            entity.Property(e => e.SessionId)
                .HasMaxLength(100)
                .HasColumnName("session_id");
            entity.Property(e => e.UserFileUrl)
                .HasMaxLength(100)
                .HasColumnName("user_file_url");
            entity.Property(e => e.UserId)
                .HasMaxLength(50)
                .HasColumnName("user_id");
            entity.Property(e => e.UserMessage).HasColumnName("user_message");
            entity.Property(e => e.UserMessageType)
                .HasMaxLength(10)
                .HasDefaultValueSql("'text'")
                .HasColumnName("user_message_type");

            entity.HasOne(d => d.Persona).WithMany(p => p.DialogueHistories)
                .HasForeignKey(d => d.PersonaId)
                .OnDelete(DeleteBehavior.ClientSetNull)
                .HasConstraintName("fk_dialogue_personas_5f7b6b54");

            entity.HasOne(d => d.Session).WithMany(p => p.DialogueHistories)
                .HasForeignKey(d => d.SessionId)
                .HasConstraintName("fk_dialogue_sessions_279e846f");

            entity.HasOne(d => d.User).WithMany(p => p.DialogueHistories)
                .HasForeignKey(d => d.UserId)
                .HasConstraintName("fk_dialogue_users_2a7d7ec1");
        });

        modelBuilder.Entity<Efmigrationshistory>(entity =>
        {
            entity.HasKey(e => e.MigrationId).HasName("PRIMARY");

            entity.ToTable("__efmigrationshistory");

            entity.Property(e => e.MigrationId).HasMaxLength(150);
            entity.Property(e => e.ProductVersion).HasMaxLength(32);
        });

        modelBuilder.Entity<EmotionalHistory>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("PRIMARY");

            entity.ToTable("emotional_history");

            entity.HasIndex(e => e.SessionId, "fk_emotiona_sessions_59ae79ad");

            entity.HasIndex(e => e.Scene, "idx_emotional_h_scene_218596");

            entity.HasIndex(e => new { e.UserId, e.CreatedAt }, "idx_emotional_h_user_id_08b816");

            entity.Property(e => e.Id).HasColumnName("id");
            entity.Property(e => e.CreatedAt)
                .HasMaxLength(6)
                .HasDefaultValueSql("CURRENT_TIMESTAMP(6)")
                .HasColumnName("created_at");
            entity.Property(e => e.EmotionConfidence).HasColumnName("emotion_confidence");
            entity.Property(e => e.EmotionLabel)
                .HasMaxLength(50)
                .HasColumnName("emotion_label");
            entity.Property(e => e.EmotionStrength).HasColumnName("emotion_strength");
            entity.Property(e => e.EmotionTrend)
                .HasMaxLength(20)
                .HasColumnName("emotion_trend");
            entity.Property(e => e.IntentConfidence).HasColumnName("intent_confidence");
            entity.Property(e => e.Scene)
                .HasMaxLength(50)
                .HasDefaultValueSql("'chat'")
                .HasColumnName("scene");
            entity.Property(e => e.SessionId)
                .HasMaxLength(100)
                .HasColumnName("session_id");
            entity.Property(e => e.TrendConfidence).HasColumnName("trend_confidence");
            entity.Property(e => e.TriggerEvent).HasColumnName("trigger_event");
            entity.Property(e => e.UserId)
                .HasMaxLength(50)
                .HasColumnName("user_id");
            entity.Property(e => e.UserIntent)
                .HasMaxLength(50)
                .HasColumnName("user_intent");

            entity.HasOne(d => d.Session).WithMany(p => p.EmotionalHistories)
                .HasForeignKey(d => d.SessionId)
                .HasConstraintName("fk_emotiona_sessions_59ae79ad");

            entity.HasOne(d => d.User).WithMany(p => p.EmotionalHistories)
                .HasForeignKey(d => d.UserId)
                .HasConstraintName("fk_emotiona_users_b23484cf");
        });

        modelBuilder.Entity<GameDefinition>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("PRIMARY");

            entity.ToTable("game_definitions");

            entity.HasIndex(e => e.TypeIdId, "idx_game_defini_type_id_4128c4");

            entity.HasIndex(e => e.Name, "name").IsUnique();

            entity.Property(e => e.Id).HasColumnName("id");
            entity.Property(e => e.Name)
                .HasMaxLength(100)
                .HasColumnName("name");
            entity.Property(e => e.TypeIdId).HasColumnName("type_id_id");

            entity.HasOne(d => d.TypeId).WithMany(p => p.GameDefinitions)
                .HasForeignKey(d => d.TypeIdId)
                .HasConstraintName("fk_game_def_game_typ_90763966");
        });

        modelBuilder.Entity<GameSession>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("PRIMARY");

            entity.ToTable("game_sessions");

            entity.HasIndex(e => e.PersonaId, "fk_game_sessions_persona");

            entity.HasIndex(e => e.GameIdId, "idx_game_sessio_game_id_66ce49");

            entity.HasIndex(e => e.Status, "idx_game_sessio_status_e83f4d");

            entity.HasIndex(e => e.UserId, "idx_game_sessio_user_id_611fc4");

            entity.Property(e => e.Id).HasColumnName("id");
            entity.Property(e => e.EndTime)
                .HasMaxLength(6)
                .HasColumnName("end_time");
            entity.Property(e => e.GameConfig)
                .HasColumnType("json")
                .HasColumnName("game_config");
            entity.Property(e => e.GameIdId).HasColumnName("game_id_id");
            entity.Property(e => e.Loser)
                .HasMaxLength(20)
                .HasColumnName("loser");
            entity.Property(e => e.PersonaId)
                .HasMaxLength(50)
                .HasColumnName("persona_id");
            entity.Property(e => e.Score).HasColumnName("score");
            entity.Property(e => e.StartTime)
                .HasMaxLength(6)
                .HasDefaultValueSql("CURRENT_TIMESTAMP(6)")
                .HasColumnName("start_time");
            entity.Property(e => e.Status)
                .HasMaxLength(20)
                .HasDefaultValueSql("'playing'")
                .HasColumnName("status");
            entity.Property(e => e.UserId)
                .HasMaxLength(50)
                .HasColumnName("user_id");
            entity.Property(e => e.Winner)
                .HasMaxLength(20)
                .HasColumnName("winner");

            entity.HasOne(d => d.GameId).WithMany(p => p.GameSessions)
                .HasForeignKey(d => d.GameIdId)
                .HasConstraintName("fk_game_ses_game_def_e688daf5");

            entity.HasOne(d => d.Persona).WithMany(p => p.GameSessions)
                .HasForeignKey(d => d.PersonaId)
                .HasConstraintName("fk_game_sessions_persona");

            entity.HasOne(d => d.User).WithMany(p => p.GameSessions)
                .HasForeignKey(d => d.UserId)
                .HasConstraintName("fk_game_sessions_user");
        });

        modelBuilder.Entity<GameType>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("PRIMARY");

            entity.ToTable("game_types");

            entity.HasIndex(e => e.Name, "name").IsUnique();

            entity.Property(e => e.Id).HasColumnName("id");
            entity.Property(e => e.Description).HasColumnName("description");
            entity.Property(e => e.Name)
                .HasMaxLength(50)
                .HasColumnName("name");
        });

        modelBuilder.Entity<GridEmotionalHistory>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("PRIMARY");

            entity.ToTable("grid_emotional_history");

            entity.HasIndex(e => e.SessionId, "fk_grid_emo_sessions_088dddba");

            entity.HasIndex(e => new { e.UserId, e.CreatedAt }, "idx_grid_emotio_user_id_ceb4d6");

            entity.Property(e => e.Id).HasColumnName("id");
            entity.Property(e => e.CreatedAt)
                .HasMaxLength(6)
                .HasDefaultValueSql("CURRENT_TIMESTAMP(6)")
                .HasColumnName("created_at");
            entity.Property(e => e.EmotionConfidence).HasColumnName("emotion_confidence");
            entity.Property(e => e.EmotionLabel)
                .HasMaxLength(50)
                .HasColumnName("emotion_label");
            entity.Property(e => e.EmotionStrength).HasColumnName("emotion_strength");
            entity.Property(e => e.EmotionTrend)
                .HasMaxLength(20)
                .HasColumnName("emotion_trend");
            entity.Property(e => e.IntentConfidence).HasColumnName("intent_confidence");
            entity.Property(e => e.Scene)
                .HasMaxLength(50)
                .HasDefaultValueSql("'chat'")
                .HasColumnName("scene");
            entity.Property(e => e.SessionId)
                .HasMaxLength(100)
                .HasColumnName("session_id");
            entity.Property(e => e.TrendConfidence).HasColumnName("trend_confidence");
            entity.Property(e => e.TriggerEvent).HasColumnName("trigger_event");
            entity.Property(e => e.UserId)
                .HasMaxLength(50)
                .HasColumnName("user_id");
            entity.Property(e => e.UserIntent)
                .HasMaxLength(50)
                .HasColumnName("user_intent");

            entity.HasOne(d => d.Session).WithMany(p => p.GridEmotionalHistories)
                .HasForeignKey(d => d.SessionId)
                .HasConstraintName("fk_grid_emo_sessions_088dddba");

            entity.HasOne(d => d.User).WithMany(p => p.GridEmotionalHistories)
                .HasForeignKey(d => d.UserId)
                .HasConstraintName("fk_grid_emo_user_7be34f26");
        });

        modelBuilder.Entity<Memory>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("PRIMARY");

            entity.ToTable("memories");

            entity.HasIndex(e => e.ImportanceScore, "idx_memories_importa_f4bf1b");

            entity.HasIndex(e => new { e.UserId, e.MemoryType }, "idx_memories_user_id_c9fa7a");

            entity.Property(e => e.Id).HasColumnName("id");
            entity.Property(e => e.AccessCount).HasColumnName("access_count");
            entity.Property(e => e.Content).HasColumnName("content");
            entity.Property(e => e.CreatedAt)
                .HasMaxLength(6)
                .HasDefaultValueSql("CURRENT_TIMESTAMP(6)")
                .HasColumnName("created_at");
            entity.Property(e => e.EmbeddingVector).HasColumnName("embedding_vector");
            entity.Property(e => e.EmotionalWeight)
                .HasDefaultValueSql("'0.5'")
                .HasColumnName("emotional_weight");
            entity.Property(e => e.ImportanceScore)
                .HasDefaultValueSql("'0.5'")
                .HasColumnName("importance_score");
            entity.Property(e => e.LastAccessed)
                .HasMaxLength(6)
                .ValueGeneratedOnAddOrUpdate()
                .HasDefaultValueSql("CURRENT_TIMESTAMP(6)")
                .HasColumnName("last_accessed");
            entity.Property(e => e.MemoryType)
                .HasMaxLength(20)
                .HasColumnName("memory_type");
            entity.Property(e => e.Metadata)
                .HasColumnType("json")
                .HasColumnName("metadata");
            entity.Property(e => e.UserId)
                .HasMaxLength(50)
                .HasColumnName("user_id");

            entity.HasOne(d => d.User).WithMany(p => p.Memories)
                .HasForeignKey(d => d.UserId)
                .HasConstraintName("fk_memories_users_efb12a86");
        });

        modelBuilder.Entity<Persona>(entity =>
        {
            entity.HasKey(e => e.PersonaId).HasName("PRIMARY");

            entity.ToTable("personas");

            entity.HasIndex(e => e.FunctionalScene, "idx_personas_functio_4ea3ea");

            entity.HasIndex(e => e.Tone, "idx_personas_tone_123950");

            entity.Property(e => e.PersonaId)
                .HasMaxLength(50)
                .HasColumnName("persona_id");
            entity.Property(e => e.CreatedAt)
                .HasMaxLength(6)
                .HasDefaultValueSql("CURRENT_TIMESTAMP(6)")
                .HasColumnName("created_at");
            entity.Property(e => e.DeployType)
                .HasMaxLength(20)
                .HasDefaultValueSql("'cloud'")
                .HasColumnName("deploy_type");
            entity.Property(e => e.Description).HasColumnName("description");
            entity.Property(e => e.EmotionalBias)
                .HasColumnType("json")
                .HasColumnName("emotional_bias");
            entity.Property(e => e.FunctionalScene)
                .HasMaxLength(100)
                .HasDefaultValueSql("'general'")
                .HasColumnName("functional_scene");
            entity.Property(e => e.IsActive)
                .IsRequired()
                .HasDefaultValueSql("'1'")
                .HasColumnName("is_active");
            entity.Property(e => e.PersonaName)
                .HasMaxLength(100)
                .HasColumnName("persona_name");
            entity.Property(e => e.SpeechCharacteristics)
                .HasColumnType("json")
                .HasColumnName("speech_characteristics");
            entity.Property(e => e.Tone)
                .HasMaxLength(50)
                .HasDefaultValueSql("'neutral'")
                .HasColumnName("tone");
        });

        modelBuilder.Entity<Scene>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("PRIMARY");

            entity.ToTable("scene");

            entity.HasIndex(e => e.UserId, "fk_scene_user_bd43ffe3");

            entity.HasIndex(e => e.Name, "name").IsUnique();

            entity.Property(e => e.Id).HasColumnName("id");
            entity.Property(e => e.CreatedAt)
                .HasMaxLength(6)
                .HasDefaultValueSql("CURRENT_TIMESTAMP(6)")
                .HasColumnName("created_at");
            entity.Property(e => e.Description)
                .HasMaxLength(100)
                .HasColumnName("description");
            entity.Property(e => e.Name)
                .HasMaxLength(100)
                .HasColumnName("name");
            entity.Property(e => e.UserId)
                .HasMaxLength(50)
                .HasColumnName("user_id");

            entity.HasOne(d => d.User).WithMany(p => p.Scenes)
                .HasForeignKey(d => d.UserId)
                .HasConstraintName("fk_scene_user_bd43ffe3");
        });

        modelBuilder.Entity<Session>(entity =>
        {
            entity.HasKey(e => e.SessionId).HasName("PRIMARY");

            entity.ToTable("sessions");

            entity.HasIndex(e => e.CurrentPersonaId, "idx_sessions_current_2a10fc");

            entity.HasIndex(e => e.IsActive, "idx_sessions_is_acti_d424ed");

            entity.HasIndex(e => e.UserId, "idx_sessions_user_id_80072d");

            entity.Property(e => e.SessionId)
                .HasMaxLength(100)
                .HasColumnName("session_id");
            entity.Property(e => e.ConnectionInfo)
                .HasColumnType("json")
                .HasColumnName("connection_info");
            entity.Property(e => e.CreatedAt)
                .HasMaxLength(6)
                .HasDefaultValueSql("CURRENT_TIMESTAMP(6)")
                .HasColumnName("created_at");
            entity.Property(e => e.CurrentPersonaId)
                .HasMaxLength(50)
                .HasDefaultValueSql("'default'")
                .HasColumnName("current_persona_id");
            entity.Property(e => e.EmotionalContext)
                .HasColumnType("json")
                .HasColumnName("emotional_context");
            entity.Property(e => e.IsActive)
                .IsRequired()
                .HasDefaultValueSql("'1'")
                .HasColumnName("is_active");
            entity.Property(e => e.LastActivity)
                .HasMaxLength(6)
                .ValueGeneratedOnAddOrUpdate()
                .HasDefaultValueSql("CURRENT_TIMESTAMP(6)")
                .HasColumnName("last_activity");
            entity.Property(e => e.ParentSessionId)
                .HasMaxLength(50)
                .HasColumnName("parent_session_id");
            entity.Property(e => e.SessionName)
                .HasMaxLength(100)
                .HasDefaultValueSql("'默认会话'")
                .HasColumnName("session_name");
            entity.Property(e => e.UserId)
                .HasMaxLength(50)
                .HasColumnName("user_id");

            entity.HasOne(d => d.CurrentPersona).WithMany(p => p.Sessions)
                .HasForeignKey(d => d.CurrentPersonaId)
                .OnDelete(DeleteBehavior.ClientSetNull)
                .HasConstraintName("fk_sessions_personas_c41025ea");

            entity.HasOne(d => d.User).WithMany(p => p.Sessions)
                .HasForeignKey(d => d.UserId)
                .HasConstraintName("fk_sessions_users_b59db3f9");
        });

        modelBuilder.Entity<User>(entity =>
        {
            entity.HasKey(e => e.UserId).HasName("PRIMARY");

            entity.ToTable("user");

            entity.Property(e => e.UserId)
                .HasMaxLength(50)
                .HasColumnName("user_id");
            entity.Property(e => e.CreatedAt)
                .HasMaxLength(6)
                .HasDefaultValueSql("CURRENT_TIMESTAMP(6)")
                .HasColumnName("created_at");
            entity.Property(e => e.LastLogin)
                .HasMaxLength(6)
                .ValueGeneratedOnAddOrUpdate()
                .HasDefaultValueSql("CURRENT_TIMESTAMP(6)")
                .HasColumnName("last_login");
            entity.Property(e => e.Pwd)
                .HasMaxLength(50)
                .HasColumnName("pwd");
            entity.Property(e => e.RelationshipLevel)
                .HasDefaultValueSql("'1'")
                .HasColumnName("relationship_level");
            entity.Property(e => e.TotalInteractionCount).HasColumnName("total_interaction_count");
            entity.Property(e => e.Username)
                .HasMaxLength(100)
                .HasColumnName("username");
        });

        modelBuilder.Entity<UserPersonaMapping>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("PRIMARY");

            entity.ToTable("user_persona_mapping");

            entity.HasIndex(e => e.PersonaId, "fk_user_per_personas_4b6a9207");

            entity.HasIndex(e => new { e.UserId, e.PersonaId }, "idx_user_person_user_id_7a228b").IsUnique();

            entity.Property(e => e.Id).HasColumnName("id");
            entity.Property(e => e.CreatedAt)
                .HasMaxLength(6)
                .HasDefaultValueSql("CURRENT_TIMESTAMP(6)")
                .HasColumnName("created_at");
            entity.Property(e => e.IsDefault).HasColumnName("is_default");
            entity.Property(e => e.PersonaId)
                .HasMaxLength(50)
                .HasColumnName("persona_id");
            entity.Property(e => e.UserId)
                .HasMaxLength(50)
                .HasColumnName("user_id");

            entity.HasOne(d => d.Persona).WithMany(p => p.UserPersonaMappings)
                .HasForeignKey(d => d.PersonaId)
                .HasConstraintName("fk_user_per_personas_4b6a9207");

            entity.HasOne(d => d.User).WithMany(p => p.UserPersonaMappings)
                .HasForeignKey(d => d.UserId)
                .HasConstraintName("fk_user_per_users_959325a2");
        });

        OnModelCreatingPartial(modelBuilder);
    }

    partial void OnModelCreatingPartial(ModelBuilder modelBuilder);
}
