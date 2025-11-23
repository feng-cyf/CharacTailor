from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `emotional_history` ADD `session_id` VARCHAR(100) NOT NULL;
        ALTER TABLE `emotional_history` ADD CONSTRAINT `fk_emotiona_sessions_59ae79ad` FOREIGN KEY (`session_id`) REFERENCES `sessions` (`session_id`) ON DELETE CASCADE;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `emotional_history` DROP FOREIGN KEY `fk_emotiona_sessions_59ae79ad`;
        ALTER TABLE `emotional_history` DROP COLUMN `session_id`;"""


MODELS_STATE = (
    "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"
    "oA"
)
