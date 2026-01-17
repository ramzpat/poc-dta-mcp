---
applyTo: '**/*session*.py'
description: 'Session management best practices for Redis-based session storage in the POC DTA MCP project'
---

# Session Management Instructions

## Your Mission

As GitHub Copilot, you are an expert in session management with deep knowledge of Redis, distributed systems, and secure data handling. Your goal is to help developers implement robust, secure, and scalable session management for privacy-preserving data access.

## Core Principles

1. **Security First**: Always encrypt sensitive data in sessions
2. **Isolation**: Complete data isolation between sessions
3. **Reliability**: Handle failures gracefully with recovery mechanisms
4. **Performance**: Minimize latency with efficient caching
5. **Auditability**: Log all session operations for compliance

## Session Architecture

### Session Structure

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Any
import uuid

@dataclass
class Session:
    """
    Session metadata and state container.
    """
    session_id: str
    created_at: datetime
    expires_at: datetime
    last_accessed: datetime
    status: str  # 'active', 'expired', 'closed'
    data_source: str
    access_level: str  # 'read', 'write'
    user_id: Optional[str]
    metadata: dict[str, Any]
    
    @classmethod
    def create(
        cls,
        data_source: str,
        access_level: str = 'read',
        ttl_seconds: int = 3600,
        user_id: Optional[str] = None,
        **metadata
    ) -> 'Session':
        """Create new session with defaults."""
        now = datetime.utcnow()
        return cls(
            session_id=str(uuid.uuid4()),
            created_at=now,
            expires_at=now + timedelta(seconds=ttl_seconds),
            last_accessed=now,
            status='active',
            data_source=data_source,
            access_level=access_level,
            user_id=user_id,
            metadata=metadata
        )
```

### Session Manager

```python
import redis.asyncio as redis
from typing import Optional
import json
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SessionManager:
    """
    Manage session lifecycle with Redis backend.
    """
    
    def __init__(
        self,
        redis_url: str,
        key_prefix: str = "session:",
        default_ttl: int = 3600
    ):
        """
        Initialize session manager.
        
        Args:
            redis_url: Redis connection URL
            key_prefix: Prefix for Redis keys
            default_ttl: Default session TTL in seconds
        """
        self.redis = redis.from_url(redis_url, decode_responses=True)
        self.key_prefix = key_prefix
        self.default_ttl = default_ttl
    
    def _make_key(self, session_id: str) -> str:
        """Generate Redis key for session."""
        return f"{self.key_prefix}{session_id}"
    
    async def create_session(
        self,
        data_source: str,
        access_level: str = 'read',
        ttl_seconds: Optional[int] = None,
        user_id: Optional[str] = None,
        **metadata
    ) -> Session:
        """
        Create new session and store in Redis.
        
        Args:
            data_source: Data source identifier
            access_level: 'read' or 'write'
            ttl_seconds: Session lifetime (default: self.default_ttl)
            user_id: Optional user identifier
            **metadata: Additional session metadata
            
        Returns:
            Created Session object
            
        Raises:
            redis.RedisError: If Redis operation fails
        """
        ttl = ttl_seconds or self.default_ttl
        
        # Create session object
        session = Session.create(
            data_source=data_source,
            access_level=access_level,
            ttl_seconds=ttl,
            user_id=user_id,
            **metadata
        )
        
        # Store in Redis
        key = self._make_key(session.session_id)
        value = json.dumps(self._serialize_session(session))
        
        try:
            await self.redis.setex(key, ttl, value)
            logger.info(f"Created session {session.session_id} for {data_source}")
            
            # Store in session index
            await self._add_to_index(session)
            
            return session
            
        except redis.RedisError as e:
            logger.error(f"Failed to create session: {e}")
            raise
    
    async def get_session(self, session_id: str) -> Optional[Session]:
        """
        Retrieve session from Redis.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session object or None if not found/expired
        """
        key = self._make_key(session_id)
        
        try:
            value = await self.redis.get(key)
            
            if not value:
                logger.warning(f"Session {session_id} not found or expired")
                return None
            
            session_data = json.loads(value)
            session = self._deserialize_session(session_data)
            
            # Update last accessed time
            session.last_accessed = datetime.utcnow()
            await self._update_session(session)
            
            return session
            
        except redis.RedisError as e:
            logger.error(f"Failed to retrieve session: {e}")
            return None
    
    async def update_session(
        self,
        session_id: str,
        **updates
    ) -> bool:
        """
        Update session metadata.
        
        Args:
            session_id: Session identifier
            **updates: Fields to update
            
        Returns:
            True if successful, False otherwise
        """
        session = await self.get_session(session_id)
        
        if not session:
            return False
        
        # Update fields
        for key, value in updates.items():
            if hasattr(session, key):
                setattr(session, key, value)
            else:
                session.metadata[key] = value
        
        return await self._update_session(session)
    
    async def _update_session(self, session: Session) -> bool:
        """Internal method to update session in Redis."""
        key = self._make_key(session.session_id)
        value = json.dumps(self._serialize_session(session))
        
        try:
            # Get remaining TTL
            ttl = await self.redis.ttl(key)
            if ttl <= 0:
                ttl = self.default_ttl
            
            await self.redis.setex(key, ttl, value)
            return True
            
        except redis.RedisError as e:
            logger.error(f"Failed to update session: {e}")
            return False
    
    async def close_session(
        self,
        session_id: str,
        archive: bool = True
    ) -> bool:
        """
        Close session and optionally archive data.
        
        Args:
            session_id: Session identifier
            archive: Whether to archive session data
            
        Returns:
            True if successful, False otherwise
        """
        session = await self.get_session(session_id)
        
        if not session:
            return False
        
        try:
            # Archive if requested
            if archive:
                await self._archive_session(session)
            
            # Remove from Redis
            key = self._make_key(session_id)
            await self.redis.delete(key)
            
            # Remove from index
            await self._remove_from_index(session)
            
            logger.info(f"Closed session {session_id}")
            return True
            
        except redis.RedisError as e:
            logger.error(f"Failed to close session: {e}")
            return False
    
    async def extend_session(
        self,
        session_id: str,
        additional_seconds: int
    ) -> bool:
        """
        Extend session TTL.
        
        Args:
            session_id: Session identifier
            additional_seconds: Seconds to add to TTL
            
        Returns:
            True if successful, False otherwise
        """
        key = self._make_key(session_id)
        
        try:
            current_ttl = await self.redis.ttl(key)
            
            if current_ttl <= 0:
                logger.warning(f"Session {session_id} already expired")
                return False
            
            new_ttl = current_ttl + additional_seconds
            await self.redis.expire(key, new_ttl)
            
            logger.info(f"Extended session {session_id} by {additional_seconds}s")
            return True
            
        except redis.RedisError as e:
            logger.error(f"Failed to extend session: {e}")
            return False
    
    async def list_active_sessions(
        self,
        user_id: Optional[str] = None
    ) -> list[Session]:
        """
        List all active sessions, optionally filtered by user.
        
        Args:
            user_id: Optional user filter
            
        Returns:
            List of active Session objects
        """
        try:
            pattern = f"{self.key_prefix}*"
            keys = []
            
            async for key in self.redis.scan_iter(match=pattern):
                keys.append(key)
            
            sessions = []
            for key in keys:
                value = await self.redis.get(key)
                if value:
                    session_data = json.loads(value)
                    session = self._deserialize_session(session_data)
                    
                    # Filter by user if specified
                    if user_id is None or session.user_id == user_id:
                        sessions.append(session)
            
            return sessions
            
        except redis.RedisError as e:
            logger.error(f"Failed to list sessions: {e}")
            return []
    
    async def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions (Redis handles TTL, but this archives).
        
        Returns:
            Number of sessions cleaned up
        """
        count = 0
        sessions = await self.list_active_sessions()
        
        now = datetime.utcnow()
        for session in sessions:
            if now > session.expires_at:
                await self.close_session(session.session_id, archive=True)
                count += 1
        
        logger.info(f"Cleaned up {count} expired sessions")
        return count
    
    async def _add_to_index(self, session: Session):
        """Add session to searchable index."""
        index_key = f"{self.key_prefix}index:{session.user_id or 'anonymous'}"
        await self.redis.sadd(index_key, session.session_id)
    
    async def _remove_from_index(self, session: Session):
        """Remove session from searchable index."""
        index_key = f"{self.key_prefix}index:{session.user_id or 'anonymous'}"
        await self.redis.srem(index_key, session.session_id)
    
    async def _archive_session(self, session: Session):
        """Archive session data to persistent storage."""
        # TODO: Implement persistent archival (e.g., to PostgreSQL)
        archive_key = f"{self.key_prefix}archive:{session.session_id}"
        value = json.dumps(self._serialize_session(session))
        
        # Store archived session (no TTL)
        await self.redis.set(archive_key, value)
        logger.info(f"Archived session {session.session_id}")
    
    @staticmethod
    def _serialize_session(session: Session) -> dict:
        """Convert Session to dict for JSON serialization."""
        return {
            'session_id': session.session_id,
            'created_at': session.created_at.isoformat(),
            'expires_at': session.expires_at.isoformat(),
            'last_accessed': session.last_accessed.isoformat(),
            'status': session.status,
            'data_source': session.data_source,
            'access_level': session.access_level,
            'user_id': session.user_id,
            'metadata': session.metadata
        }
    
    @staticmethod
    def _deserialize_session(data: dict) -> Session:
        """Convert dict to Session object."""
        return Session(
            session_id=data['session_id'],
            created_at=datetime.fromisoformat(data['created_at']),
            expires_at=datetime.fromisoformat(data['expires_at']),
            last_accessed=datetime.fromisoformat(data['last_accessed']),
            status=data['status'],
            data_source=data['data_source'],
            access_level=data['access_level'],
            user_id=data.get('user_id'),
            metadata=data.get('metadata', {})
        )
```

## Session Data Storage

### Store Data in Session

```python
class SessionDataStore:
    """
    Store and retrieve data within session context.
    """
    
    def __init__(self, redis_client: redis.Redis, session_id: str):
        self.redis = redis_client
        self.session_id = session_id
        self.data_prefix = f"session:{session_id}:data:"
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """
        Store data in session context.
        
        Args:
            key: Data key
            value: Data value (will be JSON serialized)
            ttl: Optional TTL (inherits session TTL if None)
        """
        full_key = f"{self.data_prefix}{key}"
        serialized = json.dumps(value)
        
        if ttl:
            await self.redis.setex(full_key, ttl, serialized)
        else:
            await self.redis.set(full_key, serialized)
        
        logger.debug(f"Stored {key} in session {self.session_id}")
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Retrieve data from session context.
        
        Args:
            key: Data key
            
        Returns:
            Deserialized value or None
        """
        full_key = f"{self.data_prefix}{key}"
        value = await self.redis.get(full_key)
        
        if value:
            return json.loads(value)
        return None
    
    async def delete(self, key: str):
        """Delete data from session context."""
        full_key = f"{self.data_prefix}{key}"
        await self.redis.delete(full_key)
    
    async def list_keys(self) -> list[str]:
        """List all keys in session context."""
        pattern = f"{self.data_prefix}*"
        keys = []
        
        async for key in self.redis.scan_iter(match=pattern):
            # Strip prefix to get original key
            original_key = key.replace(self.data_prefix, '')
            keys.append(original_key)
        
        return keys
    
    async def clear_all(self):
        """Clear all data from session context."""
        pattern = f"{self.data_prefix}*"
        keys = []
        
        async for key in self.redis.scan_iter(match=pattern):
            keys.append(key)
        
        if keys:
            await self.redis.delete(*keys)
            logger.info(f"Cleared {len(keys)} keys from session {self.session_id}")
```

## Security Best Practices

### Encrypt Sensitive Data

```python
from cryptography.fernet import Fernet
import base64

class SecureSessionData:
    """
    Encrypt and decrypt sensitive session data.
    """
    
    def __init__(self, encryption_key: bytes):
        """
        Initialize with encryption key.
        
        Args:
            encryption_key: 32-byte key for Fernet encryption
        """
        self.cipher = Fernet(encryption_key)
    
    def encrypt(self, data: str) -> str:
        """Encrypt data for storage."""
        encrypted = self.cipher.encrypt(data.encode())
        return base64.b64encode(encrypted).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt data from storage."""
        encrypted_bytes = base64.b64decode(encrypted_data.encode())
        decrypted = self.cipher.decrypt(encrypted_bytes)
        return decrypted.decode()
    
    def encrypt_dict(self, data: dict) -> str:
        """Encrypt dict as JSON."""
        json_str = json.dumps(data)
        return self.encrypt(json_str)
    
    def decrypt_dict(self, encrypted_data: str) -> dict:
        """Decrypt JSON string to dict."""
        json_str = self.decrypt(encrypted_data)
        return json.loads(json_str)
```

### Access Control

```python
from enum import Enum

class AccessLevel(Enum):
    READ = 'read'
    WRITE = 'write'
    ADMIN = 'admin'

class SessionAccessControl:
    """
    Enforce access control for session operations.
    """
    
    @staticmethod
    def can_read(session: Session, user_id: str) -> bool:
        """Check if user can read session data."""
        if session.user_id != user_id:
            return False
        return session.access_level in [AccessLevel.READ.value, AccessLevel.WRITE.value, AccessLevel.ADMIN.value]
    
    @staticmethod
    def can_write(session: Session, user_id: str) -> bool:
        """Check if user can write session data."""
        if session.user_id != user_id:
            return False
        return session.access_level in [AccessLevel.WRITE.value, AccessLevel.ADMIN.value]
    
    @staticmethod
    def can_admin(session: Session, user_id: str) -> bool:
        """Check if user has admin access to session."""
        if session.user_id != user_id:
            return False
        return session.access_level == AccessLevel.ADMIN.value
```

## Error Handling and Recovery

### Session Recovery

```python
class SessionRecovery:
    """
    Handle session failures and recovery.
    """
    
    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager
    
    async def recover_session(
        self,
        session_id: str,
        max_retries: int = 3
    ) -> Optional[Session]:
        """
        Attempt to recover a failed session.
        
        Args:
            session_id: Session to recover
            max_retries: Maximum recovery attempts
            
        Returns:
            Recovered Session or None
        """
        for attempt in range(max_retries):
            try:
                session = await self.session_manager.get_session(session_id)
                
                if session:
                    # Extend session to ensure it doesn't expire during recovery
                    await self.session_manager.extend_session(session_id, 300)
                    logger.info(f"Recovered session {session_id} on attempt {attempt + 1}")
                    return session
                
            except Exception as e:
                logger.error(f"Recovery attempt {attempt + 1} failed: {e}")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        logger.error(f"Failed to recover session {session_id} after {max_retries} attempts")
        return None
```

## Monitoring and Metrics

### Session Metrics

```python
from dataclasses import dataclass
from typing import Dict

@dataclass
class SessionMetrics:
    """Container for session metrics."""
    total_sessions: int
    active_sessions: int
    expired_sessions: int
    avg_session_duration_seconds: float
    sessions_by_access_level: Dict[str, int]
    sessions_by_data_source: Dict[str, int]

class SessionMetricsCollector:
    """
    Collect and report session metrics.
    """
    
    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager
    
    async def collect_metrics(self) -> SessionMetrics:
        """
        Collect current session metrics.
        
        Returns:
            SessionMetrics object
        """
        sessions = await self.session_manager.list_active_sessions()
        
        now = datetime.utcnow()
        active = [s for s in sessions if now <= s.expires_at]
        expired = [s for s in sessions if now > s.expires_at]
        
        durations = [
            (s.last_accessed - s.created_at).total_seconds()
            for s in sessions
        ]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        by_access_level = {}
        by_data_source = {}
        
        for session in sessions:
            by_access_level[session.access_level] = by_access_level.get(session.access_level, 0) + 1
            by_data_source[session.data_source] = by_data_source.get(session.data_source, 0) + 1
        
        return SessionMetrics(
            total_sessions=len(sessions),
            active_sessions=len(active),
            expired_sessions=len(expired),
            avg_session_duration_seconds=avg_duration,
            sessions_by_access_level=by_access_level,
            sessions_by_data_source=by_data_source
        )
```

## Code Review Checklist

When reviewing session management code, check for:

- [ ] Session IDs are UUIDs (not sequential or predictable)
- [ ] Sensitive data is encrypted in sessions
- [ ] TTLs are set on all session data
- [ ] Access control is enforced before operations
- [ ] All Redis operations have error handling
- [ ] Sessions are properly closed and cleaned up
- [ ] Audit logging for all session operations
- [ ] No session data in application logs
- [ ] Connection pooling is used for Redis
- [ ] Expired sessions are archived before deletion
- [ ] Race conditions handled (use Redis transactions/Lua)
- [ ] Session recovery mechanisms in place

## Common Pitfalls to Avoid

1. **Predictable Session IDs**: Always use UUID v4
2. **No TTL**: Always set expiration on session data
3. **Unencrypted PII**: Encrypt all sensitive data
4. **Missing Access Control**: Validate user permissions
5. **No Cleanup**: Implement session cleanup and archival
6. **Blocking Operations**: Use async Redis client
7. **No Monitoring**: Track session metrics and anomalies
8. **Single Point of Failure**: Use Redis cluster for production

---

**Remember**: Session management is critical for security and privacy. Always encrypt sensitive data, enforce access controls, and implement comprehensive audit logging.
