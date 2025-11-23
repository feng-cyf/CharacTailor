from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `game_sessions` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `start_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `end_time` DATETIME(6),
    `winner` VARCHAR(20),
    `loser` VARCHAR(20),
    `game_type` VARCHAR(50) NOT NULL,
    `game_name` VARCHAR(50) NOT NULL,
    `status` VARCHAR(20) NOT NULL DEFAULT 'playing',
    `persona_id` VARCHAR(50) NOT NULL,
    `user_id` VARCHAR(50) NOT NULL,
    CONSTRAINT `fk_game_ses_personas_dde51405` FOREIGN KEY (`persona_id`) REFERENCES `personas` (`persona_id`) ON DELETE CASCADE,
    CONSTRAINT `fk_game_ses_user_5b769f80` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`) ON DELETE CASCADE,
    KEY `idx_game_sessio_user_id_611fc4` (`user_id`),
    KEY `idx_game_sessio_persona_bb2c58` (`persona_id`)
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `game_sessions`;"""


MODELS_STATE = (
    "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"
)
