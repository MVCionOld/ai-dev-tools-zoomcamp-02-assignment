from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


class ExecutionRequest(BaseModel):
    code: str
    stdin: str | None = None
    timeout: int = 10
    memory_limit: str = "256m"


class ExecutionResult(BaseModel):
    stdout: str
    stderr: str
    exit_code: int
    execution_time_ms: int
    memory_used_kb: int
    error: str | None = None


class BaseExecutor(ABC):
    """Abstract base class for all code executors."""

    language: str
    docker_image: str
    default_timeout: int = 10
    default_memory: str = "256m"

    @abstractmethod
    async def execute(self, request: ExecutionRequest) -> ExecutionResult:
        """Run the provided code snippet in an isolated environment."""
        raise NotImplementedError

    @abstractmethod
    async def validate_code(self, code: str) -> tuple[bool, str | None]:
        """Perform static validations before execution (syntax, forbidden imports, etc.)."""
        raise NotImplementedError

    @abstractmethod
    def get_resource_limits(self) -> dict[str, Any]:
        """Expose the resource limits configured for the executor."""
        raise NotImplementedError
