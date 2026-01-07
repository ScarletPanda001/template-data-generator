"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           YOUR TASK GENERATOR                                 ║
║                                                                               ║
║  CUSTOMIZE THIS FILE to implement your data generation logic.                 ║
║  Replace the example implementation with your own task.                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import random
import tempfile
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from core import BaseGenerator, TaskPair, ImageRenderer
from core.video_utils import VideoGenerator
from .config import TaskConfig
from .prompts import get_prompt, get_rubric


# Planet presets with gravity acceleration (m/s²)
PLANET_PRESETS = {
    "Earth": 9.8,
    "Moon": 1.6,
    "Mars": 3.7,
    "Jupiter": 24.8,
    "Venus": 8.9,
    "Mercury": 3.7,
}


class TaskGenerator(BaseGenerator):
    """
    Your custom task generator.
    
    IMPLEMENT THIS CLASS for your specific task.
    
    Required:
        - generate_task_pair(task_id) -> TaskPair
    
    The base class provides:
        - self.config: Your TaskConfig instance
        - generate_dataset(): Loops and calls generate_task_pair() for each sample
    """
    
    def __init__(self, config: TaskConfig):
        super().__init__(config)
        self.renderer = ImageRenderer(image_size=config.image_size)
        
        # Initialize video generator if enabled (using mp4 format)
        self.video_generator = None
        if config.generate_videos and VideoGenerator.is_available():
            self.video_generator = VideoGenerator(fps=config.video_fps, output_format="mp4")
    
    def generate_task_pair(self, task_id: str) -> TaskPair:
        """Generate one task pair."""
        
        # Generate task data
        task_data = self._generate_task_data()
        
        # Render images
        first_image = self._render_initial_state(task_data)
        final_image = self._render_final_state(task_data)
        
        # Generate video (optional)
        video_path = None
        if self.config.generate_videos and self.video_generator:
            video_path = self._generate_video(first_image, final_image, task_id, task_data)
        
        # Select prompt and rubric
        task_type = task_data.get("type", "default")
        prompt = get_prompt(task_type)
        rubric = get_rubric(task_type)
        
        return TaskPair(
            task_id=task_id,
            domain=self.config.domain,
            prompt=prompt,
            rubric=rubric,
            first_image=first_image,
            final_image=final_image,
            ground_truth_video=video_path
        )
    
    # ══════════════════════════════════════════════════════════════════════════
    #  TASK-SPECIFIC METHODS
    # ══════════════════════════════════════════════════════════════════════════
    
    def _generate_task_data(self) -> dict:
        """Generate gravity motion task data."""
        # Select planet and gravity
        if self.config.planet_name is not None:
            planet_name = self.config.planet_name
            gravity = self.config.gravity_acceleration or PLANET_PRESETS.get(planet_name, 9.8)
        elif self.config.gravity_acceleration is not None:
            gravity = self.config.gravity_acceleration
            planet_name = self._find_planet_name(gravity)
        else:
            # Randomly select a planet
            planet_name = random.choice(list(PLANET_PRESETS.keys()))
            gravity = PLANET_PRESETS[planet_name]
        
        # Generate initial position (relative coordinates 0-1)
        width, height = self.config.image_size
        margin = self.config.ball_radius + 10  # Margin to keep ball visible
        
        if self.config.ball_initial_x is not None:
            initial_x_rel = self.config.ball_initial_x
        else:
            initial_x_rel = random.uniform(0.2, 0.8)
        
        if self.config.ball_initial_y is not None:
            initial_y_rel = self.config.ball_initial_y
        else:
            initial_y_rel = random.uniform(0.1, 0.4)  # Start in upper portion
        
        initial_x = initial_x_rel * width
        initial_y = initial_y_rel * height
        
        # Initial velocities (pixels per second)
        initial_vx = self.config.ball_initial_vx
        initial_vy = self.config.ball_initial_vy
        
        # Convert gravity from m/s² to pixels/s²
        # Assuming 1 meter = 100 pixels for scaling
        pixels_per_meter = 100
        gravity_pixels = gravity * pixels_per_meter
        
        # Calculate physics trajectory
        positions = self._calculate_physics(
            initial_x, initial_y,
            initial_vx, initial_vy,
            gravity_pixels,
            self.config.simulation_duration,
            self.config.time_step
        )
        
        # Get final position
        final_x, final_y = positions[-1]
        
        # Ensure final position is within bounds
        final_x = max(margin, min(width - margin, final_x))
        final_y = max(margin, min(height - margin, final_y))
        
        return {
            "planet_name": planet_name,
            "gravity": gravity,
            "gravity_pixels": gravity_pixels,
            "initial_x": initial_x,
            "initial_y": initial_y,
            "initial_vx": initial_vx,
            "initial_vy": initial_vy,
            "final_x": final_x,
            "final_y": final_y,
            "positions": positions,
            "type": "default",
        }
    
    def _calculate_physics(
        self,
        initial_x: float,
        initial_y: float,
        initial_vx: float,
        initial_vy: float,
        gravity_pixels: float,
        duration: float,
        time_step: float
    ) -> list:
        """
        Calculate physics trajectory using kinematic equations.
        
        Returns:
            List of (x, y) positions at each time step
        """
        positions = []
        width, height = self.config.image_size
        margin = self.config.ball_radius
        
        t = 0.0
        while t <= duration:
            # Horizontal motion: x = x0 + vx * t (no acceleration)
            x = initial_x + initial_vx * t
            
            # Vertical motion: y = y0 + vy * t + 0.5 * g * t²
            y = initial_y + initial_vy * t + 0.5 * gravity_pixels * t * t
            
            # Clamp to image bounds
            x = max(margin, min(width - margin, x))
            y = max(margin, min(height - margin, y))
            
            positions.append((x, y))
            t += time_step
        
        return positions
    
    def _render_initial_state(self, task_data: dict) -> Image.Image:
        """Render initial state: ball + gravity arrow."""
        width, height = self.config.image_size
        
        # Create background
        img = Image.new("RGB", (width, height), self.config.background_color)
        draw = ImageDraw.Draw(img)
        
        # Draw ball at initial position
        ball_x = task_data["initial_x"]
        ball_y = task_data["initial_y"]
        self._draw_ball(draw, ball_x, ball_y, self.config.ball_radius, self.config.ball_color)
        
        # Draw gravity arrow (pointing downward)
        arrow_x = width - self.config.arrow_length - 20  # Right side with margin
        arrow_y = 20  # Top with margin
        self._draw_gravity_arrow(draw, arrow_x, arrow_y, self.config.arrow_length, self.config.arrow_color)
        
        # Optional: Add planet name label
        if task_data.get("planet_name"):
            self._draw_planet_label(draw, task_data["planet_name"], width, height)
        
        return img
    
    def _render_final_state(self, task_data: dict) -> Image.Image:
        """Render final state: ball at final position."""
        width, height = self.config.image_size
        
        # Create background
        img = Image.new("RGB", (width, height), self.config.background_color)
        draw = ImageDraw.Draw(img)
        
        # Draw ball at final position
        ball_x = task_data["final_x"]
        ball_y = task_data["final_y"]
        self._draw_ball(draw, ball_x, ball_y, self.config.ball_radius, self.config.ball_color)
        
        # Draw gravity arrow (same as initial)
        arrow_x = width - self.config.arrow_length - 20
        arrow_y = 20
        self._draw_gravity_arrow(draw, arrow_x, arrow_y, self.config.arrow_length, self.config.arrow_color)
        
        # Optional: Add planet name label
        if task_data.get("planet_name"):
            self._draw_planet_label(draw, task_data["planet_name"], width, height)
        
        return img
    
    def _generate_video(
        self,
        first_image: Image.Image,
        final_image: Image.Image,
        task_id: str,
        task_data: dict
    ) -> str:
        """Generate ground truth video showing physics motion."""
        temp_dir = Path(tempfile.gettempdir()) / f"{self.config.domain}_videos"
        temp_dir.mkdir(parents=True, exist_ok=True)
        video_path = temp_dir / f"{task_id}_ground_truth.mp4"
        
        # Create animation frames
        frames = self._create_physics_animation_frames(task_data)
        
        result = self.video_generator.create_video_from_frames(
            frames,
            video_path
        )
        
        return str(result) if result else None
    
    def _create_physics_animation_frames(self, task_data: dict) -> list:
        """
        Create animation frames showing ball motion under gravity.
        
        The ball moves smoothly following physics laws.
        """
        width, height = self.config.image_size
        positions = task_data["positions"]
        
        frames = []
        
        for x, y in positions:
            # Create frame
            img = Image.new("RGB", (width, height), self.config.background_color)
            draw = ImageDraw.Draw(img)
            
            # Draw gravity arrow (constant)
            arrow_x = width - self.config.arrow_length - 20
            arrow_y = 20
            self._draw_gravity_arrow(draw, arrow_x, arrow_y, self.config.arrow_length, self.config.arrow_color)
            
            # Draw ball at current position
            self._draw_ball(draw, x, y, self.config.ball_radius, self.config.ball_color)
            
            # Optional: Add planet name label
            if task_data.get("planet_name"):
                self._draw_planet_label(draw, task_data["planet_name"], width, height)
            
            frames.append(img)
        
        return frames
    
    # ══════════════════════════════════════════════════════════════════════════
    #  RENDERING HELPERS
    # ══════════════════════════════════════════════════════════════════════════
    
    def _draw_ball(
        self,
        draw: ImageDraw.Draw,
        x: float,
        y: float,
        radius: int,
        color: tuple[int, int, int]
    ) -> None:
        """Draw a ball (circle) at the specified position."""
        x0 = int(x - radius)
        y0 = int(y - radius)
        x1 = int(x + radius)
        y1 = int(y + radius)
        
        # Draw filled circle
        draw.ellipse([x0, y0, x1, y1], fill=color, outline=(0, 0, 0), width=2)
    
    def _draw_gravity_arrow(
        self,
        draw: ImageDraw.Draw,
        x: float,
        y: float,
        length: int,
        color: tuple[int, int, int]
    ) -> None:
        """
        Draw a gravity arrow pointing downward.
        
        Args:
            x, y: Top-left position of arrow
            length: Arrow length in pixels
            color: Arrow color
        """
        # Arrow points downward
        arrow_head_size = 10
        
        # Draw arrow shaft (vertical line)
        x_center = int(x + length // 2)
        draw.line(
            [(x_center, int(y)), (x_center, int(y + length - arrow_head_size))],
            fill=color,
            width=3
        )
        
        # Draw arrow head (triangle pointing down)
        head_x = x_center
        head_y = int(y + length - arrow_head_size)
        
        # Triangle points: left, right, bottom
        points = [
            (head_x - arrow_head_size, head_y),
            (head_x + arrow_head_size, head_y),
            (head_x, head_y + arrow_head_size)
        ]
        
        draw.polygon(points, fill=color, outline=color)
    
    def _draw_planet_label(
        self,
        draw: ImageDraw.Draw,
        planet_name: str,
        width: int,
        height: int
    ) -> None:
        """Draw planet name label in the corner."""
        try:
            # Try to load a font
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
        except:
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
            except:
                font = ImageFont.load_default()
        
        # Position in top-left corner
        text_x = 10
        text_y = 10
        
        # Draw text with background
        bbox = draw.textbbox((text_x, text_y), planet_name, font=font)
        padding = 4
        draw.rectangle(
            [
                bbox[0] - padding,
                bbox[1] - padding,
                bbox[2] + padding,
                bbox[3] + padding
            ],
            fill=(255, 255, 255, 200),
            outline=(0, 0, 0),
            width=1
        )
        draw.text((text_x, text_y), planet_name, fill=(0, 0, 0), font=font)
    
    def _find_planet_name(self, gravity: float) -> str:
        """Find the closest matching planet name for a given gravity value."""
        closest_planet = "Earth"
        min_diff = float('inf')
        
        for planet, planet_gravity in PLANET_PRESETS.items():
            diff = abs(gravity - planet_gravity)
            if diff < min_diff:
                min_diff = diff
                closest_planet = planet
        
        return closest_planet
