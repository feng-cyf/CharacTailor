from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `users` DROP FOREIGN KEY `fk_users_personas_98839158`;
        ALTER TABLE `users` DROP COLUMN `default_persona_id`;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `users` ADD `default_persona_id` VARCHAR(50) NOT NULL DEFAULT 'default';
        ALTER TABLE `users` ADD CONSTRAINT `fk_users_personas_98839158` FOREIGN KEY (`default_persona_id`) REFERENCES `personas` (`persona_id`) ON DELETE SET DEFAULT;"""


MODELS_STATE = (
    "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"
)
