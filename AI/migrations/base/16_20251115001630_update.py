from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `dialogue_history` ADD `bot_audio_url` VARCHAR(100);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `dialogue_history` DROP COLUMN `bot_audio_url`;"""


MODELS_STATE = (
    "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"
)
