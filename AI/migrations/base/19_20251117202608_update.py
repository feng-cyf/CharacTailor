from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `scene` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `name` VARCHAR(100) NOT NULL UNIQUE,
    `description` VARCHAR(100),
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `user_id` VARCHAR(50) NOT NULL,
    CONSTRAINT `fk_scene_user_bd43ffe3` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `scene`;"""


MODELS_STATE = (
    "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"
)
