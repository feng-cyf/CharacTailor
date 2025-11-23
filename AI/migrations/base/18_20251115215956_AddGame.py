from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `game_sessions` DROP INDEX `idx_game_sessio_persona_bb2c58`;
        CREATE TABLE IF NOT EXISTS `game_types` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `name` VARCHAR(50) NOT NULL UNIQUE,
    `description` LONGTEXT
) CHARACTER SET utf8mb4;
        CREATE TABLE IF NOT EXISTS `game_definitions` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `name` VARCHAR(100) NOT NULL UNIQUE,
    `type_id_id` INT NOT NULL,
    CONSTRAINT `fk_game_def_game_typ_90763966` FOREIGN KEY (`type_id_id`) REFERENCES `game_types` (`id`) ON DELETE CASCADE,
    KEY `idx_game_defini_type_id_4128c4` (`type_id_id`)
) CHARACTER SET utf8mb4;
        ALTER TABLE `game_sessions` ADD `game_id_id` INT NOT NULL;
        ALTER TABLE `game_sessions` ADD `game_config` JSON;
        ALTER TABLE `game_sessions` ADD `score` INT NOT NULL DEFAULT 0;
        ALTER TABLE `game_sessions` DROP COLUMN `game_type`;
        ALTER TABLE `game_sessions` DROP COLUMN `game_name`;
        ALTER TABLE `game_sessions` ADD CONSTRAINT `fk_game_ses_game_def_e688daf5` FOREIGN KEY (`game_id_id`) REFERENCES `game_definitions` (`id`) ON DELETE CASCADE;
        ALTER TABLE `game_sessions` ADD INDEX `idx_game_sessio_game_id_66ce49` (`game_id_id`);
        ALTER TABLE `game_sessions` ADD INDEX `idx_game_sessio_status_e83f4d` (`status`);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `game_sessions` DROP INDEX `idx_game_sessio_status_e83f4d`;
        ALTER TABLE `game_sessions` DROP INDEX `idx_game_sessio_game_id_66ce49`;
        ALTER TABLE `game_sessions` DROP FOREIGN KEY `fk_game_ses_game_def_e688daf5`;
        ALTER TABLE `game_sessions` ADD `game_type` VARCHAR(50) NOT NULL;
        ALTER TABLE `game_sessions` ADD `game_name` VARCHAR(50) NOT NULL;
        ALTER TABLE `game_sessions` DROP COLUMN `game_id_id`;
        ALTER TABLE `game_sessions` DROP COLUMN `game_config`;
        ALTER TABLE `game_sessions` DROP COLUMN `score`;
        DROP TABLE IF EXISTS `game_definitions`;
        DROP TABLE IF EXISTS `game_types`;
        ALTER TABLE `game_sessions` ADD INDEX `idx_game_sessio_persona_bb2c58` (`persona_id`);"""


MODELS_STATE = (
    "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"
)
