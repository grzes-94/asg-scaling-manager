import structlog
import os

_logger = None


def get_logger():
    global _logger
    if _logger is None:
        # Get log level from environment or default to INFO
        log_level = os.getenv("ASG_SCALING_MANAGER_LOG_LEVEL", "INFO").upper()
        
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.dev.ConsoleRenderer(colors=True),
            ],
            wrapper_class=structlog.stdlib.BoundLogger,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )
        _logger = structlog.get_logger("asg-scaling-manager")
        _logger.setLevel(log_level)
    return _logger


def set_log_level(level: str):
    """Set the log level for the application."""
    global _logger
    if _logger is not None:
        _logger.setLevel(level.upper())
    else:
        os.environ["ASG_SCALING_MANAGER_LOG_LEVEL"] = level.upper()


