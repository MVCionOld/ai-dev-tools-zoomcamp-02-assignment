"""Registry for mapping language identifiers to executor implementations."""

from __future__ import annotations

from typing import Type

from .base import BaseExecutor
from .python_executor import Python313Executor


class ExecutorRegistry:
    """Plugin registry for code executors."""

    _executors: dict[str, Type[BaseExecutor]] = {}

    @classmethod
    def register(cls, executor_class: Type[BaseExecutor]):
        """Register a new executor"""
        cls._executors[executor_class.language] = executor_class

    @classmethod
    def get_executor(cls, language: str) -> BaseExecutor:
        """Get executor instance for language"""
        if language not in cls._executors:
            raise ValueError(f"Unsupported language: {language}")
        return cls._executors[language]()

    @classmethod
    def list_supported_languages(cls) -> list[str]:
        """List all registered languages"""
        return list(cls._executors.keys())


# Auto-register Python executor
ExecutorRegistry.register(Python313Executor)
