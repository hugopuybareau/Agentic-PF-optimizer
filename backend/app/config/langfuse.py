import logging
import os
from functools import wraps
from typing import Optional

from langfuse import Langfuse
from langfuse.callback import CallbackHandler
from langfuse.decorators import langfuse_context, observe

logger = logging.getLogger(__name__)


class LangfuseConfig:

    _instance: Optional['LangfuseConfig'] = None
    _langfuse: Langfuse | None = None
    _handler: CallbackHandler | None = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.secret_key = os.getenv("LANGFUSE_SECRET_KEY")
            self.public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
            self.host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
            self.enabled = os.getenv("LANGFUSE_ENABLED", "true").lower() == "true"
            self.initialized = True

            if self.enabled and self.secret_key and self.public_key:
                self._initialize_langfuse()
            else:
                logger.warning("Langfuse is disabled or missing credentials")

    def _initialize_langfuse(self):
        try:
            self._langfuse = Langfuse(
                secret_key=self.secret_key,
                public_key=self.public_key,
                host=self.host
            )

            self._handler = CallbackHandler(
                secret_key=self.secret_key,
                public_key=self.public_key,
                host=self.host
            )

            logger.info(f"Langfuse initialized successfully at {self.host}")
        except Exception as e:
            logger.error(f"Failed to initialize Langfuse: {e}")
            self.enabled = False

    @property
    def langfuse(self) -> Langfuse | None:
        return self._langfuse if self.enabled else None

    @property
    def handler(self) -> CallbackHandler | None:
        return self._handler if self.enabled else None

    def get_callbacks(self) -> list:
        return [self.handler] if self.handler else []

    def trace_function(self, name: str | None = None, **kwargs):
        def decorator(func):
            if not self.enabled:
                return func

            @wraps(func)
            def wrapper(*args, **func_kwargs):
                trace_name = name or func.__name__
                trace = self._langfuse.trace( # type: ignore
                    name=trace_name,
                    **kwargs
                )

                try:
                    with langfuse_context(trace_id=trace.id): # type: ignore
                        result = func(*args, **func_kwargs)
                        trace.update(
                            output=result,
                            metadata={"success": True}
                        )
                        return result
                except Exception as e:
                    trace.update(
                        output={"error": str(e)},
                        metadata={"success": False, "error": str(e)}
                    )
                    raise

            return wrapper
        return decorator

    def observe_method(self, name: str | None = None, **kwargs):
        def decorator(func):
            if not self.enabled:
                return func

            return observe(name=name or func.__name__, **kwargs)(func)

        return decorator


langfuse_config = LangfuseConfig()


def get_langfuse_callbacks():
    return langfuse_config.get_callbacks()


def trace_agent_execution(agent_name: str, **metadata):
    return langfuse_config.trace_function(name=agent_name, **metadata)


# Environment setup helper
def setup_langfuse_env():
    """
    Helper to set up Langfuse environment variables.
    Call this in your main application startup.
    """
    required_vars = {
        "LANGFUSE_SECRET_KEY": "your-secret-key",
        "LANGFUSE_PUBLIC_KEY": "your-public-key",
        "LANGFUSE_HOST": "https://cloud.langfuse.com",
        "LANGFUSE_ENABLED": "true"
    }

    missing_vars = []
    for var, _default in required_vars.items():
        if not os.getenv(var):
            logger.warning(f"Missing environment variable: {var}")
            missing_vars.append(var)

    if missing_vars:
        logger.error(
            f"Missing Langfuse environment variables: {', '.join(missing_vars)}\n"
            f"Please set these in your .env file or environment."
        )
        return False

    return True
