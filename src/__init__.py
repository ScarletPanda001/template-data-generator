"""
Your custom task implementation.

Files to customize:
    - config.py   : Task-specific configuration (TaskConfig)
    - generator.py: Task generation logic (TaskGenerator)
    - prompts.py  : Task prompts/instructions (get_prompt, get_rubric)
"""

from .config import TaskConfig
from .generator import TaskGenerator
from .prompts import get_prompt, get_rubric

__all__ = ["TaskConfig", "TaskGenerator", "get_prompt", "get_rubric"]
