from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `dialogue_history` RENAME COLUMN `type` TO `bot_response_type`;
        ALTER TABLE `dialogue_history` ADD `user_message_type` VARCHAR(10) NOT NULL DEFAULT 'text';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `dialogue_history` RENAME COLUMN `bot_response_type` TO `type`;
        ALTER TABLE `dialogue_history` DROP COLUMN `user_message_type`;"""


MODELS_STATE = (
    "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"
    "5F"
)
