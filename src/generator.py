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
from typing import List, Tuple
from PIL import Image, ImageDraw

from core import BaseGenerator, TaskPair, ImageRenderer
from core.video_utils import VideoGenerator
from .config import TaskConfig
from .prompts import get_prompt


class TaskGenerator(BaseGenerator):
    """
    Ball bouncing trajectory generator.
    
    Generates tasks where a ball bounces off four walls in a bounded area.
    The task is to predict and generate the complete bounce trajectory.
    
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
        
        # Generate task data (ball position, velocity, trajectory)
        task_data = self._generate_task_data()
        
        # Render images
        first_image = self._render_initial_state(task_data)
        final_image = self._render_final_state(task_data)
        
        # Generate video (optional)
        video_path = None
        if self.config.generate_videos and self.video_generator:
            video_path = self._generate_video(first_image, final_image, task_id, task_data)
        
        # Select prompt based on bounce count, including explicit bounce count
        bounce_count = task_data["num_bounces"]
        if bounce_count <= 3:
            task_type = "simple"
        elif bounce_count <= 5:
            task_type = "medium"
        else:
            task_type = "complex"
        prompt = get_prompt(task_type, num_bounces=bounce_count)
        
        return TaskPair(
            task_id=task_id,
            domain=self.config.domain,
            prompt=prompt,
            first_image=first_image,
            final_image=final_image,
            ground_truth_video=video_path
        )
    
    # ══════════════════════════════════════════════════════════════════════════
    #  TASK-SPECIFIC METHODS
    # ══════════════════════════════════════════════════════════════════════════
    
    def _generate_task_data(self) -> dict:
        """Generate ball bouncing task data."""
        width, height = self.config.image_size
        margin = self.config.margin
        ball_radius = self.config.ball_radius
        
        # Define bounce area (inside margins)
        left_bound = margin
        right_bound = width - margin
        top_bound = margin
        bottom_bound = height - margin
        
        # Random initial position (within bounce area, accounting for ball radius)
        x0 = random.uniform(left_bound + ball_radius, right_bound - ball_radius)
        y0 = random.uniform(top_bound + ball_radius, bottom_bound - ball_radius)
        
        # Random initial velocity
        speed = random.uniform(self.config.initial_speed_min, self.config.initial_speed_max)
        angle = random.uniform(0, 2 * math.pi)
        vx = speed * math.cos(angle)
        vy = speed * math.sin(angle)
        
        # Calculate trajectory
        num_bounces = random.randint(self.config.min_bounces, self.config.max_bounces)
        trajectory, bounce_points = self._calculate_bounce_trajectory(
            x0, y0, vx, vy, num_bounces,
            left_bound, right_bound, top_bound, bottom_bound, ball_radius
        )
        
        return {
            "initial_position": (x0, y0),
            "initial_velocity": (vx, vy),
            "trajectory": trajectory,
            "bounce_points": bounce_points,
            "bounds": (left_bound, right_bound, top_bound, bottom_bound),
            "num_bounces": len(bounce_points),
            "type": "default"
        }
    
    def _calculate_bounce_trajectory(
        self,
        x0: float, y0: float,
        vx: float, vy: float,
        target_bounces: int,
        left: float, right: float, top: float, bottom: float,
        ball_radius: float
    ) -> Tuple[List[Tuple[float, float, float]], List[Tuple[float, float, str]]]:
        """
        Calculate ball bounce trajectory.
        
        Returns:
            trajectory: List of (x, y, t) points along the path
            bounce_points: List of (x, y, wall) bounce locations
        """
        trajectory = []
        bounce_points = []
        
        x, y = x0, y0
        vx_current, vy_current = vx, vy
        t = 0.0
        dt = 0.01  # Time step for simulation
        
        # Add initial point
        trajectory.append((x, y, t))
        
        bounce_count = 0
        
        while bounce_count < target_bounces:
            # Calculate time to next wall collision
            time_to_collision = float('inf')
            next_wall = None
            
            # Check collision with left wall
            if vx_current < 0:
                t_collision = (left + ball_radius - x) / vx_current
                if t_collision > 0 and t_collision < time_to_collision:
                    time_to_collision = t_collision
                    next_wall = "left"
            
            # Check collision with right wall
            if vx_current > 0:
                t_collision = (right - ball_radius - x) / vx_current
                if t_collision > 0 and t_collision < time_to_collision:
                    time_to_collision = t_collision
                    next_wall = "right"
            
            # Check collision with top wall
            if vy_current < 0:
                t_collision = (top + ball_radius - y) / vy_current
                if t_collision > 0 and t_collision < time_to_collision:
                    time_to_collision = t_collision
                    next_wall = "top"
            
            # Check collision with bottom wall
            if vy_current > 0:
                t_collision = (bottom - ball_radius - y) / vy_current
                if t_collision > 0 and t_collision < time_to_collision:
                    time_to_collision = t_collision
                    next_wall = "bottom"
            
            if time_to_collision == float('inf'):
                # No collision found, break
                break
            
            # Move ball until collision (with intermediate points)
            steps = max(1, int(time_to_collision / dt))
            actual_time = steps * dt
            if actual_time > time_to_collision:
                actual_time = time_to_collision
            
            for i in range(steps):
                t_step = dt if i < steps - 1 else (time_to_collision - (steps - 1) * dt)
                t += t_step
                x += vx_current * t_step
                y += vy_current * t_step
                trajectory.append((x, y, t))
            
            # Handle collision - ensure exact position at wall
            if next_wall == "left" or next_wall == "right":
                # Bounce off vertical wall
                x = left + ball_radius if next_wall == "left" else right - ball_radius
                vx_current = -vx_current * self.config.bounce_coefficient
            elif next_wall == "top" or next_wall == "bottom":
                # Bounce off horizontal wall
                y = top + ball_radius if next_wall == "top" else bottom - ball_radius
                vy_current = -vy_current * self.config.bounce_coefficient
            
            bounce_points.append((x, y, next_wall))
            bounce_count += 1
            
            # Update trajectory with exact bounce point
            if len(trajectory) == 0 or trajectory[-1] != (x, y, t):
                trajectory.append((x, y, t))
        
        return trajectory, bounce_points
    
    def _render_initial_state(self, task_data: dict) -> Image.Image:
        """Render initial state: ball, velocity arrow, and walls."""
        width, height = self.config.image_size
        img = Image.new("RGB", (width, height), color="white")
        draw = ImageDraw.Draw(img)
        
        # Draw walls
        self._draw_walls(draw, task_data["bounds"])
        
        # Draw ball at initial position
        x0, y0 = task_data["initial_position"]
        self._draw_ball(draw, x0, y0)
        
        # Draw velocity arrow
        vx, vy = task_data["initial_velocity"]
        self._draw_velocity_arrow(draw, x0, y0, vx, vy)
        
        return img
    
    def _render_final_state(self, task_data: dict) -> Image.Image:
        """Render final state: ball, complete trajectory, and walls."""
        width, height = self.config.image_size
        img = Image.new("RGB", (width, height), color="white")
        draw = ImageDraw.Draw(img)
        
        # Draw walls
        self._draw_walls(draw, task_data["bounds"])
        
        # Draw complete trajectory
        self._draw_trajectory(draw, task_data["trajectory"])
        
        # Draw ball at initial position
        x0, y0 = task_data["initial_position"]
        self._draw_ball(draw, x0, y0)
        
        # Mark all bounce points, with special emphasis on the last one
        bounce_points = task_data["bounce_points"]
        for i, (bx, by, wall) in enumerate(bounce_points):
            if i == len(bounce_points) - 1:
                # Last bounce point - draw with special marker
                self._draw_final_bounce_marker(draw, bx, by)
            else:
                # Regular bounce points
                self._draw_bounce_marker(draw, bx, by)
        
        return img
    
    def _generate_video(
        self,
        first_image: Image.Image,
        final_image: Image.Image,
        task_id: str,
        task_data: dict
    ) -> str:
        """Generate ground truth video showing ball moving along trajectory."""
        temp_dir = Path(tempfile.gettempdir()) / f"{self.config.domain}_videos"
        temp_dir.mkdir(parents=True, exist_ok=True)
        video_path = temp_dir / f"{task_id}_ground_truth.mp4"
        
        # Create animation frames
        frames = self._create_animation_frames(task_data)
        
        result = self.video_generator.create_video_from_frames(
            frames,
            video_path
        )
        
        return str(result) if result else None
    
    def _create_animation_frames(self, task_data: dict) -> List[Image.Image]:
        """Create animation frames showing ball moving along trajectory, stopping after the specified number of bounces."""
        width, height = self.config.image_size
        trajectory = task_data["trajectory"]
        bounds = task_data["bounds"]
        bounce_points = task_data["bounce_points"]
        
        if not trajectory:
            return []
        
        # Calculate total time (up to the last bounce point)
        total_time = trajectory[-1][2] if trajectory else self.config.animation_duration
        num_frames = int(self.config.video_fps * total_time)
        num_frames = max(10, min(num_frames, 300))  # Limit between 10 and 300 frames
        
        # Add hold frames at the end to show the ball stopped at final position
        hold_frames = int(self.config.video_fps * 0.5)  # Hold for 0.5 seconds
        
        frames = []
        dt = total_time / num_frames if num_frames > 0 else 0.01
        
        for frame_idx in range(num_frames):
            t = frame_idx * dt
            
            # Clamp time to not exceed trajectory end
            if t > total_time:
                t = total_time
            
            # Find current position in trajectory
            current_pos = None
            for i in range(len(trajectory) - 1):
                t1 = trajectory[i][2]
                t2 = trajectory[i + 1][2]
                if t1 <= t <= t2:
                    # Interpolate between points
                    alpha = (t - t1) / (t2 - t1) if t2 > t1 else 0
                    x1, y1, _ = trajectory[i]
                    x2, y2, _ = trajectory[i + 1]
                    current_pos = (
                        x1 + alpha * (x2 - x1),
                        y1 + alpha * (y2 - y1)
                    )
                    break
            
            if current_pos is None:
                # Use last point (final position after last bounce)
                current_pos = (trajectory[-1][0], trajectory[-1][1])
            
            # Create frame
            img = Image.new("RGB", (width, height), color="white")
            draw = ImageDraw.Draw(img)
            
            # Draw walls
            self._draw_walls(draw, bounds)
            
            # Draw trajectory up to current time
            current_trajectory = [(x, y, t_val) for x, y, t_val in trajectory if t_val <= t]
            if len(current_trajectory) > 1:
                self._draw_trajectory(draw, current_trajectory)
            
            # Draw ball at current position
            self._draw_ball(draw, current_pos[0], current_pos[1])
            
            # If we've reached the final bounce point, mark it
            if bounce_points and t >= total_time:
                final_bx, final_by, _ = bounce_points[-1]
                self._draw_final_bounce_marker(draw, final_bx, final_by)
            
            frames.append(img)
        
        # Add hold frames at the end showing the final state
        final_frame = frames[-1] if frames else None
        if final_frame:
            for _ in range(hold_frames):
                frames.append(final_frame.copy())
        
        return frames
    
    # ══════════════════════════════════════════════════════════════════════════
    #  RENDERING HELPERS
    # ══════════════════════════════════════════════════════════════════════════
    
    def _draw_walls(self, draw: ImageDraw.Draw, bounds: Tuple[float, float, float, float]):
        """Draw four walls (bounce surfaces)."""
        left, right, top, bottom = bounds
        thickness = self.config.wall_thickness
        color = self.config.wall_color
        
        # Left wall
        draw.rectangle([left - thickness, top - thickness, left, bottom + thickness], fill=color)
        # Right wall
        draw.rectangle([right, top - thickness, right + thickness, bottom + thickness], fill=color)
        # Top wall
        draw.rectangle([left - thickness, top - thickness, right + thickness, top], fill=color)
        # Bottom wall
        draw.rectangle([left - thickness, bottom, right + thickness, bottom + thickness], fill=color)
    
    def _draw_ball(self, draw: ImageDraw.Draw, x: float, y: float):
        """Draw ball at position (x, y)."""
        radius = self.config.ball_radius
        color = self.config.ball_color
        
        # Draw circle
        bbox = [x - radius, y - radius, x + radius, y + radius]
        draw.ellipse(bbox, fill=color)
    
    def _draw_velocity_arrow(self, draw: ImageDraw.Draw, x: float, y: float, vx: float, vy: float):
        """Draw velocity arrow indicating initial direction."""
        arrow_length = 40
        arrow_head_size = 8
        
        # Normalize velocity to get direction
        speed = math.sqrt(vx * vx + vy * vy)
        if speed == 0:
            return
        
        dx = (vx / speed) * arrow_length
        dy = (vy / speed) * arrow_length
        
        # Arrow line
        end_x = x + dx
        end_y = y + dy
        
        color = self.config.trajectory_color
        width = self.config.trajectory_width
        
        # Draw arrow line
        draw.line([(x, y), (end_x, end_y)], fill=color, width=width)
        
        # Draw arrow head
        angle = math.atan2(dy, dx)
        arrow_angle1 = angle + math.pi - math.pi / 6
        arrow_angle2 = angle + math.pi + math.pi / 6
        
        head_x1 = end_x + arrow_head_size * math.cos(arrow_angle1)
        head_y1 = end_y + arrow_head_size * math.sin(arrow_angle1)
        head_x2 = end_x + arrow_head_size * math.cos(arrow_angle2)
        head_y2 = end_y + arrow_head_size * math.sin(arrow_angle2)
        
        draw.polygon([(end_x, end_y), (head_x1, head_y1), (head_x2, head_y2)], fill=color)
    
    def _draw_trajectory(self, draw: ImageDraw.Draw, trajectory: List[Tuple[float, float, float]]):
        """Draw trajectory path."""
        if len(trajectory) < 2:
            return
        
        color = self.config.trajectory_color
        width = self.config.trajectory_width
        
        # Draw connected line segments
        points = [(x, y) for x, y, _ in trajectory]
        draw.line(points, fill=color, width=width)
    
    def _draw_bounce_marker(self, draw: ImageDraw.Draw, x: float, y: float):
        """Draw a small marker at bounce point."""
        marker_size = 4
        color = (255, 0, 0)  # Red marker
        
        bbox = [x - marker_size, y - marker_size, x + marker_size, y + marker_size]
        draw.ellipse(bbox, fill=color)
    
    def _draw_final_bounce_marker(self, draw: ImageDraw.Draw, x: float, y: float):
        """Draw a special marker at the final bounce point (where the ball stops)."""
        # Draw a larger, more prominent marker
        outer_size = 8
        inner_size = 5
        outer_color = (255, 0, 0)  # Red outer ring
        inner_color = (255, 255, 0)  # Yellow inner circle
        
        # Outer ring
        outer_bbox = [x - outer_size, y - outer_size, x + outer_size, y + outer_size]
        draw.ellipse(outer_bbox, fill=outer_color)
        
        # Inner circle
        inner_bbox = [x - inner_size, y - inner_size, x + inner_size, y + inner_size]
        draw.ellipse(inner_bbox, fill=inner_color)
