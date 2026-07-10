import asyncio
import logging

from app.core.config import get_settings
from app.core.logging import setup_logging
from app.database.seed import seed_demo_data
from app.database.session import get_session_factory

logger = logging.getLogger(__name__)


async def run_seed() -> None:
    settings = get_settings()
    setup_logging(settings)
    session_factory = get_session_factory(settings)
    async with session_factory() as session:
        await seed_demo_data(session)
    logger.info("Seed command completed")


def main() -> None:
    asyncio.run(run_seed())


if __name__ == "__main__":
    main()
