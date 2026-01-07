"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           YOUR TASK CONFIGURATION                             ║
║                                                                               ║
║  CUSTOMIZE THIS FILE to define your task-specific settings.                   ║
║  Inherits common settings from core.GenerationConfig                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from typing import Optional
from pydantic import Field
from core import GenerationConfig


class TaskConfig(GenerationConfig):
    """
    Your task-specific configuration.
    
    CUSTOMIZE THIS CLASS to add your task's hyperparameters.
    
    Inherited from GenerationConfig:
        - num_samples: int          # Number of samples to generate
        - domain: str               # Task domain name
        - difficulty: Optional[str] # Difficulty level
        - random_seed: Optional[int] # For reproducibility
        - output_dir: Path          # Where to save outputs
        - image_size: tuple[int, int] # Image dimensions
    """
    
    # ══════════════════════════════════════════════════════════════════════════
    #  OVERRIDE DEFAULTS
    # ══════════════════════════════════════════════════════════════════════════
    
    domain: str = Field(default="gravity")
    image_size: tuple[int, int] = Field(default=(512, 512))
    
    # ══════════════════════════════════════════════════════════════════════════
    #  VIDEO SETTINGS
    # ══════════════════════════════════════════════════════════════════════════
    
    generate_videos: bool = Field(
        default=True,
        description="Whether to generate ground truth videos"
    )
    
    video_fps: int = Field(
        default=10,
        description="Video frame rate"
    )
    
    # ══════════════════════════════════════════════════════════════════════════
    #  TASK-SPECIFIC SETTINGS
    # ══════════════════════════════════════════════════════════════════════════
    
    # Gravity and physics parameters
    gravity_acceleration: Optional[float] = Field(
        default=None,
        description="Gravity acceleration (m/s²). If None, randomly selected from planet presets."
    )
    
    planet_name: Optional[str] = Field(
        default=None,
        description="Planet name for visual identification. If None, randomly selected."
    )
    
    # Ball parameters
    ball_radius: int = Field(
        default=20,
        description="Ball radius in pixels"
    )
    
    ball_color: tuple[int, int, int] = Field(
        default=(255, 0, 0),
        description="Ball color (RGB)"
    )
    
    ball_initial_x: Optional[float] = Field(
        default=None,
        description="Initial X position (0-1 relative coordinates). If None, randomly generated."
    )
    
    ball_initial_y: Optional[float] = Field(
        default=None,
        description="Initial Y position (0-1 relative coordinates). If None, randomly generated."
    )
    
    ball_initial_vx: float = Field(
        default=0.0,
        description="Initial horizontal velocity (pixels/second)"
    )
    
    ball_initial_vy: float = Field(
        default=0.0,
        description="Initial vertical velocity (pixels/second)"
    )
    
    # Scene parameters
    background_color: tuple[int, int, int] = Field(
        default=(240, 240, 240),
        description="Background color (RGB)"
    )
    
    arrow_color: tuple[int, int, int] = Field(
        default=(0, 0, 255),
        description="Gravity arrow color (RGB)"
    )
    
    arrow_length: int = Field(
        default=60,
        description="Gravity arrow length in pixels"
    )
    
    # Physics simulation parameters
    simulation_duration: float = Field(
        default=2.0,
        description="Simulation duration in seconds"
    )
    
    time_step: float = Field(
        default=0.05,
        description="Time step for physics simulation in seconds"
    )
