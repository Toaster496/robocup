#!/usr/bin/env python3
"""
Vision System for Open Jr RoboCup Soccer Robot
Ball, goal, and field detection using Arducam IMX477
"""

import cv2
import numpy as np
from dataclasses import dataclass
from typing import Optional, List, Tuple
import yaml


@dataclass
class BallDetection:
    """Detected ball information"""
    center_x: int
    center_y: int
    radius_pixels: int
    distance_meters: float
    confidence: float


@dataclass
class GoalDetection:
    """Detected goal information"""
    color: str  # 'blue' or 'yellow'
    center_x: int
    center_y: int
    width: int
    height: int
    distance_meters: float


@dataclass
class FieldLines:
    """Detected field lines"""
    lines: List[Tuple[int, int, int, int]]  # (x1, y1, x2, y2)


class VisionSystem:
    """
    Computer vision system for RoboCup soccer
    Detects balls, goals, and field features
    """
    
    def __init__(self, camera_params_file: str):
        self.camera_params = self._load_camera_params(camera_params_file)
        self.cap: Optional[cv2.VideoCapture] = None
        self.frame_width = self.camera_params['processing']['target_width']
        self.frame_height = self.camera_params['processing']['target_height']
        
    def _load_camera_params(self, params_file: str) -> dict:
        """Load camera parameters from YAML file"""
        with open(params_file, 'r') as f:
            return yaml.safe_load(f)
            
    def connect(self, camera_id: int = 0) -> bool:
        """Connect to camera"""
        try:
            # Try CSI camera first
            self.cap = cv2.VideoCapture(camera_id, cv2.CAP_V4L2)
            
            if not self.cap.isOpened():
                print("Failed to open camera")
                return False
                
            # Set resolution
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
            self.cap.set(cv2.CAP_PROP_FPS, self.camera_params['processing']['frame_rate'])
            
            # Set exposure and gain to auto
            self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 3)
            
            print(f"Camera connected: {self.frame_width}x{self.frame_height}")
            return True
            
        except Exception as e:
            print(f"Camera connection failed: {e}")
            return False
            
    def disconnect(self):
        """Disconnect from camera"""
        if self.cap:
            self.cap.release()
            self.cap = None
            
    def _hsv_to_bgr(self, hsv_min: dict, hsv_max: dict) -> Tuple[np.ndarray, np.ndarray]:
        """Convert HSV ranges to numpy arrays"""
        lower = np.array([hsv_min['h'], hsv_min['s'], hsv_min['v']], dtype=np.uint8)
        upper = np.array([hsv_max['h'], hsv_max['s'], hsv_max['v']], dtype=np.uint8)
        return lower, upper
        
    def detect_ball(self, frame: np.ndarray) -> Optional[BallDetection]:
        """
        Detect orange ball in frame
        
        Args:
            frame: BGR image frame
            
        Returns:
            BallDetection if found, None otherwise
        """
        # Convert to HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Get orange color range
        orange_min = self.camera_params['vision']['ball_detection']['orange_range']
        orange_max = {
            'h': orange_min['h_max'],
            's': orange_min['s_max'],
            'v': orange_min['v_max']
        }
        orange_min_arr = np.array([orange_min['h_min'], orange_min['s_min'], orange_min['v_min']], dtype=np.uint8)
        orange_max_arr = np.array([orange_max['h'], orange_max['s'], orange_max['v']], dtype=np.uint8)
        
        # Threshold for orange color
        mask = cv2.inRange(hsv, orange_min_arr, orange_max_arr)
        
        # Morphological operations to reduce noise
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return None
            
        # Find largest contour (most likely the ball)
        largest_contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest_contour)
        
        # Check if contour is large enough
        min_area = self.camera_params['vision']['ball_detection']['min_contour_area']
        max_area = self.camera_params['vision']['ball_detection']['max_contour_area']
        
        if area < min_area or area > max_area:
            return None
            
        # Get enclosing circle
        ((x, y), radius) = cv2.minEnclosingCircle(largest_contour)
        center = (int(x), int(y))
        radius = int(radius)
        
        # Estimate distance based on apparent size
        # This should be calibrated for your specific setup
        known_diameter_m = 0.07  # Standard RoboCup ball ~7cm
        focal_length = self.camera_params['intrinsics']['focal_length']['fx']
        distance = (known_diameter_m * focal_length) / (2 * radius * 0.001)  # Rough estimate
        
        # Calculate confidence based on circularity
        perimeter = cv2.arcLength(largest_contour, True)
        if perimeter == 0:
            return None
        circularity = 4 * np.pi * area / (perimeter * perimeter)
        confidence = min(1.0, circularity / 0.8)  # Normalize to [0, 1]
        
        return BallDetection(
            center_x=center[0],
            center_y=center[1],
            radius_pixels=radius,
            distance_meters=distance,
            confidence=confidence
        )
        
    def detect_goal(self, frame: np.ndarray) -> Optional[GoalDetection]:
        """
        Detect blue or yellow goal in frame
        
        Args:
            frame: BGR image frame
            
        Returns:
            GoalDetection if found, None otherwise
        """
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Try both colors
        for color_name in ['blue', 'yellow']:
            color_range = self.camera_params['vision']['goal_detection'][f'{color_name}_range']
            lower = np.array([color_range['h_min'], color_range['s_min'], color_range['v_min']], dtype=np.uint8)
            upper = np.array([color_range['h_max'], color_range['s_max'], color_range['v_max']], dtype=np.uint8)
            
            # Threshold
            mask = cv2.inRange(hsv, lower, upper)
            
            # Morphological operations
            kernel = np.ones((5, 5), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            
            # Find contours
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                continue
                
            # Find largest contour
            largest_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest_contour)
            
            if area < 500:  # Minimum goal area threshold
                continue
                
            # Get bounding rectangle
            x, y, w, h = cv2.boundingRect(largest_contour)
            
            # Estimate distance (simplified)
            distance = 2.0  # Placeholder - should be calibrated
            
            return GoalDetection(
                color=color_name,
                center_x=x + w // 2,
                center_y=y + h // 2,
                width=w,
                height=h,
                distance_meters=distance
            )
            
        return None
        
    def detect_field_lines(self, frame: np.ndarray) -> Optional[FieldLines]:
        """
        Detect field lines using edge detection and Hough transform
        
        Args:
            frame: BGR image frame
            
        Returns:
            FieldLines if detected, None otherwise
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Edge detection
        edges = cv2.Canny(blurred, 50, 150, apertureSize=3)
        
        # Detect lines using Hough transform
        lines = cv2.HoughLinesP(
            edges,
            rho=1,
            theta=np.pi / 180,
            threshold=50,
            minLineLength=50,
            maxLineGap=10
        )
        
        if lines is None:
            return None
            
        # Convert to list of tuples
        line_list = [(line[0][0], line[0][1], line[0][2], line[0][3]) for line in lines]
        
        return FieldLines(lines=line_list)
        
    def get_frame(self) -> Optional[np.ndarray]:
        """Capture a frame from camera"""
        if not self.cap:
            return None
            
        ret, frame = self.cap.read()
        if not ret:
            return None
            
        return frame
        
    def process_frame(self, frame: np.ndarray) -> dict:
        """
        Process a frame and detect all objects
        
        Args:
            frame: BGR image frame
            
        Returns:
            Dictionary with all detections
        """
        results = {
            'ball': self.detect_ball(frame),
            'goal': self.detect_goal(frame),
            'field_lines': self.detect_field_lines(frame),
            'timestamp': time.time()
        }
        
        return results
        
    def visualize_detections(self, frame: np.ndarray, results: dict) -> np.ndarray:
        """
        Draw detections on frame for visualization
        
        Args:
            frame: BGR image frame
            results: Detection results from process_frame()
            
        Returns:
            Annotated frame
        """
        vis_frame = frame.copy()
        
        # Draw ball detection
        if results['ball']:
            ball = results['ball']
            cv2.circle(vis_frame, (ball.center_x, ball.center_y), ball.radius_pixels, (0, 255, 0), 2)
            cv2.putText(vis_frame, f"Ball: {ball.distance_meters:.2f}m",
                       (ball.center_x - 50, ball.center_y - ball.radius_pixels - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                       
        # Draw goal detection
        if results['goal']:
            goal = results['goal']
            color = (255, 0, 0) if goal.color == 'blue' else (0, 255, 255)
            x1 = goal.center_x - goal.width // 2
            y1 = goal.center_y - goal.height // 2
            cv2.rectangle(vis_frame, (x1, y1), (x1 + goal.width, y1 + goal.height), color, 2)
            cv2.putText(vis_frame, f"{goal.color.capitalize()} Goal",
                       (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                       
        # Draw field lines
        if results['field_lines']:
            for line in results['field_lines'].lines:
                cv2.line(vis_frame, (line[0], line[1]), (line[2], line[3]), (255, 255, 255), 2)
                
        return vis_frame


def main():
    """Example usage of vision system"""
    import time
    
    vision = VisionSystem('/workspace/config/camera_params.yaml')
    
    if not vision.connect():
        print("Failed to connect to camera")
        return
        
    print("Press 'q' to quit")
    
    try:
        while True:
            frame = vision.get_frame()
            if frame is None:
                print("Failed to capture frame")
                break
                
            # Process frame
            results = vision.process_frame(frame)
            
            # Visualize
            vis_frame = vision.visualize_detections(frame, results)
            
            # Display
            cv2.imshow('Vision System', vis_frame)
            
            # Print detections
            if results['ball']:
                print(f"Ball detected at ({results['ball'].center_x}, {results['ball'].center_y}), "
                      f"distance: {results['ball'].distance_meters:.2f}m")
                      
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        pass
    finally:
        vision.disconnect()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
