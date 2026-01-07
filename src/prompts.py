"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           YOUR TASK PROMPTS                                   ║
║                                                                               ║
║  CUSTOMIZE THIS FILE to define prompts/instructions for your task.            ║
║  Prompts are selected based on task type and returned to the model.           ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import random


# ══════════════════════════════════════════════════════════════════════════════
#  DEFINE YOUR PROMPTS
# ══════════════════════════════════════════════════════════════════════════════

PROMPTS = {
    "default": [
        "Predict the motion of the object under gravity",
    ],
}


def get_prompt(task_type: str = "default") -> str:
    """
    Select a random prompt for the given task type.
    
    Args:
        task_type: Type of task (key in PROMPTS dict)
        
    Returns:
        Random prompt string from the specified type
    """
    prompts = PROMPTS.get(task_type, PROMPTS["default"])
    return random.choice(prompts)


def get_all_prompts(task_type: str = "default") -> list[str]:
    """Get all prompts for a given task type."""
    return PROMPTS.get(task_type, PROMPTS["default"])


# ══════════════════════════════════════════════════════════════════════════════
#  DEFINE YOUR RUBRICS
# ══════════════════════════════════════════════════════════════════════════════
#
# Rubrics are used to evaluate the quality of model outputs.
# 
# Important format requirements:
#   - Use natural language descriptions that align with human intuition
#   - Do NOT use numbered lists (e.g., "1. 2. 3.")
#   - Do NOT include points or percentages (e.g., "1 point", "40%")
#   - Should describe checkpoints like a human evaluator would
#
# Example style:
#   ✓ "Check if the final rotation angle and position match the expected result."
#   ✓ "Verify that the solution correctly identifies the checkmating move."
#   ✓ "Ensure the animation smoothly transitions from initial to final state."
#
#   ✗ "1. Correctness (4 points): ..."
#   ✗ "Award 1 point if counts match, 0 otherwise."
#   ✗ "Move Accuracy (40%): ..."
#
# You can define different rubrics for different task types.
# ══════════════════════════════════════════════════════════════════════════════

RUBRICS = {
    "default": [
        """Check if the solution correctly predicts the object's motion under gravity. Verify that the final position matches the expected result based on physical laws, and the animation smoothly shows the object moving from the initial position to the final position following gravity. Ensure the motion trajectory follows the correct physics principles with proper acceleration and velocity changes throughout the animation.""",
        
        """Verify that the solution accurately predicts how the object moves under the influence of gravity. Check that the animation demonstrates smooth motion following physical laws, and the final position correctly reflects the object's trajectory. Ensure the visualization clearly shows the object's path and the motion appears natural and physically accurate.""",
        
        """Confirm the solution shows correct prediction of the object's motion under gravity. The animation should demonstrate smooth movement that follows physical principles, and the final position should accurately reflect where the object ends up after being affected by gravity. Check that the motion appears realistic and the trajectory is consistent with gravity's effect.""",
    ],
}


def get_rubric(task_type: str = "default") -> str:
    """
    Select a random rubric for the given task type.
    
    Args:
        task_type: Type of task (key in RUBRICS dict)
        
    Returns:
        Random rubric string from the specified type
    """
    rubrics = RUBRICS.get(task_type, RUBRICS["default"])
    return random.choice(rubrics)
