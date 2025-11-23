from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `emotional_history` ADD `emotion_trend` VARCHAR(20) NOT NULL;
        ALTER TABLE `emotional_history` ADD `emotion_strength` DOUBLE NOT NULL;
        ALTER TABLE `emotional_history` ADD `emotion_label` VARCHAR(50) NOT NULL;
        ALTER TABLE `emotional_history` ADD `emotion_confidence` DOUBLE NOT NULL;
        ALTER TABLE `emotional_history` ADD `trend_confidence` DOUBLE NOT NULL;
        ALTER TABLE `emotional_history` ADD `user_intent` VARCHAR(50) NOT NULL;
        ALTER TABLE `emotional_history` ADD `intent_confidence` DOUBLE NOT NULL;
        ALTER TABLE `emotional_history` DROP COLUMN `emotion_source`;
        ALTER TABLE `emotional_history` DROP COLUMN `sadness`;
        ALTER TABLE `emotional_history` DROP COLUMN `calmness`;
        ALTER TABLE `emotional_history` DROP COLUMN `excitement`;
        ALTER TABLE `emotional_history` DROP COLUMN `anxiety`;
        ALTER TABLE `emotional_history` DROP COLUMN `emotional_valence`;
        ALTER TABLE `emotional_history` DROP COLUMN `duration`;
        ALTER TABLE `emotional_history` DROP COLUMN `mood_intensity`;
        ALTER TABLE `emotional_history` DROP COLUMN `dominant_mood`;
        ALTER TABLE `emotional_history` DROP COLUMN `anger`;
        ALTER TABLE `emotional_history` DROP COLUMN `emotional_stability`;
        ALTER TABLE `emotional_history` DROP COLUMN `happiness`;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `emotional_history` ADD `emotion_source` VARCHAR(50) NOT NULL DEFAULT 'system';
        ALTER TABLE `emotional_history` ADD `sadness` DOUBLE NOT NULL DEFAULT 0.1;
        ALTER TABLE `emotional_history` ADD `calmness` DOUBLE NOT NULL DEFAULT 0.6;
        ALTER TABLE `emotional_history` ADD `excitement` DOUBLE NOT NULL DEFAULT 0.3;
        ALTER TABLE `emotional_history` ADD `anxiety` DOUBLE NOT NULL DEFAULT 0.2;
        ALTER TABLE `emotional_history` ADD `emotional_valence` DOUBLE NOT NULL DEFAULT 0;
        ALTER TABLE `emotional_history` ADD `duration` INT NOT NULL DEFAULT 15;
        ALTER TABLE `emotional_history` ADD `mood_intensity` DOUBLE NOT NULL DEFAULT 0.4;
        ALTER TABLE `emotional_history` ADD `dominant_mood` VARCHAR(20) NOT NULL DEFAULT 'neutral';
        ALTER TABLE `emotional_history` ADD `anger` DOUBLE NOT NULL DEFAULT 0.1;
        ALTER TABLE `emotional_history` ADD `emotional_stability` DOUBLE NOT NULL DEFAULT 0.7;
        ALTER TABLE `emotional_history` ADD `happiness` DOUBLE NOT NULL DEFAULT 0.5;
        ALTER TABLE `emotional_history` DROP COLUMN `emotion_trend`;
        ALTER TABLE `emotional_history` DROP COLUMN `emotion_strength`;
        ALTER TABLE `emotional_history` DROP COLUMN `emotion_label`;
        ALTER TABLE `emotional_history` DROP COLUMN `emotion_confidence`;
        ALTER TABLE `emotional_history` DROP COLUMN `trend_confidence`;
        ALTER TABLE `emotional_history` DROP COLUMN `user_intent`;
        ALTER TABLE `emotional_history` DROP COLUMN `intent_confidence`;"""


MODELS_STATE = (
    "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"
)
