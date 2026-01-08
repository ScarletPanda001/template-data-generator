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
        "Predict and generate the ball's multiple bounce trajectory. Animate the ball moving from its initial position, following the direction indicated by the arrow, and bouncing off the four walls to show the complete path.",
        "Show the complete bouncing trajectory of the ball. Starting from the initial position and direction arrow, animate how the ball bounces multiple times off the four walls, displaying the full path it will take.",
        "Generate the ball's bounce path. Based on the initial position and velocity arrow, animate the ball's movement as it bounces off the four boundaries, revealing the complete trajectory.",
    ],
    
    "simple": [
        "Show a simple bounce trajectory with 2-3 bounces. The ball should move smoothly from start, bounce off the walls, and display a clear path.",
        "Animate a straightforward bounce path. The ball starts at the initial position, follows the arrow direction, and bounces 2-3 times off the walls.",
    ],
    
    "medium": [
        "Generate a medium-complexity bounce trajectory with 4-5 bounces. Show the ball's path as it bounces multiple times off different walls.",
        "Animate a moderate bounce sequence. The ball should demonstrate 4-5 bounces, creating an interesting path across the bounded area.",
    ],
    
    "complex": [
        "Create a complex bounce trajectory with 6 or more bounces. Show the intricate path the ball takes as it bounces repeatedly off all four walls.",
        "Generate an elaborate bounce pattern. The ball should bounce many times, creating a complex trajectory that demonstrates multiple wall interactions.",
    ],
}


def get_prompt(task_type: str = "default", num_bounces: int = None) -> str:
    """
    Select a random prompt for the given task type.
    
    Args:
        task_type: Type of task (key in PROMPTS dict)
        num_bounces: Number of bounces (will be included in prompt if provided)
        
    Returns:
        Random prompt string from the specified type, with bounce count if provided
    """
    prompts = PROMPTS.get(task_type, PROMPTS["default"])
    base_prompt = random.choice(prompts)
    
    # Add explicit bounce count to prompt if provided
    if num_bounces is not None:
        if num_bounces == 1:
            bounce_text = f"Stop after the {num_bounces}st bounce"
        elif num_bounces == 2:
            bounce_text = f"Stop after the {num_bounces}nd bounce"
        elif num_bounces == 3:
            bounce_text = f"Stop after the {num_bounces}rd bounce"
        else:
            bounce_text = f"Stop after the {num_bounces}th bounce"
        
        # Append bounce count instruction to the prompt
        base_prompt = f"{base_prompt} {bounce_text}."
    
    return base_prompt


def get_all_prompts(task_type: str = "default") -> list[str]:
    """Get all prompts for a given task type."""
    return PROMPTS.get(task_type, PROMPTS["default"])


# ══════════════════════════════════════════════════════════════════════════════
#  DEFINE YOUR RUBRICS
# ══════════════════════════════════════════════════════════════════════════════

RUBRICS = {
    "default": [
        """Check if the solution correctly predicts and generates the ball's bounce trajectory. Verify that the ball follows the initial velocity direction, bounces off the walls at the correct angles, and the animation smoothly shows the complete path. Ensure the trajectory matches the expected number of bounces and the final position is accurate.""",
        
        """Verify that the solution accurately shows the ball's bouncing path. Check that the ball starts from the correct initial position, follows the velocity arrow direction, bounces off all walls correctly, and the animation demonstrates a smooth trajectory that matches the expected bounce pattern.""",
        
        """Confirm the solution displays a correct bounce trajectory. Check that the ball moves smoothly from start, bounces at the right locations on each wall, maintains proper physics (angle of reflection equals angle of incidence), and the visualization clearly shows the complete path with all bounces.""",
    ],
    
    "simple": [
        """Check if the solution correctly shows a simple bounce trajectory with 2-3 bounces. Verify that the ball follows the initial direction, bounces off the walls correctly, and the animation clearly displays the path with smooth motion.""",
    ],
    
    "medium": [
        """Verify that the solution accurately demonstrates a medium-complexity bounce trajectory with 4-5 bounces. Check that the ball follows the correct path, bounces off different walls at appropriate angles, and the animation smoothly shows the complete trajectory.""",
    ],
    
    "complex": [
        """Verify that the solution correctly generates a complex bounce trajectory with 6 or more bounces. Check that the ball follows the intricate path, bounces off all four walls multiple times at correct angles, the animation is smooth throughout, and the final position matches the expected result after all bounces.""",
    ],
}


def get_rubric(task_type: str = "default") -> str:
    """
    Randomly select a rubric for the given task type.
    
    Args:
        task_type: Type of task (key in RUBRICS dict)
        
    Returns:
        Random rubric string from the specified type
    """
    rubrics = RUBRICS.get(task_type, RUBRICS["default"])
    return random.choice(rubrics)
