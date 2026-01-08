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


class TaskGenerator(BaseGenerator):
    """
    Optics refraction task generator.
    
    Generates tasks for predicting light refraction through glass.
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
        """Generate optics refraction task data."""
        # Random glass refractive index
        n_glass = random.uniform(self.config.n_glass_min, self.config.n_glass_max)
        
        # Random incident angle (theta) in degrees
        theta_degrees = random.uniform(self.config.theta_min, self.config.theta_max)
        theta_radians = math.radians(theta_degrees)
        
        # Calculate refraction angle using Snell's law: n1 * sin(theta1) = n2 * sin(theta2)
        # n_air * sin(theta_incident) = n_glass * sin(theta_refracted)
        sin_theta_refracted = (self.config.n_air * math.sin(theta_radians)) / n_glass
        
        # Check for total internal reflection (shouldn't happen for air to glass)
        if sin_theta_refracted > 1.0:
            sin_theta_refracted = 1.0
        
        theta_refracted_radians = math.asin(sin_theta_refracted)
        theta_refracted_degrees = math.degrees(theta_refracted_radians)
        
        return {
            "n_glass": n_glass,
            "n_air": self.config.n_air,
            "theta_incident_degrees": theta_degrees,
            "theta_incident_radians": theta_radians,
            "theta_refracted_degrees": theta_refracted_degrees,
            "theta_refracted_radians": theta_refracted_radians,
            "type": "default"
        }
        """Generate mate-in-1 position using chess library."""
        generators = [
            self._gen_back_rank_mate,
            self._gen_queen_mate,
            self._gen_rook_mate,
        ]
        
        for _ in range(10):  # Try up to 10 times
            gen_func = random.choice(generators)
            position = gen_func()
            if position and self._validate_mate(position):
                return position
        
        # Fallback to template
        return random.choice(self._get_fallback_templates())
    
    def _render_initial_state(self, task_data: dict) -> Image.Image:
        """Render initial state: glass surface, incident ray, and angle annotation."""
        img = self.renderer.create_blank_image(bg_color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        width, height = self.config.image_size
        center_x, center_y = width // 2, height // 2
        
        # Glass surface: horizontal line in the middle
        glass_y = center_y
        glass_line_width = 3
        draw.line([(0, glass_y), (width, glass_y)], fill=(0, 0, 0), width=glass_line_width)
        
        # Glass hatch lines (below the surface)
        hatch_spacing = 8
        hatch_length = 15
        hatch_angle = 45  # degrees
        num_hatches = width // hatch_spacing
        
        for i in range(num_hatches):
            x = i * hatch_spacing
            # Draw diagonal hatch lines
            x1 = x
            y1 = glass_y + 5
            x2 = x1 + hatch_length * math.cos(math.radians(hatch_angle))
            y2 = y1 + hatch_length * math.sin(math.radians(hatch_angle))
            draw.line([(x1, y1), (x2, y2)], fill=(100, 100, 100), width=1)
        
        # Incident ray: from top-left to glass surface
        theta = task_data["theta_incident_radians"]
        
        # Calculate ray start point (above glass)
        # Ray comes from left side, hits glass surface at center
        ray_length_above = center_y - 50  # Distance from top to glass
        ray_start_x = center_x - ray_length_above * math.tan(theta)
        ray_start_y = 50
        
        # Ray end point (at glass surface)
        ray_end_x = center_x
        ray_end_y = glass_y
        
        # Draw incident ray with arrow
        self._draw_arrow(draw, (ray_start_x, ray_start_y), (ray_end_x, ray_end_y), 
                        color=(0, 0, 255), width=3)
        
        # Draw normal line (perpendicular to glass surface)
        normal_length = 30
        draw.line([(center_x, glass_y - normal_length), (center_x, glass_y + normal_length)], 
                 fill=(150, 150, 150), width=1)
        
        # Draw angle arc and label
        angle_arc_radius = 40
        # Angle arc from normal to incident ray
        # Normal points up (-90 degrees in PIL's coordinate system)
        # If ray comes from left, angle should be from normal (-90) to normal - theta
        # PIL's arc: 0 degrees is 3 o'clock, positive is counterclockwise
        start_angle = -90  # Normal points up
        end_angle = -90 - math.degrees(theta)  # Ray angle (negative because it's to the left of normal)
        
        # Draw angle arc
        bbox = (center_x - angle_arc_radius, glass_y - angle_arc_radius,
                center_x + angle_arc_radius, glass_y + angle_arc_radius)
        draw.arc(bbox, start=end_angle, end=start_angle, fill=(0, 0, 0), width=2)
        
        # Label angle: "θ = X°"
        theta_degrees = task_data["theta_incident_degrees"]
        angle_label = f"θ = {theta_degrees:.0f}°"
        
        # Position label near the angle arc
        label_x = center_x + angle_arc_radius + 10
        label_y = glass_y - angle_arc_radius
        font = self._get_font(size=20)
        draw.text((label_x, label_y), angle_label, fill=(0, 0, 0), font=font)
        
        return img
    
    def _render_final_state(self, task_data: dict) -> Image.Image:
        """Render final state: glass surface, incident ray, refracted ray."""
        img = self.renderer.create_blank_image(bg_color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        width, height = self.config.image_size
        center_x, center_y = width // 2, height // 2
        
        # Glass surface: horizontal line in the middle
        glass_y = center_y
        glass_line_width = 3
        draw.line([(0, glass_y), (width, glass_y)], fill=(0, 0, 0), width=glass_line_width)
        
        # Glass hatch lines (below the surface)
        hatch_spacing = 8
        hatch_length = 15
        hatch_angle = 45  # degrees
        num_hatches = width // hatch_spacing
        
        for i in range(num_hatches):
            x = i * hatch_spacing
            x1 = x
            y1 = glass_y + 5
            x2 = x1 + hatch_length * math.cos(math.radians(hatch_angle))
            y2 = y1 + hatch_length * math.sin(math.radians(hatch_angle))
            draw.line([(x1, y1), (x2, y2)], fill=(100, 100, 100), width=1)
        
        # Incident ray: from top-left to glass surface
        theta_incident = task_data["theta_incident_radians"]
        ray_length_above = center_y - 50
        ray_start_x = center_x - ray_length_above * math.tan(theta_incident)
        ray_start_y = 50
        ray_end_x = center_x
        ray_end_y = glass_y
        
        # Draw incident ray
        self._draw_arrow(draw, (ray_start_x, ray_start_y), (ray_end_x, ray_end_y), 
                        color=(0, 0, 255), width=3)
        
        # Refracted ray: from glass surface into glass
        theta_refracted = task_data["theta_refracted_radians"]
        
        # Refracted ray goes into glass (below surface)
        # Calculate where the ray hits the bottom edge of the image
        # Ray starts at (center_x, glass_y) and propagates at angle theta_refracted
        # We need to find intersection with bottom edge (y = height) or side edge
        
        # Calculate intersection with bottom edge first
        distance_to_bottom = height - glass_y
        x_at_bottom = center_x + distance_to_bottom * math.tan(theta_refracted)
        
        # Check if ray hits bottom edge or side edge first
        if 0 <= x_at_bottom <= width:
            # Ray hits bottom edge
            refracted_end_x = x_at_bottom
            refracted_end_y = height
        elif x_at_bottom > width:
            # Ray hits right edge
            distance_to_right = width - center_x
            refracted_end_x = width
            refracted_end_y = glass_y + distance_to_right / math.tan(theta_refracted)
        else:
            # Ray hits left edge (shouldn't happen for normal refraction, but handle it)
            distance_to_left = center_x
            refracted_end_x = 0
            refracted_end_y = glass_y + distance_to_left / math.tan(theta_refracted)
        
        # Draw refracted ray with arrow (extending to edge)
        self._draw_arrow(draw, (center_x, glass_y), (refracted_end_x, refracted_end_y), 
                        color=(255, 0, 0), width=3)
        
        # Draw normal line
        normal_length = 30
        draw.line([(center_x, glass_y - normal_length), (center_x, glass_y + normal_length)], 
                 fill=(150, 150, 150), width=1)
        
        return img
    
    def _generate_video(
        self,
        first_image: Image.Image,
        final_image: Image.Image,
        task_id: str,
        task_data: dict
    ) -> str:
        """Generate ground truth video showing light refraction."""
        temp_dir = Path(tempfile.gettempdir()) / f"{self.config.domain}_videos"
        temp_dir.mkdir(parents=True, exist_ok=True)
        video_path = temp_dir / f"{task_id}_ground_truth.mp4"
        
        # Create animation frames
        frames = self._create_refraction_animation_frames(task_data)
        
        result = self.video_generator.create_video_from_frames(
            frames,
            video_path
        )
        
        return str(result) if result else None
    
    def _create_refraction_animation_frames(
        self,
        task_data: dict,
        hold_frames: int = 5,
        transition_frames: int = 25
    ) -> list:
        """
        Create animation frames showing light entering glass and refracting.
        
        The animation shows:
        1. Initial state: incident ray approaching glass
        2. Transition: ray entering glass and refracting
        3. Final state: refracted ray propagating in glass
        """
        frames = []
        
        # Hold initial position
        first_frame = self._render_initial_state(task_data)
        for _ in range(hold_frames):
            frames.append(first_frame)
        
        # Create transition frames
        width, height = self.config.image_size
        center_x, center_y = width // 2, height // 2
        glass_y = center_y
        
        theta_incident = task_data["theta_incident_radians"]
        theta_refracted = task_data["theta_refracted_radians"]
        
        # Calculate ray positions
        ray_length_above = center_y - 50
        ray_start_x = center_x - ray_length_above * math.tan(theta_incident)
        ray_start_y = 50
        
        ray_length_below = height - center_y - 50
        refracted_end_x = center_x + ray_length_below * math.tan(theta_refracted)
        refracted_end_y = height - 50
        
        for i in range(transition_frames):
            progress = i / (transition_frames - 1) if transition_frames > 1 else 1.0
            
            # Create frame with animated ray
            img = self.renderer.create_blank_image(bg_color=(255, 255, 255))
            draw = ImageDraw.Draw(img)
            
            # Draw glass surface
            glass_line_width = 3
            draw.line([(0, glass_y), (width, glass_y)], fill=(0, 0, 0), width=glass_line_width)
            
            # Draw glass hatch lines
            hatch_spacing = 8
            hatch_length = 15
            hatch_angle = 45
            num_hatches = width // hatch_spacing
            
            for j in range(num_hatches):
                x = j * hatch_spacing
                x1 = x
                y1 = glass_y + 5
                x2 = x1 + hatch_length * math.cos(math.radians(hatch_angle))
                y2 = y1 + hatch_length * math.sin(math.radians(hatch_angle))
                draw.line([(x1, y1), (x2, y2)], fill=(100, 100, 100), width=1)
            
            # Draw normal line
            normal_length = 30
            draw.line([(center_x, glass_y - normal_length), (center_x, glass_y + normal_length)], 
                     fill=(150, 150, 150), width=1)
            
            # Draw incident ray (always visible)
            self._draw_arrow(draw, (ray_start_x, ray_start_y), (center_x, glass_y), 
                            color=(0, 0, 255), width=3)
            
            # Draw refracted ray (appears gradually)
            if progress > 0:
                # Calculate final refracted ray end position (at image edge)
                distance_to_bottom = height - glass_y
                x_at_bottom = center_x + distance_to_bottom * math.tan(theta_refracted)
                
                if 0 <= x_at_bottom <= width:
                    final_end_x = x_at_bottom
                    final_end_y = height
                elif x_at_bottom > width:
                    distance_to_right = width - center_x
                    final_end_x = width
                    final_end_y = glass_y + distance_to_right / math.tan(theta_refracted)
                else:
                    distance_to_left = center_x
                    final_end_x = 0
                    final_end_y = glass_y + distance_to_left / math.tan(theta_refracted)
                
                # Current position based on progress (fixed angle, just extend length)
                current_end_x = center_x + (final_end_x - center_x) * progress
                current_end_y = glass_y + (final_end_y - glass_y) * progress
                
                self._draw_arrow(draw, (center_x, glass_y), (current_end_x, current_end_y), 
                                color=(255, 0, 0), width=3)
            
            # Draw angle label and arc (only in initial frames)
            if progress < 0.3:
                theta_degrees = task_data["theta_incident_degrees"]
                theta = task_data["theta_incident_radians"]
                angle_label = f"θ = {theta_degrees:.0f}°"
                angle_arc_radius = 40
                
                # Draw angle arc (same as in initial state)
                start_angle = -90  # Normal points up
                end_angle = -90 - math.degrees(theta)  # Ray angle
                bbox = (center_x - angle_arc_radius, glass_y - angle_arc_radius,
                        center_x + angle_arc_radius, glass_y + angle_arc_radius)
                draw.arc(bbox, start=end_angle, end=start_angle, fill=(0, 0, 0), width=2)
                
                # Position label near the angle arc
                label_x = center_x + angle_arc_radius + 10
                label_y = glass_y - angle_arc_radius
                font = self._get_font(size=20)
                draw.text((label_x, label_y), angle_label, fill=(0, 0, 0), font=font)
            
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
