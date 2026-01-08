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
import numpy as np
import cv2
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from core import BaseGenerator, TaskPair, ImageRenderer
from core.video_utils import VideoGenerator
from .config import TaskConfig
from .prompts import get_prompt, get_rubric


class TaskGenerator(BaseGenerator):
    """
    Color addition mixing task generator.
    
    Generates tasks for predicting color mixing when two colored balls overlap.
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
        prompt = get_prompt(task_type, task_data)
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
        """Generate color mixing task data."""
        width, height = self.config.image_size
        
        # Generate two random colors (RGB)
        color1 = (
            random.randint(50, 255),
            random.randint(50, 255),
            random.randint(50, 255)
        )
        color2 = (
            random.randint(50, 255),
            random.randint(50, 255),
            random.randint(50, 255)
        )
        
        # Calculate additive color mixing with normalization
        # First add the colors
        mixed_r = color1[0] + color2[0]
        mixed_g = color1[1] + color2[1]
        mixed_b = color1[2] + color2[2]
        
        # Normalize if any channel exceeds 255
        max_value = max(mixed_r, mixed_g, mixed_b)
        if max_value > 255:
            # Scale all channels proportionally to keep the color relationship
            scale = 255.0 / max_value
            mixed_r = int(mixed_r * scale)
            mixed_g = int(mixed_g * scale)
            mixed_b = int(mixed_b * scale)
        else:
            mixed_r = int(mixed_r)
            mixed_g = int(mixed_g)
            mixed_b = int(mixed_b)
        
        mixed_color = (mixed_r, mixed_g, mixed_b)
        
        # Generate two ball positions that don't overlap
        # Ensure balls are fully visible and have minimum distance
        margin = self.config.edge_margin
        radius = self.config.ball_radius
        min_dist = self.config.min_distance
        
        # Try to find valid positions
        for _ in range(100):  # Try up to 100 times
            x1 = random.randint(margin, width - margin)
            y1 = random.randint(margin, height - margin)
            x2 = random.randint(margin, width - margin)
            y2 = random.randint(margin, height - margin)
            
            # Check distance
            distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            if distance >= min_dist:
                # Calculate midpoint (where they will meet)
                mid_x = (x1 + x2) / 2
                mid_y = (y1 + y2) / 2
                
                return {
                    "color1": color1,
                    "color2": color2,
                    "mixed_color": mixed_color,
                    "ball1_pos": (x1, y1),
                    "ball2_pos": (x2, y2),
                    "final_pos": (mid_x, mid_y),
                    "type": "default"
                }
        
        # Fallback: use default positions if we can't find valid ones
        x1 = width // 4
        y1 = height // 2
        x2 = 3 * width // 4
        y2 = height // 2
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        
        return {
            "color1": color1,
            "color2": color2,
            "mixed_color": mixed_color,
            "ball1_pos": (x1, y1),
            "ball2_pos": (x2, y2),
            "final_pos": (mid_x, mid_y),
            "type": "default"
        }
    
    def _render_initial_state(self, task_data: dict) -> Image.Image:
        """Render initial state: two colored balls at different positions."""
        img = self.renderer.create_blank_image(bg_color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        radius = self.config.ball_radius
        ball1_pos = task_data["ball1_pos"]
        ball2_pos = task_data["ball2_pos"]
        color1 = task_data["color1"]
        color2 = task_data["color2"]
        
        # Draw ball 1
        bbox1 = (
            ball1_pos[0] - radius,
            ball1_pos[1] - radius,
            ball1_pos[0] + radius,
            ball1_pos[1] + radius
        )
        draw.ellipse(bbox1, fill=color1, outline=(0, 0, 0), width=2)
        
        # Draw ball 2
        bbox2 = (
            ball2_pos[0] - radius,
            ball2_pos[1] - radius,
            ball2_pos[0] + radius,
            ball2_pos[1] + radius
        )
        draw.ellipse(bbox2, fill=color2, outline=(0, 0, 0), width=2)
        
        return img
    
    def _render_final_state(self, task_data: dict) -> Image.Image:
        """Render final state: two balls overlapped at midpoint with mixed color."""
        img = self.renderer.create_blank_image(bg_color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        radius = self.config.ball_radius
        final_pos = task_data["final_pos"]
        mixed_color = task_data["mixed_color"]
        
        # Draw the overlapped ball at the midpoint with mixed color
        bbox = (
            final_pos[0] - radius,
            final_pos[1] - radius,
            final_pos[0] + radius,
            final_pos[1] + radius
        )
        draw.ellipse(bbox, fill=mixed_color, outline=(0, 0, 0), width=2)
        
        return img
    
    def _generate_video(
        self,
        first_image: Image.Image,
        final_image: Image.Image,
        task_id: str,
        task_data: dict
    ) -> str:
        """Generate ground truth video showing color mixing animation."""
        temp_dir = Path(tempfile.gettempdir()) / f"{self.config.domain}_videos"
        temp_dir.mkdir(parents=True, exist_ok=True)
        video_path = temp_dir / f"{task_id}_ground_truth.mp4"
        
        # Create animation frames
        frames = self._create_mixing_animation_frames(task_data)
        
        result = self.video_generator.create_video_from_frames(
            frames,
            video_path
        )
        
        return str(result) if result else None
    
    def _create_mixing_animation_frames(
        self,
        task_data: dict,
        hold_frames: int = 5,
        transition_frames: int = 25
    ) -> list:
        """
        Create animation frames showing two balls moving toward each other and mixing.
        
        The animation shows:
        1. Initial state: two balls at different positions
        2. Transition: balls moving toward each other at same speed
        3. Final state: balls overlapped at midpoint with mixed color
        """
        frames = []
        
        # Hold initial position
        first_frame = self._render_initial_state(task_data)
        for _ in range(hold_frames):
            frames.append(first_frame)
        
        # Create transition frames
        radius = self.config.ball_radius
        ball1_start = task_data["ball1_pos"]
        ball2_start = task_data["ball2_pos"]
        final_pos = task_data["final_pos"]
        color1 = task_data["color1"]
        color2 = task_data["color2"]
        mixed_color = task_data["mixed_color"]
        
        for i in range(transition_frames):
            progress = i / (transition_frames - 1) if transition_frames > 1 else 1.0
            
            # Create frame with animated balls
            img = self.renderer.create_blank_image(bg_color=(255, 255, 255))
            draw = ImageDraw.Draw(img)
            
            # Calculate current positions (linear interpolation)
            ball1_current = (
                ball1_start[0] + (final_pos[0] - ball1_start[0]) * progress,
                ball1_start[1] + (final_pos[1] - ball1_start[1]) * progress
            )
            ball2_current = (
                ball2_start[0] + (final_pos[0] - ball2_start[0]) * progress,
                ball2_start[1] + (final_pos[1] - ball2_start[1]) * progress
            )
            
            # Calculate distance between ball centers
            distance = math.sqrt(
                (ball2_current[0] - ball1_current[0]) ** 2 +
                (ball2_current[1] - ball1_current[1]) ** 2
            )
            
            # Draw balls with proper overlap handling
            if distance < 2 * radius:
                # Balls are overlapping - need to draw with mixed color only in overlap region
                # Use numpy for efficient pixel operations
                
                width, height = self.config.image_size
                img_array = np.ones((height, width, 3), dtype=np.uint8) * 255
                
                # Create coordinate grids
                y_coords, x_coords = np.ogrid[:height, :width]
                
                # Calculate distances from each ball center
                dist1 = np.sqrt((x_coords - ball1_current[0]) ** 2 + (y_coords - ball1_current[1]) ** 2)
                dist2 = np.sqrt((x_coords - ball2_current[0]) ** 2 + (y_coords - ball2_current[1]) ** 2)
                
                # Create masks
                ball1_mask = dist1 <= radius
                ball2_mask = dist2 <= radius
                overlap_mask = ball1_mask & ball2_mask
                ball1_only_mask = ball1_mask & ~overlap_mask
                ball2_only_mask = ball2_mask & ~overlap_mask
                
                # Draw ball1 (non-overlap parts)
                img_array[ball1_only_mask] = color1
                
                # Draw ball2 (non-overlap parts)
                img_array[ball2_only_mask] = color2
                
                # Draw overlap region with normalized additive color mixing
                # Calculate normalized mixed color for overlap region
                overlap_mixed_r = np.zeros((height, width), dtype=np.float32)
                overlap_mixed_g = np.zeros((height, width), dtype=np.float32)
                overlap_mixed_b = np.zeros((height, width), dtype=np.float32)
                
                # Add colors in overlap region
                overlap_mixed_r[overlap_mask] = color1[0] + color2[0]
                overlap_mixed_g[overlap_mask] = color1[1] + color2[1]
                overlap_mixed_b[overlap_mask] = color1[2] + color2[2]
                
                # Normalize: find max value per pixel and scale if > 255
                max_per_pixel = np.maximum(np.maximum(overlap_mixed_r, overlap_mixed_g), overlap_mixed_b)
                scale_mask = max_per_pixel > 255
                scale_factor = np.ones((height, width), dtype=np.float32)
                scale_factor[scale_mask] = 255.0 / max_per_pixel[scale_mask]
                
                # Apply normalization
                overlap_mixed_r = (overlap_mixed_r * scale_factor).astype(np.uint8)
                overlap_mixed_g = (overlap_mixed_g * scale_factor).astype(np.uint8)
                overlap_mixed_b = (overlap_mixed_b * scale_factor).astype(np.uint8)
                
                # Combine into RGB image
                img_array[overlap_mask, 0] = overlap_mixed_r[overlap_mask]
                img_array[overlap_mask, 1] = overlap_mixed_g[overlap_mask]
                img_array[overlap_mask, 2] = overlap_mixed_b[overlap_mask]
                
                # Convert back to PIL Image
                img = Image.fromarray(img_array, 'RGB')
                draw = ImageDraw.Draw(img)
                
                # Draw complete black outlines for both balls (always visible, regardless of overlap)
                bbox1 = (
                    int(ball1_current[0] - radius),
                    int(ball1_current[1] - radius),
                    int(ball1_current[0] + radius),
                    int(ball1_current[1] + radius)
                )
                draw.ellipse(bbox1, outline=(0, 0, 0), width=2)
                
                bbox2 = (
                    int(ball2_current[0] - radius),
                    int(ball2_current[1] - radius),
                    int(ball2_current[0] + radius),
                    int(ball2_current[1] + radius)
                )
                draw.ellipse(bbox2, outline=(0, 0, 0), width=2)
            else:
                # Draw both balls separately (no overlap)
                bbox1 = (
                    ball1_current[0] - radius,
                    ball1_current[1] - radius,
                    ball1_current[0] + radius,
                    ball1_current[1] + radius
                )
                draw.ellipse(bbox1, fill=color1, outline=(0, 0, 0), width=2)
                
                bbox2 = (
                    ball2_current[0] - radius,
                    ball2_current[1] - radius,
                    ball2_current[0] + radius,
                    ball2_current[1] + radius
                )
                draw.ellipse(bbox2, fill=color2, outline=(0, 0, 0), width=2)
            
            frames.append(img)
        
        # Hold final position
        final_frame = self._render_final_state(task_data)
        for _ in range(hold_frames):
            frames.append(final_frame)
        
        return frames
    
    # ══════════════════════════════════════════════════════════════════════════
    #  HELPER METHODS
    # ══════════════════════════════════════════════════════════════════════════
    
    def _draw_arrow(self, draw: ImageDraw.Draw, start: tuple, end: tuple, 
                   color: tuple = (0, 0, 0), width: int = 2):
        """Draw a line with an arrowhead at the end."""
        # Draw the line
        draw.line([start, end], fill=color, width=width)
        
        # Calculate arrowhead
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        angle = math.atan2(dy, dx)
        
        arrow_length = 15
        arrow_angle = math.pi / 6  # 30 degrees
        
        # Arrowhead points
        arrow1_x = end[0] - arrow_length * math.cos(angle - arrow_angle)
        arrow1_y = end[1] - arrow_length * math.sin(angle - arrow_angle)
        arrow2_x = end[0] - arrow_length * math.cos(angle + arrow_angle)
        arrow2_y = end[1] - arrow_length * math.sin(angle + arrow_angle)
        
        # Draw arrowhead
        draw.line([end, (arrow1_x, arrow1_y)], fill=color, width=width)
        draw.line([end, (arrow2_x, arrow2_y)], fill=color, width=width)
    
    def _get_font(self, size: int = 20) -> ImageFont.FreeTypeFont:
        """Get a font for rendering text."""
        # Try common fonts
        font_names = [
            "Arial.ttf",
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/Library/Fonts/Arial.ttf",
            "DejaVuSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
        
        for font_name in font_names:
            try:
                return ImageFont.truetype(font_name, size)
            except (OSError, IOError):
                continue
        
        # Fallback to default
        return ImageFont.load_default()
