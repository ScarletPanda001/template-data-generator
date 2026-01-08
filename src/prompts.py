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
        "Given the refractive index of glass = {n_glass:.2f}, predict the refraction of light through the glass. The refracted ray should extend to the edge of the image.",
        "Given the glass refractive index = {n_glass:.2f}, predict how light refracts when passing through the glass. Extend the refracted ray to the image edge.",
        "Given the refractive index of glass = {n_glass:.2f}, predict the light refraction through the glass surface. The refracted ray must extend all the way to the edge of the image.",
    ],
}


def get_prompt(task_type: str = "default", task_data: dict = None) -> str:
    """
    Select a random prompt for the given task type.
    
    Args:
        task_type: Type of task (key in PROMPTS dict)
        task_data: Task data dictionary containing n_glass
        
    Returns:
        Random prompt string from the specified type with refractive index filled in
    """
    prompts = PROMPTS.get(task_type, PROMPTS["default"])
    prompt_template = random.choice(prompts)
    
    # Fill in the refractive index if task_data is provided
    if task_data and "n_glass" in task_data:
        return prompt_template.format(n_glass=task_data["n_glass"])
    else:
        # Fallback if no task_data provided
        return prompt_template.format(n_glass=1.5)


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
        """Check if the solution correctly predicts the light refraction angle based on Snell's law. Verify that the refracted ray angle matches the calculated value using the given glass refractive index. Ensure the animation shows smooth light propagation from air into glass, with the ray bending at the glass surface according to physical laws. The final visualization should clearly show both the incident and refracted rays with correct angles.""",
        
        """Verify that the solution accurately calculates and visualizes the refraction angle using the provided glass refractive index. Check that the light ray bends correctly at the glass-air interface, with the bending direction and magnitude consistent with Snell's law. The animation should smoothly show light entering the glass and refracting, and the final state should clearly demonstrate the refracted ray propagating in the glass at the correct angle.""",
        
        """Confirm the solution shows the correct refraction angle calculation and visualization. Check that the refracted ray angle is accurate based on the given glass refractive index and incident angle. The animation should demonstrate smooth light propagation and refraction, and the final visualization should clearly show the light ray following physical laws as it enters and propagates through the glass.""",
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
