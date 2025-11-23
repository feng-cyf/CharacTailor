from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `dialogue_history` MODIFY COLUMN `user_file_url` VARCHAR(100);
        ALTER TABLE `dialogue_history` MODIFY COLUMN `bot_file_url` VARCHAR(100);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `dialogue_history` MODIFY COLUMN `user_file_url` VARCHAR(100) NOT NULL;
        ALTER TABLE `dialogue_history` MODIFY COLUMN `bot_file_url` VARCHAR(100) NOT NULL;"""


MODELS_STATE = (
    "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"
)
