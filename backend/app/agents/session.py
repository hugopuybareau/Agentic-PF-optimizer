# backend/app/agent/session_storage.py

import json
import logging
import os
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

import redis
from redis.exceptions import ConnectionError as RedisConnectionError

from .state.chat_state import ChatSession

logger = logging.getLogger(__name__)


class SessionStorage(ABC):
    """Abstract base class for session storage"""

    @abstractmethod
    def get(self, session_id: str) -> ChatSession | None:
        pass

    @abstractmethod
    def set(self, session_id: str, session: ChatSession) -> None:
        pass

    @abstractmethod
    def delete(self, session_id: str) -> None:
        pass

    @abstractmethod
    def exists(self, session_id: str) -> bool:
        pass

    @abstractmethod
    def cleanup_expired(self) -> int:
        pass


class InMemorySessionStorage(SessionStorage):
    """Simple in-memory storage for development"""

    def __init__(self, ttl_minutes: int = 60):
        self.sessions: dict[str, ChatSession] = {}
        self.ttl = timedelta(minutes=ttl_minutes)

    def get(self, session_id: str) -> ChatSession | None:
        session = self.sessions.get(session_id)
        if session and self._is_expired(session):
            del self.sessions[session_id]
            return None
        return session

    def set(self, session_id: str, session: ChatSession) -> None:
        self.sessions[session_id] = session

    def delete(self, session_id: str) -> None:
        self.sessions.pop(session_id, None)

    def exists(self, session_id: str) -> bool:
        return session_id in self.sessions and not self._is_expired(self.sessions[session_id])

    def cleanup_expired(self) -> int:
        expired = []
        for sid, session in self.sessions.items():
            if self._is_expired(session):
                expired.append(sid)

        for sid in expired:
            del self.sessions[sid]

        return len(expired)

    def _is_expired(self, session: ChatSession) -> bool:
        return datetime.now() - session.last_activity > self.ttl


class RedisSessionStorage(SessionStorage):
    """Redis-based session storage for production"""

    def __init__(self, redis_url: str | None = None, ttl_minutes: int = 60):
        self.redis_url = redis_url or os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        self.ttl = ttl_minutes * 60  # Convert to seconds
        self.key_prefix = "chat_session:"

        try:
            self.client = redis.from_url(self.redis_url, decode_responses=True)
            self.client.ping()
            logger.info("Connected to Redis for session storage")
        except RedisConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    def get(self, session_id: str) -> ChatSession | None:
        try:
            key = f"{self.key_prefix}{session_id}"
            data = self.client.get(key)

            if not data:
                return None

            session_dict = json.loads(data) # type: ignore
            return ChatSession(**session_dict)

        except Exception as e:
            logger.error(f"Failed to get session {session_id}: {e}")
            return None

    def set(self, session_id: str, session: ChatSession) -> None:
        try:
            key = f"{self.key_prefix}{session_id}"

            # Convert session to JSON-serializable dict
            session_dict = session.model_dump()

            # Handle datetime serialization
            for field in ['created_at', 'last_activity']:
                if field in session_dict:
                    session_dict[field] = session_dict[field].isoformat()

            # Handle messages
            for msg in session_dict.get('messages', []):
                if 'timestamp' in msg:
                    msg['timestamp'] = msg['timestamp'].isoformat()

            # Store with TTL
            self.client.setex(
                key,
                self.ttl,
                json.dumps(session_dict)
            )

        except Exception as e:
            logger.error(f"Failed to set session {session_id}: {e}")
            raise

    def delete(self, session_id: str) -> None:
        try:
            key = f"{self.key_prefix}{session_id}"
            self.client.delete(key)
        except Exception as e:
            logger.error(f"Failed to delete session {session_id}: {e}")

    def exists(self, session_id: str) -> bool:
        try:
            key = f"{self.key_prefix}{session_id}"
            return bool(self.client.exists(key))
        except Exception as e:
            logger.error(f"Failed to check session existence {session_id}: {e}")
            return False

    def cleanup_expired(self) -> int:
        """Redis handles expiration automatically via TTL"""
        return 0

    def get_active_sessions_count(self) -> int:
        """Get count of active sessions"""
        try:
            pattern = f"{self.key_prefix}*"
            return len(list(self.client.scan_iter(match=pattern)))
        except Exception as e:
            logger.error(f"Failed to count active sessions: {e}")
            return 0


class HybridSessionStorage(SessionStorage):
    """
    Hybrid storage that uses Redis if available, falls back to in-memory.
    Useful for development environments where Redis might not be available.
    """

    def __init__(self, redis_url: str | None = None, ttl_minutes: int = 60):
        self.storage: SessionStorage

        try:
            self.storage = RedisSessionStorage(redis_url, ttl_minutes)
            logger.info("Using Redis for session storage")
        except Exception as e:
            logger.warning(f"Redis not available, using in-memory storage: {e}")
            self.storage = InMemorySessionStorage(ttl_minutes)

    def get(self, session_id: str) -> ChatSession | None:
        return self.storage.get(session_id)

    def set(self, session_id: str, session: ChatSession) -> None:
        self.storage.set(session_id, session)

    def delete(self, session_id: str) -> None:
        self.storage.delete(session_id)

    def exists(self, session_id: str) -> bool:
        return self.storage.exists(session_id)

    def cleanup_expired(self) -> int:
        return self.storage.cleanup_expired()


# Factory function
def get_session_storage() -> SessionStorage:
    """
    Get appropriate session storage based on environment.
    """
    if os.getenv('ENVIRONMENT') == 'production':
        return RedisSessionStorage()
    else:
        return HybridSessionStorage()
