from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `dialogue_history` ADD `type` VARCHAR(10) NOT NULL DEFAULT 'text';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `dialogue_history` DROP COLUMN `type`;"""


MODELS_STATE = (
    "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"
)
