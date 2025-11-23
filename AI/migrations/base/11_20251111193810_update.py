from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `grid_emotional_history` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `emotion_label` VARCHAR(50) NOT NULL,
    `emotion_strength` DOUBLE NOT NULL,
    `emotion_confidence` DOUBLE NOT NULL,
    `emotion_trend` VARCHAR(20) NOT NULL,
    `trend_confidence` DOUBLE NOT NULL,
    `user_intent` VARCHAR(50) NOT NULL,
    `intent_confidence` DOUBLE NOT NULL,
    `trigger_event` LONGTEXT,
    `scene` VARCHAR(50) NOT NULL DEFAULT 'chat',
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `session_id` VARCHAR(100) NOT NULL,
    `user_id` VARCHAR(50) NOT NULL,
    CONSTRAINT `fk_grid_emo_sessions_088dddba` FOREIGN KEY (`session_id`) REFERENCES `sessions` (`session_id`) ON DELETE CASCADE,
    CONSTRAINT `fk_grid_emo_user_7be34f26` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`) ON DELETE CASCADE,
    KEY `idx_grid_emotio_user_id_ceb4d6` (`user_id`, `created_at`)
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `grid_emotional_history`;
        ALTER TABLE `user` ADD INDEX `idx_user_default_af931b` (`default_persona_id`);"""


MODELS_STATE = (
    "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"
    "c2mCW8E3Sabe3XpRaTZ1gQ2Y8heW5/8BQNq80A=="
)
