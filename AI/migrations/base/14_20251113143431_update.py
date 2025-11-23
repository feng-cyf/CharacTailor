from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `dialogue_history` ADD `bot_file_url` VARCHAR(100) NOT NULL;
        ALTER TABLE `dialogue_history` ADD `user_file_url` VARCHAR(100) NOT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `dialogue_history` DROP COLUMN `bot_file_url`;
        ALTER TABLE `dialogue_history` DROP COLUMN `user_file_url`;"""


MODELS_STATE = (
    "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"
)
