"""
Main application entry point.
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional

from loguru import logger

from roblox_garden.config.settings import Settings
from roblox_garden.core.application import RobloxGardenApp


def setup_logging(settings: Settings) -> None:
    """Configure logging with loguru."""
    logger.remove()  # Remove default handler
    
    # Console logging
    logger.add(
        sys.stderr,
        level=settings.log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
               "<level>{message}</level>",
        colorize=True,
    )
    
    # File logging
    if settings.log_file:
        log_path = Path(settings.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.add(
            settings.log_file,
            level=settings.log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | "
                   "{name}:{function}:{line} - {message}",
            rotation="10 MB",
            retention="1 week",
            compression="gz",
        )


async def main() -> None:
    """Main application entry point."""
    try:
        # Load configuration
        settings = Settings()
        
        # Setup logging
        setup_logging(settings)
        
        logger.info("Starting Roblox Garden Parser...")
        logger.info(f"Configuration loaded: {settings.model_dump_json(indent=2)}")
        
        # Create and run application
        app = RobloxGardenApp(settings)
        await app.run()
        
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
        raise
    finally:
        logger.info("Application shutdown complete")


def cli() -> None:
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Roblox Garden WebSocket Parser")
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    
    args = parser.parse_args()
    
    if args.debug:
        import os
        os.environ["LOG_LEVEL"] = "DEBUG"
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nApplication stopped by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli()
