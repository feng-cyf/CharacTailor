from models.model import Memories


class MemoriesProcess:
    def __init__(self, user_id):
        self.user_id = user_id
    async def get_memory(self):
        user_memory=await Memories.filter(user_id=self.user_id).all()
        data={
            m.memory_type:m.content for m in user_memory
        }
        return data