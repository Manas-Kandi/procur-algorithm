"""Database session management and connection pooling."""

from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import Pool

from .base import Base
from .config import get_database_config

logger = logging.getLogger(__name__)


class DatabaseSession:
    """Database session manager with connection pooling."""
    
    def __init__(self) -> None:
        """Initialize database session manager."""
        self.config = get_database_config()
        self._engine: Engine | None = None
        self._session_factory: sessionmaker | None = None
    
    @property
    def engine(self) -> Engine:
        """Get or create SQLAlchemy engine."""
        if self._engine is None:
            self._engine = create_engine(
                self.config.database_url,
                **self.config.get_engine_kwargs(),
            )
            self._setup_listeners(self._engine)
            logger.info(
                f"Database engine created: {self.config.host}:{self.config.port}/{self.config.database}"
            )
        return self._engine
    
    @property
    def session_factory(self) -> sessionmaker:
        """Get or create session factory."""
        if self._session_factory is None:
            self._session_factory = sessionmaker(
                bind=self.engine,
                autocommit=False,
                autoflush=False,
                expire_on_commit=False,
            )
        return self._session_factory
    
    def _setup_listeners(self, engine: Engine) -> None:
        """Set up SQLAlchemy event listeners."""
        
        @event.listens_for(engine, "connect")
        def receive_connect(dbapi_conn, connection_record):
            """Handle new database connections."""
            logger.debug("New database connection established")
        
        @event.listens_for(engine, "checkout")
        def receive_checkout(dbapi_conn, connection_record, connection_proxy):
            """Handle connection checkout from pool."""
            logger.debug("Connection checked out from pool")
        
        @event.listens_for(engine, "checkin")
        def receive_checkin(dbapi_conn, connection_record):
            """Handle connection checkin to pool."""
            logger.debug("Connection checked in to pool")
        
        @event.listens_for(Pool, "connect")
        def set_postgresql_pragma(dbapi_conn, connection_record):
            """Set PostgreSQL connection parameters."""
            cursor = dbapi_conn.cursor()
            cursor.execute("SET TIME ZONE 'UTC'")
            cursor.close()
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Get a database session with automatic cleanup.
        
        Usage:
            with db.get_session() as session:
                session.query(Model).all()
        """
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def create_all_tables(self) -> None:
        """Create all database tables."""
        Base.metadata.create_all(self.engine)
        logger.info("All database tables created")
    
    def drop_all_tables(self) -> None:
        """Drop all database tables. USE WITH CAUTION!"""
        Base.metadata.drop_all(self.engine)
        logger.warning("All database tables dropped")
    
    def close(self) -> None:
        """Close database connections and dispose engine."""
        if self._engine is not None:
            self._engine.dispose()
            logger.info("Database engine disposed")
            self._engine = None
            self._session_factory = None


# Global database session instance
_db_session: DatabaseSession | None = None


def get_db_session() -> DatabaseSession:
    """Get global database session instance."""
    global _db_session
    if _db_session is None:
        _db_session = DatabaseSession()
    return _db_session


def get_session() -> Generator[Session, None, None]:
    """
    Dependency injection helper for getting database sessions.
    
    Usage with FastAPI:
        @app.get("/items")
        def get_items(session: Session = Depends(get_session)):
            return session.query(Item).all()
    
    Usage as context manager:
        with get_session() as session:
            session.query(Item).all()
    """
    db = get_db_session()
    session = db.session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db(create_tables: bool = True) -> DatabaseSession:
    """
    Initialize database connection and optionally create tables.
    
    Args:
        create_tables: Whether to create all tables
    
    Returns:
        DatabaseSession instance
    """
    db = get_db_session()
    if create_tables:
        db.create_all_tables()
    return db
