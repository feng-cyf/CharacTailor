from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `sessions` ADD `session_name` VARCHAR(100) DEFAULT '默认会话';
        ALTER TABLE `sessions` ADD `parent_session_id` VARCHAR(50);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `sessions` DROP COLUMN `session_name`;
        ALTER TABLE `sessions` DROP COLUMN `parent_session_id`;"""


MODELS_STATE = (
    "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"
)
