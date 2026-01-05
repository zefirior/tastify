import asyncio
import logging
from abc import ABC, abstractmethod

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import async_session_maker

logger = logging.getLogger(__name__)


class BaseJob(ABC):
    """
    Base class for background jobs with PostgreSQL advisory lock support.
    
    Advisory locks ensure that only one instance of the job runs at a time,
    even across multiple application instances.
    """

    # Unique lock ID for this job type (override in subclass)
    lock_id: int = 0
    
    # Interval between job executions in seconds (override in subclass)
    interval_seconds: float = 1.0
    
    # Job name for logging (override in subclass)
    job_name: str = "BaseJob"

    async def run(self):
        """Main job loop. Acquires advisory lock and executes the job periodically."""
        logger.info(f"Starting {self.job_name} with interval {self.interval_seconds}s")
        
        while True:
            try:
                async with async_session_maker() as session:
                    # Try to acquire advisory lock (non-blocking)
                    result = await session.execute(
                        text(f"SELECT pg_try_advisory_xact_lock({self.lock_id})")
                    )
                    lock_acquired = result.scalar()

                    if lock_acquired:
                        try:
                            await self.execute(session)
                            await session.commit()
                        except Exception as e:
                            logger.exception(f"Error in {self.job_name}: {e}")
                            await session.rollback()
                    # Lock is automatically released when transaction ends
                    
            except Exception as e:
                logger.exception(f"Error in {self.job_name} loop: {e}")

            await asyncio.sleep(self.interval_seconds)

    @abstractmethod
    async def execute(self, session: AsyncSession):
        """
        Execute the job logic. Override in subclass.
        
        The session is already inside a transaction with an advisory lock held.
        """
        pass

