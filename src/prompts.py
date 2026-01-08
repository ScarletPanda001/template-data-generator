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
        "Two circular balls with different colors are positioned at different locations. Animate the balls moving toward each other at the same speed until they completely merge as one. When the balls overlap, the overlapping region should display the additive color mixture of their original colors. The animation should stop after the two balls completely merge into a single ball at the midpoint between their initial positions.",
        "Two colored circular balls start at different positions. They move toward each other at equal speeds until they fully overlap and merge into one. The overlapping region during movement and the final merged ball should show the additive color mixture of the two original ball colors. Stop the animation when the balls have completely merged at the midpoint.",
        "Animate two circular balls with distinct colors moving toward each other at the same velocity. The balls should continue moving until they completely merge as one ball. During overlap and in the final merged state, use additive color mixing to combine the original colors. The animation stops when both balls have fully merged at the midpoint between their starting positions.",
        "Two balls of different colors are placed at separate locations. Show them moving toward each other at identical speeds. When they overlap, the overlapping area should display the additive mixture of their colors. Continue the animation until the balls completely merge into a single ball at the midpoint, then stop.",
    ],
}


def get_prompt(task_type: str = "default", task_data: dict = None) -> str:
    """
    Select a random prompt for the given task type.
    
    Args:
        task_type: Type of task (key in PROMPTS dict)
        task_data: Task data dictionary (not used for color mixing prompts)
        
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
        """Check if the solution correctly animates both balls moving toward each other at the same speed. Verify that the balls move in straight lines toward each other and meet at the midpoint between their initial positions. Ensure the animation shows smooth motion throughout. When the balls overlap during movement, check that only the overlapping region displays the additive color mixture while non-overlapping parts retain their original colors. Verify that the animation stops after the two balls completely merge into a single ball at the midpoint, and that the final merged ball shows the correct additive color mixture of the two original colors.""",
        
        """Verify that the solution shows both balls moving at equal speeds toward each other until they completely merge. Check that the motion is smooth and linear, with both balls traveling the same distance at the same rate. Confirm that during partial overlap, the overlapping region correctly displays the additive color mixture while maintaining the original colors in non-overlapping areas. Ensure the animation continues until the balls fully merge into one ball at the midpoint, then stops. Check that the final merged ball at the midpoint position shows the correct normalized additive color mixture of the original two colors.""",
        
        """Confirm the solution animates the two balls moving toward each other at the same velocity. Check that the balls follow straight paths and meet at the center point between their starting positions. Verify that the animation smoothly shows the balls approaching, with partial overlap correctly displaying additive color mixing only in the overlapping region. Ensure the animation continues until both balls completely merge as one, then stops. Check that the final merged ball at the midpoint displays the correct additive color mixture, where the RGB values of the original colors are added together and normalized if they exceed 255.""",
        
        """Check that both balls move toward each other at identical speeds in straight lines. Verify the animation shows smooth progression from initial separation through partial overlap to complete merging. During partial overlap, ensure only the overlapping region shows the additive color mixture while maintaining original ball colors elsewhere. Confirm the animation stops after the balls completely merge into a single ball at the midpoint. Verify the final merged ball displays the correct normalized additive color mixture, where the red, green, and blue components of the original colors are added and proportionally scaled if the sum exceeds 255.""",
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
