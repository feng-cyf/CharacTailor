from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `users` RENAME TO `user`;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `user` RENAME TO `users`;"""


MODELS_STATE = (
    "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"
)
