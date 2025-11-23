import aiomysql

from database.raw_mysql import get_raw_pool

async def persona_users(u_id: str):
    pool = get_raw_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:

            # 1. 用户关联人设
            await cur.execute(
                "SELECT persona_id FROM user_persona_mapping WHERE user_id = %s",
                (u_id,)
            )
            mappings = await cur.fetchall()
            persona_ids = [r["persona_id"] for r in mappings]
            if not persona_ids:
                return {"code": 404, "msg": "未找到关联的人设详情"}

            # 2. 人设详情
            placeholders = ",".join(["%s"] * len(persona_ids))
            await cur.execute(f"""
                SELECT persona_id,
                       persona_name,
                       description,
                       tone,
                       deploy_type
                FROM   personas
                WHERE  persona_id IN ({placeholders})
            """, persona_ids)
            personas = await cur.fetchall()
            if not personas:
                return {"code": 404, "msg": "未找到人设详情"}

            # 3. 最新会话
            await cur.execute(f"""
                SELECT current_persona_id,
                       session_id
                FROM   sessions
                WHERE  user_id = %s
                  AND  current_persona_id IN ({placeholders})
                ORDER  BY last_activity DESC
            """, [u_id, *persona_ids])
            sessions = await cur.fetchall()
            sess_map = {s["current_persona_id"]: s["session_id"] for s in sessions}

            # 4. 拼结果 - 确保字段名称与前端期望一致
            data = [
                {
                    "persona_id": p["persona_id"],
                    "persona_name": p["persona_name"],
                    "description": p["description"],
                    "tone": p["tone"],
                    "is_cloud_model": p["deploy_type"] == 'cloud',
                    "session_id": sess_map.get(p["persona_id"]),
                }
                for p in personas
            ]
            return {"code": 200, "data": data}