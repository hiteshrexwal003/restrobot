import json, os
import redis.asyncio as redis
from datetime import datetime

class RedisMemoryManager:
    def __init__(self, host="localhost", port=6379, db=0, ttl=3600):
        self.host = os.getenv("REDIS_HOST", host)
        self.port = int(os.getenv("REDIS_PORT", port))
        self.db = int(os.getenv("REDIS_DB", db))
        self.ttl = int(os.getenv("REDIS_TTL", ttl))
        self.password = os.getenv("REDIS_PASSWORD", None)
        self.redis = None

    async def connect(self):
        if not self.redis:
            url = f"rediss://:{self.password}@{self.host}:{self.port}/{self.db}"
            self.redis = await redis.from_url(
                url,
                encoding="utf-8",
                decode_responses=True,
                ssl_cert_reqs="required"
            )

    async def add_message(self, session_id, sender, message):
        await self.connect()
        key = f"session:{session_id}:messages"
        entry = json.dumps({
            "sender": sender,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        })
        await self.redis.rpush(key, entry)
        await self.redis.expire(key, self.ttl)

    async def get_history(self, session_id):
        await self.connect()
        key = f"session:{session_id}:messages"
        data = await self.redis.lrange(key, 0, -1)
        return [json.loads(x) for x in data]

    async def set_user_data(self, session_id, data):
        await self.connect()
        key = f"session:{session_id}:user_data"
        await self.redis.set(key, json.dumps(data), ex=self.ttl)

    async def get_user_data(self, session_id):
        await self.connect()
        key = f"session:{session_id}:user_data"
        data = await self.redis.get(key)
        return json.loads(data) if data else {}
    
redis_memory = RedisMemoryManager()