# Template Data Generator 🎲

A minimal template for creating synthetic reasoning task generators. This repository implements a **bouncing ball trajectory prediction task** where a ball bounces off four walls in a bounded area. Fork this and customize it for your own task (maze, sudoku, rotation, etc.).

---

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/your-org/your-task-generator.git
cd your-task-generator

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .

# 4. Generate tasks
python examples/generate.py --num-samples 50
```

---

## 📁 Structure

```
template-data-generator/
├── core/                    # ✅ KEEP: Standard utilities
│   ├── base_generator.py   # Abstract base class
│   ├── schemas.py          # Pydantic models
│   ├── image_utils.py      # Image helpers
│   ├── video_utils.py      # Video generation
│   └── output_writer.py    # File output
├── src/                     # ⚠️ CUSTOMIZE: Your task logic
│   ├── generator.py        # Your task generator
│   ├── prompts.py          # Your prompt templates
│   └── config.py           # Your configuration
├── examples/
│   └── generate.py         # Entry point
└── data/questions/         # Generated output
```

---

## 📦 Output Format

Every generator produces:

```
data/questions/{domain}_task/{task_id}/
├── first_frame.png          # Initial state (REQUIRED)
├── final_frame.png          # Goal state (or goal.txt)
├── prompt.txt               # Instructions (REQUIRED)
├── rubric.txt               # Evaluation rubric (REQUIRED)
└── ground_truth.mp4         # Solution video (OPTIONAL)
```

---

## 🎨 Customization (3 Files to Modify)

### 1. Update `src/generator.py`

Replace the example chess generator with your task:

```python
from core import BaseGenerator, TaskPair, ImageRenderer

class MazeGenerator(BaseGenerator):
    def __init__(self, config):
        super().__init__(config)
        self.renderer = ImageRenderer(config.image_size)
    
    def generate_task_pair(self, task_id: str) -> TaskPair:
        # 1. Generate your problem
        maze = self.create_maze()
        
        # 2. Solve it
        solution = self.solve_maze(maze)
        
        # 3. Render images
        first_image = self.render_maze(maze)
        final_image = self.render_maze_with_solution(maze, solution)
        
        # 4. Create TaskPair
        return TaskPair(
            task_id=task_id,
            domain=self.config.domain,
            prompt=self.select_prompt(),
            first_image=first_image,
            final_image=final_image,
            ground_truth_video=None  # Optional
        )
```

### 2. Update `src/prompts.py`

Replace chess prompts with yours:

```python
PROMPTS = {
    "default": [
        "Animate a path from start to goal through the maze.",
        "Show the solution route navigating through corridors.",
    ]
}

def get_prompt(task_type: str = "default") -> str:
    prompts = PROMPTS.get(task_type, PROMPTS["default"])
    return random.choice(prompts)
```

### 3. Update `src/config.py`

**All hyperparameters go here** - both general and task-specific:

```python
from core import GenerationConfig
from pydantic import Field

class TaskConfig(GenerationConfig):
    """Your task-specific configuration."""
    # Inherits: num_samples, domain, seed, output_dir, image_size
    
    # Override defaults
    domain: str = Field(default="maze")
    image_size: tuple[int, int] = Field(default=(512, 512))
    
    # Task-specific hyperparameters
    grid_size: int = Field(default=10, description="Maze grid size")
    wall_thickness: int = Field(default=2, description="Wall thickness")
    difficulty: str = Field(default="medium", description="easy/medium/hard")
```

### Step 4: Define Rubrics

Add the `RUBRICS` dictionary in `src/prompts.py`:

```python
RUBRICS = {
    "default": [
        """Check if the solution correctly finds a path from start to goal. Verify that the path reaches the goal and the animation smoothly shows the route through the maze. Ensure the path is reasonably efficient and the visualization clearly shows both the start and end points.""",
        
        """Verify that the solution identifies a valid path through the maze and reaches the goal. The animation should show smooth path progression, and the final visualization should clearly demonstrate the complete route from entrance to exit.""",
        
        """Confirm the solution shows a correct path that reaches the goal. Check that the animation is smooth and the path visualization is clear and understandable throughout.""",
    ],
    
    "easy": [
        """Check if the solution correctly navigates through the simple maze structure. Verify the path reaches the goal and the animation clearly shows the route.""",
    ],
    
    "hard": [
        """Verify that the solution finds an optimal or near-optimal path through the complex maze. Check that the path correctly reaches the goal, the animation is smooth, and the visualization clearly shows the efficient route taken.""",
    ],
}

def get_rubric(task_type: str = "default") -> str:
    """Randomly select a rubric for the given task type"""
    rubrics = RUBRICS.get(task_type, RUBRICS["default"])
    return random.choice(rubrics)
```

**Rubric Format Requirements**:
- ✅ **Use natural language descriptions** that align with human intuition, describing checkpoints like a human evaluator would
- ✅ **Example style**:
  - "Check if the final rotation angle and position match the expected result."
  - "Verify that the solution correctly identifies the checkmating move."
  - "Ensure the animation smoothly transitions from initial to final state."
- ❌ **Do NOT use**:
  - Numbered lists (e.g., "1. 2. 3.")
  - Points or percentages (e.g., "1 point", "40%", "Award 1 point if...")
  - Structured scoring tables
- You can define different rubrics for different difficulty levels
- Rubrics should be objective and actionable, using natural language to describe what needs to be checked

---
**Single entry point:** `python examples/generate.py --num-samples 50`