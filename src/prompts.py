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
        "Given the mirror reflectivity = {reflectivity:.2f}, predict the reflection of light when it hits the mirror.",
        "Given the mirror reflectivity = {reflectivity:.2f}, predict how light reflects when it encounters the mirror.",
        "Given the mirror reflectivity = {reflectivity:.2f}, predict the light reflection from the mirror surface.",
    ],
}


def get_prompt(task_type: str = "default", task_data: dict = None) -> str:
    """
    Select a random prompt for the given task type.
    
    Args:
        task_type: Type of task (key in PROMPTS dict)
        task_data: Task data dictionary containing reflectivity
        
    Returns:
        Random prompt string from the specified type with reflectivity filled in
    """
    prompts = PROMPTS.get(task_type, PROMPTS["default"])
    prompt_template = random.choice(prompts)
    
    # Fill in the reflectivity if task_data is provided
    if task_data and "reflectivity" in task_data:
        base_prompt = prompt_template.format(reflectivity=task_data["reflectivity"])
    else:
        # Fallback if no task_data provided
        base_prompt = prompt_template.format(reflectivity=0.8)
    
    # Add requirement about extending to frame boundary
    return base_prompt + " Your generated light ray should go all the way until the boundary of the frame."


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
        """Check if the solution correctly predicts the light reflection angle based on the law of reflection. Verify that the reflected ray angle matches the incident angle relative to the normal, following the physical law that the angle of incidence equals the angle of reflection. Ensure the animation shows smooth light propagation hitting the mirror and reflecting, with the ray following physical laws. The final visualization should clearly show both the incident and reflected rays with correct angles, and the reflected ray should extend all the way to the boundary of the frame.""",
        
        """Verify that the solution accurately calculates and visualizes the reflection angle using the provided mirror reflectivity. Check that the light ray reflects correctly at the mirror surface, with the reflection angle matching the incident angle relative to the normal. The animation should smoothly show light hitting the mirror and reflecting according to physical laws, and the final state should clearly demonstrate the reflected ray propagating at the correct angle and extending to the frame boundary.""",
        
        """Confirm the solution shows the correct reflection angle calculation and visualization. Check that the reflected ray angle is accurate based on the given mirror reflectivity and incident angle, following the law of reflection. The animation should demonstrate smooth light propagation and reflection, and the final visualization should clearly show the light ray following physical laws as it hits the mirror and reflects, with the reflected ray extending all the way until the boundary of the frame.""",
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
