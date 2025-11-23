from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `dialogue_history` ADD `confidence` DOUBLE NOT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `dialogue_history` DROP COLUMN `confidence`;"""


MODELS_STATE = (
    "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"
)
