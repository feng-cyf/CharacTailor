from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `personas` (
    `persona_id` VARCHAR(50) NOT NULL PRIMARY KEY,
    `persona_name` VARCHAR(100) NOT NULL,
    `description` LONGTEXT,
    `tone` VARCHAR(50) NOT NULL DEFAULT 'neutral',
    `speech_characteristics` JSON,
    `functional_scene` VARCHAR(100) NOT NULL DEFAULT 'general',
    `emotional_bias` JSON,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `is_active` BOOL NOT NULL DEFAULT 1,
    KEY `idx_personas_functio_4ea3ea` (`functional_scene`),
    KEY `idx_personas_tone_123950` (`tone`)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `users` (
    `user_id` VARCHAR(50) NOT NULL PRIMARY KEY,
    `username` VARCHAR(100) NOT NULL,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `last_login` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `total_interaction_count` INT NOT NULL DEFAULT 0,
    `relationship_level` INT NOT NULL DEFAULT 1,
    `default_persona_id` VARCHAR(50) NOT NULL DEFAULT 'default',
    CONSTRAINT `fk_users_personas_98839158` FOREIGN KEY (`default_persona_id`) REFERENCES `personas` (`persona_id`) ON DELETE SET DEFAULT,
    KEY `idx_users_default_19af58` (`default_persona_id`)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `emotional_history` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `happiness` DOUBLE NOT NULL DEFAULT 0.5,
    `sadness` DOUBLE NOT NULL DEFAULT 0.1,
    `anger` DOUBLE NOT NULL DEFAULT 0.1,
    `anxiety` DOUBLE NOT NULL DEFAULT 0.2,
    `calmness` DOUBLE NOT NULL DEFAULT 0.6,
    `excitement` DOUBLE NOT NULL DEFAULT 0.3,
    `mood_intensity` DOUBLE NOT NULL DEFAULT 0.4,
    `emotional_valence` DOUBLE NOT NULL DEFAULT 0,
    `emotional_stability` DOUBLE NOT NULL DEFAULT 0.7,
    `dominant_mood` VARCHAR(20) NOT NULL DEFAULT 'neutral',
    `trigger_event` LONGTEXT,
    `scene` VARCHAR(50) NOT NULL DEFAULT 'chat',
    `emotion_source` VARCHAR(50) NOT NULL DEFAULT 'system',
    `duration` INT NOT NULL DEFAULT 15,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `user_id` VARCHAR(50) NOT NULL,
    CONSTRAINT `fk_emotiona_users_b23484cf` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
    KEY `idx_emotional_h_user_id_08b816` (`user_id`, `created_at`),
    KEY `idx_emotional_h_scene_218596` (`scene`)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `memories` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `memory_type` VARCHAR(20) NOT NULL,
    `content` LONGTEXT NOT NULL,
    `embedding_vector` LONGBLOB,
    `importance_score` DOUBLE NOT NULL DEFAULT 0.5,
    `emotional_weight` DOUBLE NOT NULL DEFAULT 0.5,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `last_accessed` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `access_count` INT NOT NULL DEFAULT 0,
    `metadata` JSON,
    `user_id` VARCHAR(50) NOT NULL,
    CONSTRAINT `fk_memories_users_efb12a86` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
    KEY `idx_memories_user_id_c9fa7a` (`user_id`, `memory_type`),
    KEY `idx_memories_importa_f4bf1b` (`importance_score`)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `sessions` (
    `session_id` VARCHAR(100) NOT NULL PRIMARY KEY,
    `connection_info` JSON,
    `is_active` BOOL NOT NULL DEFAULT 1,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `last_activity` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `emotional_context` JSON,
    `current_persona_id` VARCHAR(50) NOT NULL DEFAULT 'default',
    `user_id` VARCHAR(50) NOT NULL,
    CONSTRAINT `fk_sessions_personas_c41025ea` FOREIGN KEY (`current_persona_id`) REFERENCES `personas` (`persona_id`) ON DELETE SET DEFAULT,
    CONSTRAINT `fk_sessions_users_b59db3f9` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
    KEY `idx_sessions_user_id_80072d` (`user_id`),
    KEY `idx_sessions_is_acti_d424ed` (`is_active`),
    KEY `idx_sessions_current_2a10fc` (`current_persona_id`)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `dialogue_history` (
    `dialogue_id` VARCHAR(100) NOT NULL PRIMARY KEY,
    `user_message` LONGTEXT NOT NULL,
    `bot_response` LONGTEXT NOT NULL,
    `emotional_feedback` DOUBLE NOT NULL DEFAULT 0.5,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `persona_id` VARCHAR(50) NOT NULL,
    `session_id` VARCHAR(100) NOT NULL,
    `user_id` VARCHAR(50) NOT NULL,
    CONSTRAINT `fk_dialogue_personas_5f7b6b54` FOREIGN KEY (`persona_id`) REFERENCES `personas` (`persona_id`) ON DELETE RESTRICT,
    CONSTRAINT `fk_dialogue_sessions_279e846f` FOREIGN KEY (`session_id`) REFERENCES `sessions` (`session_id`) ON DELETE CASCADE,
    CONSTRAINT `fk_dialogue_users_2a7d7ec1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
    KEY `idx_dialogue_hi_persona_8af913` (`persona_id`),
    KEY `idx_dialogue_hi_user_id_a64a2d` (`user_id`, `session_id`)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `user_persona_mapping` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `is_default` BOOL NOT NULL DEFAULT 0,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `persona_id` VARCHAR(50) NOT NULL,
    `user_id` VARCHAR(50) NOT NULL,
    UNIQUE KEY `uid_user_person_user_id_7a228b` (`user_id`, `persona_id`),
    CONSTRAINT `fk_user_per_personas_4b6a9207` FOREIGN KEY (`persona_id`) REFERENCES `personas` (`persona_id`) ON DELETE CASCADE,
    CONSTRAINT `fk_user_per_users_959325a2` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
    KEY `idx_user_person_user_id_7a228b` (`user_id`, `persona_id`)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `aerich` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `version` VARCHAR(255) NOT NULL,
    `app` VARCHAR(100) NOT NULL,
    `content` JSON NOT NULL
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """


MODELS_STATE = (
    "eJztXV1v27gS/SuBn7pAtmi9TVvsm524t95N4iJx7t3doBAYibGJSqQr0WmMRf77Jakvii"
    "IVK5YVKeVLYJEcSTwccmYOR8y/gxsQwdcnCPhksYafUURJuBn8fvDvAIMAsh/6BocHA7Ba"
    "pdX8koIbX7T3kqbOUmp7E9EQuJTV3wI/gqzIg5EbohVFBLNSvPZ9Xkhc1hDhRV60xug7ux"
    "klC0iXMGQV119ZMcIevIcRv7werGAYEQwc5A1Y3fVgHcGQX7B2EYwi9ghRxeVW35xbBH2v"
    "0MXslWMZ0cChm5WoPF6C8JMQ4S9447jEXwdYI7ba0CV7UirHOsJLFxDDEFDoSX3nXUvgSo"
    "vibrICGq5h1j8vL/DgLVj7VMJqSwBdgjn4CNNIdDoA944P8YIu2eXbN28e4m7lnY6b8S78"
    "d3Rx/Hl08Yq1+oX3hbAxjAf5PKkaxnUP4iaAgvg2YlhyeMVwBGwgwAKW8Z3De6rHV5VrBu"
    "C0IEc4V8lmIK5AdD75a85fOoii774M5Kuz0V8C42CT1JzOzv+TNpeAPz6djQXe0gwl1Alh"
    "tGJvUQtfVc7iq8cXBoS/IvCdWwi9G+B+K6P8ySfAALNeXAH7lsvvC+43r4/2gvbJ7Gp8Oj"
    "n4cjE5nl5OZ+cFfONKsQZ/9xEVvbyYjE4VcN0Q8t46ce+LoJ6wGooCqMe1KKng6SWir9Mf"
    "3VTlAeuDN8P+Jlnoq1R7eja5nI/OvhT0+2Q0n/CaYRH7pPTVe2Xdzm5y8L/p/PMBvzz4Z3"
    "YuhmlFIroIxRPzdvN/BvydwJoSB5MfDvAkm5SWpsAUBlYyyjVsalGqLytS0agebWNTj8wm"
    "9SixqDmWkhdTA8uiVD+xbNBBURySelhKIv0Eshml5C707Tetl5dom8Y0khCiBf4TbgS0U/"
    "aSALs6j0OEGpf5fbqH6UOqF2lpvhiG4EcWWihTj/3woA9jG3g8ujwenUwGJY3cGbmr5Cb9"
    "hU2aZY9jlpiKnWH7kt+nv8gV7WYBvAtmyS+mx/OBmL3c//wBQs8pTGNeQ4ZEKcnalquCYa"
    "CWAMziNC/pycNhgu4k9X6N3EKpxaGZXMh96fbYBUkpJZdTEA2RyxSmgljQ2ZgpNsQJWuvC"
    "R1xRzGT4n5VEWPCn/Dp8++7Du4+/vX/3kTURb5KVfKiwNtPz+SOMwZKNP8JsDa0VaBWkbH"
    "yVmGXg1QZSkmkXxredhRHghdZCm0HMJCyEKYT3CNJNTRAzmXZhHHYWRhf4Qe0ZLQu1C+T7"
    "zgIJ711WGUCsYZ6q6LyCWLtg/tZZMANCPIc9C+II1ZzjZdF2QX3XWVBzb/cOsEDe1bD7W/"
    "HOknS70L7pAbQsOLxBfl2lNci3C++HzsLrkQBhgKnDJ3etPVVVsD22bYDhmiHkD56OapFy"
    "G25DuQ3NlNuwRFyypy+YV+nAO63VMm/1lQSfBGsSRb7grb44oK+hr5lAi3rqLuNFpUO8sG"
    "ZpdSKyDnUmywxmWbJFVKNNxNy6DuPqrVmftQy7kVKSRR4nlpqC8u0ObEgzzJLdXn7x28t2"
    "D28Pe3h2G2q7bajn2Eg5Y9YxRMmAFzZQsppD88ZJILdpbb9EPHUTq4fYMEHBioRCe5zIZW"
    "pl904a3zuRMa+xOCpi/Vwgm4+42ONozVhLEukLiu1nVN5Az2Nv5NxBlxKNzRkjDMKNKUwo"
    "S6uGaEPjta5PEe2YAyVDzZAeT89HF3/rsU7by57V+O/5ZKSgXVp0yxbeTHTphO3eqkoi/m"
    "AO0rLmPoJG2AJro7YXHbX5IKIOcF0YRVDj31WPbUnYDu+zDm/y8tIOvxgbNmJrncdkdN5V"
    "sfaYqh32p5omqgJIAffpy7j9cTk7N/nsuYwC2hVm/bn2kEsPD3wU0a99c4Z4r6v9TtXFVN"
    "SZ30D1Oy1pZEmjn4o0SnObS5yRlPRsooySlOI2KKPbNXbT7fQ4pZaTRZRUJtd25wOjdr/Z"
    "bWpnyUwhpRiJ6ydgm8r1c8HcyydH8puVEDVzSYqY3bXX0klioaihp2n7HueW7OEbwxWE7t"
    "JxGWpsoYchcxqRq8kyNbuj5jtY53QL57RkBGtotE62Re2Ob9qcdu9lCc4JtxsEail2WdIq"
    "9BYKbVm8F0HzlFk8FDlsgUd3miVqTIgPATbsJchyahTIBPc1kJk73viOzWx2Whiz8VR1V6"
    "7OxhO2VP1S5Lxj/qcUVJtDxPJhRZoVbJyIfvrzAvqmxC/TeU7dm0GmyFvhHLlCOckH1zuB"
    "0ssvz5UoQzzM4VzETlD0j44p83xpNBqIz0IXO+ORUCZn8e16hs6OFFMRWg2UZwBv5oT/3S"
    "vdt2+mpYLsC4gHfadAoqW9CLn2MHdF4U9imEgoEP4GNxl8CfmUoZ/UFakpugzJerE0qbOR"
    "Z2Tljpry9FBBEaarXokilJZDE0Uor7otZZXFaWSZIyEu3XUYQkwd+RxAI23YnbN0XuBRf+"
    "wNMBSRqIPwLakTZGlEbZR1+HiUZZ3xZpxxG7n+BJFrkkLC1F77wedW+Se5sB3ebuWf5Dyd"
    "yMG918zebUg+SdhaoC0skMb9quFZ6aVbJK/Tn005Ws1vzdi0FZu20okj95S5ujN8ez56r4"
    "GpvS2M+lWsgOjlZH5wMvk0ujqtPIrPMr3N0VYVtIeYuSXOI53PJsIjY7/2zHakRO5WjEYX"
    "zMNLS4HiANVNf5Jl+ml097LvboPpFxFtGYJpZlyQJqVti0g6k7QD260wmhLKomB+Ihu3cJ"
    "yQrftFR8UdfsqPO8LESYuWaMVW2zvo1wBTL9zicS7dwVHjFtWwz3rpn55pqIiRFcRsvJfF"
    "e3pdsvFeg0kc6lnvaDdgdMfM9xQZ+TCXp8IhHxrTUxhsztcgDeVtrtM+cp0KeTy7pDvtYP"
    "e6lfEkdURNesoTw4oZT0ULqeY8yflQTWU8xZHqI9yfouFaJrA8C6p4Qd37NksTXmebFqlD"
    "9tWYJ3VYQN4es9X0MVsociRvs17ejSTYYuJNXQW0mTeWU7L/DrIrUbrNB7D5AJ3LB+gJL9"
    "QOchVU0LOeATKCIXKXg5KHm5RXeLUgb7HP7W7rmzbsm94xTdQeNGG2D5JIP+3D8OhoCwPB"
    "WpkPf+V1yr8sYxOjBohJ834CuJ+9f9PxuZXfgRiOz31K9u3z2Yu9pt/W+HK4ecPy8H9rVX"
    "mp"
)
