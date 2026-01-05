"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           YOUR TASK CONFIGURATION                             ║
║                                                                               ║
║  CUSTOMIZE THIS FILE to define your task-specific settings.                   ║
║  Inherits common settings from core.GenerationConfig                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

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
    
    domain: str = Field(default="bouncing_ball")
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
    
    # Ball properties
    ball_radius: int = Field(default=8, description="Ball radius in pixels")
    ball_color: tuple[int, int, int] = Field(default=(0, 0, 0), description="Ball color (RGB)")
    
    # Trajectory properties
    trajectory_color: tuple[int, int, int] = Field(default=(255, 140, 0), description="Trajectory arrow color (RGB)")
    trajectory_width: int = Field(default=2, description="Trajectory line width")
    
    # Wall properties
    wall_thickness: int = Field(default=3, description="Wall thickness in pixels")
    wall_color: tuple[int, int, int] = Field(default=(100, 100, 100), description="Wall color (RGB)")
    margin: int = Field(default=20, description="Margin from image edges for bounce area")
    
    # Bounce properties
    min_bounces: int = Field(default=2, description="Minimum number of bounces")
    max_bounces: int = Field(default=6, description="Maximum number of bounces")
    initial_speed_min: float = Field(default=50.0, description="Minimum initial speed (pixels per second)")
    initial_speed_max: float = Field(default=150.0, description="Maximum initial speed (pixels per second)")
    bounce_coefficient: float = Field(default=1.0, description="Bounce coefficient (1.0 = perfectly elastic)")
    
    # Animation properties
    animation_duration: float = Field(default=3.0, description="Animation duration in seconds")
