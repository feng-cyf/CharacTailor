from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `dialogue_history` ADD `emotion_type` VARCHAR(10) NOT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `dialogue_history` DROP COLUMN `emotion_type`;"""


MODELS_STATE = (
    "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"
    "A1oiu1C9YXn4HxaEWV0="
)
