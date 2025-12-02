"""Python 3.13 executor implementation."""

from __future__ import annotations

import ast
import asyncio
import sys
import time
from typing import Any

from app.core.config import settings

from .base import BaseExecutor, ExecutionRequest, ExecutionResult


class Python313Executor(BaseExecutor):
    """Execute Python snippets inside the host interpreter sandbox."""

    language = "python3.13"
    docker_image = settings.PYTHON_EXECUTOR_IMAGE
    default_timeout = settings.EXECUTION_TIMEOUT
    default_memory = settings.EXECUTION_MEMORY_LIMIT

    _ALLOWED_MODULES = {
        "math",
        "itertools",
        "collections",
        "functools",
        "heapq",
        "bisect",
        "re",
        "json",
        "datetime",
        "statistics",
        "random",
        "decimal",
        "fractions",
        "typing",
    }

    def __init__(self) -> None:
        self._python_binary = sys.executable

    async def validate_code(self, code: str) -> tuple[bool, str | None]:
        try:
            tree = ast.parse(code)
        except SyntaxError as exc:  # pragma: no cover - ast.parse reports error context
            return False, f"syntax error: {exc}"

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root = alias.name.split(".")[0]
                    if root not in self._ALLOWED_MODULES:
                        return False, f"import '{alias.name}' is not allowed"
            elif isinstance(node, ast.ImportFrom):
                if node.module is None:
                    return False, "relative imports are not allowed"
                root = node.module.split(".")[0]
                if root not in self._ALLOWED_MODULES:
                    return False, f"import '{node.module}' is not allowed"
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == "__import__":
                    return False, "__import__ is not allowed"
        return True, None

    def get_resource_limits(self) -> dict[str, Any]:
        return {"timeout": self.default_timeout, "memory_limit": self.default_memory}

    async def execute(self, request: ExecutionRequest) -> ExecutionResult:
        timeout = request.timeout or self.default_timeout
        start = time.perf_counter()

        process = await asyncio.create_subprocess_exec(
            self._python_binary,
            "-I",
            "-c",
            request.code,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        try:
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                process.communicate(
                    input=request.stdin.encode() if request.stdin is not None else None
                ),
                timeout=timeout,
            )
            exit_code = await process.wait()
            error = None
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
            stdout_bytes, stderr_bytes = b"", b""
            exit_code = -1
            error = "execution timed out"

        execution_time_ms = int((time.perf_counter() - start) * 1000)

        return ExecutionResult(
            stdout=stdout_bytes.decode(),
            stderr=stderr_bytes.decode(),
            exit_code=exit_code,
            execution_time_ms=execution_time_ms,
            memory_used_kb=0,
            error=error,
        )
