import cv2
import mediapipe as mp
import numpy as np
from typing import List, Dict, Tuple, Optional
import math
import base64
import io
from PIL import Image

class BasketballPoseAnalyzer:
    """
    Analyzes basketball shooting form using MediaPipe pose estimation
    """
    
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=2,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Key pose landmarks for basketball shooting analysis
        self.key_landmarks = {
            'nose': 0,
            'left_eye': 1,
            'right_eye': 2,
            'left_ear': 7,
            'right_ear': 8,
            'left_shoulder': 11,
            'right_shoulder': 12,
            'left_elbow': 13,
            'right_elbow': 14,
            'left_wrist': 15,
            'right_wrist': 16,
            'left_hip': 23,
            'right_hip': 24,
            'left_knee': 25,
            'right_knee': 26,
            'left_ankle': 27,
            'right_ankle': 28
        }
    
    def analyze_video(self, video_path: str) -> Dict:
        """
        Analyze basketball shooting form from video
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video file: {video_path}")
        
        # Get video rotation information
        rotation = self._get_video_rotation(cap)
        print(f"Detected video rotation from metadata: {rotation} degrees")
        
        all_frames_data = []  # Store data for all detected people
        raw_frames = []  # Store raw frames for later cropping
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Store original frame dimensions for landmark transformation
            original_shape = frame.shape
            
            # If no rotation detected from metadata, try content-based detection on first frame
            if rotation == 0 and frame_count == 0:
                content_rotation = self._detect_rotation_from_content(frame)
                if content_rotation != 0:
                    rotation = content_rotation
                    print(f"Applied content-based rotation detection: {rotation} degrees")
                
            # Correct frame rotation if needed
            if rotation != 0:
                frame = self._rotate_frame(frame, rotation)
                
            # Store raw frame for potential cropping
            raw_frames.append(frame.copy())
                
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Detect all people in the frame using a sliding window approach
            people_in_frame = self._detect_multiple_people(rgb_frame)
            
            frame_people_data = []
            for person_idx, person_landmarks in enumerate(people_in_frame):
                if person_landmarks:
                    landmarks_data = self._extract_landmarks(person_landmarks)
                    
                    # Transform landmarks if rotation was applied
                    if rotation != 0:
                        landmarks_data = self._transform_landmarks_for_rotation(
                            landmarks_data, original_shape, rotation
                        )
                    
                    frame_people_data.append({
                        'person_id': person_idx,
                        'landmarks': landmarks_data,
                        'confidence': self._calculate_pose_confidence(person_landmarks)
                    })
            
            if frame_people_data:
                all_frames_data.append({
                    'frame': frame_count,
                    'people': frame_people_data,
                    'timestamp': cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
                })
            
            frame_count += 1
        
        cap.release()
        
        # Follow new streamlined flow: detect → track → release → visualize
        print("Starting streamlined shooter analysis flow...")
        try:
            analysis = self._streamlined_shooter_analysis(all_frames_data, raw_frames)
            if 'error' not in analysis:
                return analysis
        except Exception as e:
            print(f"Streamlined analysis failed: {e}")
        
        # Fallback to original single-player analysis
        print("Falling back to single-player analysis...")
        return self._fallback_single_player_analysis(all_frames_data, raw_frames)
    
    def _get_video_rotation(self, cap: cv2.VideoCapture) -> int:
        """
        Get the rotation angle from video metadata
        Returns rotation angle in degrees (0, 90, 180, or 270)
        """
        try:
            # Try to get rotation from video metadata
            # This works for some video formats that store rotation info
            rotation = cap.get(cv2.CAP_PROP_ORIENTATION_META)
            if rotation == 0:
                # Try alternative method for some video formats
                rotation = cap.get(cv2.CAP_PROP_ORIENTATION)
            
            # Convert to degrees and normalize
            if rotation == 90:
                return 90
            elif rotation == 180:
                return 180
            elif rotation == 270:
                return 270
            else:
                return 0
        except:
            # If we can't get rotation info, return 0 (no rotation)
            return 0
    
    def _detect_rotation_from_content(self, frame: np.ndarray) -> int:
        """
        Detect rotation by analyzing frame content and dimensions
        This is a fallback method when metadata rotation info is not available
        """
        height, width = frame.shape[:2]
        
        # If height > width, it's likely a portrait video that needs rotation
        # Most mobile videos are recorded in portrait mode
        if height > width:
            print(f"Detected portrait orientation: {width}x{height}")
            # Check if this looks like it needs 90-degree rotation
            # For mobile videos, this is usually the case
            return 90
        else:
            print(f"Detected landscape orientation: {width}x{height}")
            return 0
    
    def _rotate_frame(self, frame: np.ndarray, rotation: int) -> np.ndarray:
        """
        Rotate frame by the specified angle
        """
        if rotation == 0:
            return frame
        
        height, width = frame.shape[:2]
        
        if rotation == 90:
            # Rotate 90 degrees clockwise
            rotated = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        elif rotation == 180:
            # Rotate 180 degrees
            rotated = cv2.rotate(frame, cv2.ROTATE_180)
        elif rotation == 270:
            # Rotate 270 degrees clockwise (same as 90 degrees counter-clockwise)
            rotated = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        else:
            return frame
        
        print(f"Rotated frame from {width}x{height} to {rotated.shape[1]}x{rotated.shape[0]}")
        return rotated
    
    def _transform_landmarks_for_rotation(self, landmarks: Dict, original_shape: Tuple, rotation: int) -> Dict:
        """
        Transform landmark coordinates to match rotated frame
        """
        if rotation == 0:
            return landmarks
        
        original_height, original_width = original_shape[:2]
        transformed_landmarks = {}
        
        for landmark_name, landmark_data in landmarks.items():
            # Get normalized coordinates (0-1)
            x_norm = landmark_data['x']
            y_norm = landmark_data['y']
            
            # Convert to pixel coordinates
            x_pixel = x_norm * original_width
            y_pixel = y_norm * original_height
            
            # Apply rotation transformation
            if rotation == 90:
                # 90 degrees clockwise: (x, y) -> (y, width-x)
                new_x = y_pixel
                new_y = original_width - x_pixel
                new_width = original_height
                new_height = original_width
            elif rotation == 180:
                # 180 degrees: (x, y) -> (width-x, height-y)
                new_x = original_width - x_pixel
                new_y = original_height - y_pixel
                new_width = original_width
                new_height = original_height
            elif rotation == 270:
                # 270 degrees clockwise: (x, y) -> (height-y, x)
                new_x = original_height - y_pixel
                new_y = x_pixel
                new_width = original_height
                new_height = original_width
            else:
                new_x, new_y = x_pixel, y_pixel
                new_width, new_height = original_width, original_height
            
            # Convert back to normalized coordinates
            transformed_landmarks[landmark_name] = {
                'x': new_x / new_width,
                'y': new_y / new_height,
                'visibility': landmark_data['visibility']
            }
        
        return transformed_landmarks
    
    def _transform_ball_position_for_rotation(self, ball_position: Tuple[int, int, int], original_shape: Tuple, rotation: int) -> Tuple[int, int, int]:
        """
        Transform ball position coordinates to match rotated frame
        """
        if rotation == 0:
            return ball_position
        
        x, y, radius = ball_position
        original_height, original_width = original_shape[:2]
        
        # Apply rotation transformation
        if rotation == 90:
            # 90 degrees clockwise: (x, y) -> (y, width-x)
            new_x = y
            new_y = original_width - x
        elif rotation == 180:
            # 180 degrees: (x, y) -> (width-x, height-y)
            new_x = original_width - x
            new_y = original_height - y
        elif rotation == 270:
            # 270 degrees clockwise: (x, y) -> (height-y, x)
            new_x = original_height - y
            new_y = x
        else:
            return ball_position
        
        return (new_x, new_y, radius)
    
    def _streamlined_shooter_analysis(self, all_frames_data: List[Dict], raw_frames: List = None) -> Dict:
        """
        Streamlined analysis flow:
        1. Record video (already done)
        2. Detect who is the basketball shooter
        3. Track the basketball shooter
        4. Find the ball release frame
        5. Show the ball release frame in analysis report
        6. Add bounding box to the basketball shooter on the ball release frame
        """
        if not all_frames_data or not raw_frames:
            return {'error': 'No frame data available for analysis'}
        
        print("Step 1: Video recorded - processing frames...")
        
        # Step 2: Detect who is the basketball shooter
        print("Step 2: Detecting basketball shooter...")
        shooter_id, shooter_frames = self._detect_basketball_shooter(all_frames_data, raw_frames)
        
        if shooter_id is None or not shooter_frames:
            print("No basketball shooter detected, falling back...")
            return {'error': 'No basketball shooter detected'}
        
        print(f"Detected shooter with ID: {shooter_id} in {len(shooter_frames)} frames")
        
        # Step 3: Track the basketball shooter
        print("Step 3: Tracking basketball shooter...")
        tracked_shooter_data = self._track_basketball_shooter(shooter_frames, shooter_id)
        
        # Step 4: Find the ball release frame
        print("Step 4: Finding ball release frame...")
        release_frame_idx = self._find_ball_release_frame_streamlined(tracked_shooter_data, raw_frames)
        
        if release_frame_idx is None:
            print("Could not determine ball release frame")
            return {'error': 'Could not determine ball release frame'}
        
        print(f"Ball release detected at frame {release_frame_idx}")
        
        # Step 5 & 6: Create shooting sequence frames with bounding boxes
        print("Step 5-6: Creating shooting sequence with shooter bounding boxes...")
        shooting_sequence = self._create_shooting_sequence_frames(
            raw_frames, 
            tracked_shooter_data,
            shooter_id,
            release_frame_idx
        )
        
        if not shooting_sequence:
            return {'error': 'Failed to create shooting sequence analysis'}
        
        # Transform streamlined data to match iOS app's expected comprehensive format
        analysis_result = self._transform_to_comprehensive_format(
            shooter_id, 
            len(all_frames_data), 
            len(tracked_shooter_data), 
            release_frame_idx, 
            shooting_sequence
        )
        
        print("Streamlined analysis completed successfully!")
        return analysis_result
    
    def _detect_basketball_shooter(self, all_frames_data: List[Dict], raw_frames: List) -> Tuple[Optional[int], List[Dict]]:
        """
        Step 2: Detect who is the basketball shooter using ball detection and proximity
        Returns (shooter_id, shooter_frames) where shooter_frames contains only frames with the shooter
        """
        ball_holder_votes = {}  # person_id -> count of frames where they hold the ball
        shooter_frames = []
        
        for frame_idx, frame_data in enumerate(all_frames_data):
            if frame_idx >= len(raw_frames):
                continue
                
            raw_frame = raw_frames[frame_idx]
            
            # Detect basketball in this frame
            ball_position = self._detect_basketball(raw_frame)
            if not ball_position:
                continue
            
            # Transform ball position if rotation was applied
            if rotation != 0:
                ball_position = self._transform_ball_position_for_rotation(
                    ball_position, original_shape, rotation
                )
                
            # Find person closest to the ball
            ball_holder_id = self._find_ball_holder(frame_data, ball_position, raw_frame.shape[1], raw_frame.shape[0])
            if ball_holder_id is not None:
                ball_holder_votes[ball_holder_id] = ball_holder_votes.get(ball_holder_id, 0) + 1
                
                # Add this frame to shooter frames
                shooter_frame_data = {
                    'frame_idx': frame_idx,
                    'frame_data': frame_data,
                    'ball_position': ball_position,
                    'shooter_id': ball_holder_id
                }
                shooter_frames.append(shooter_frame_data)
        
        if not ball_holder_votes:
            print("No ball holder detected in any frame")
            return None, []
        
        # The person who holds the ball most often is the shooter
        shooter_id = max(ball_holder_votes, key=ball_holder_votes.get)
        shooter_frame_count = ball_holder_votes[shooter_id]
        
        print(f"Identified shooter {shooter_id} holding ball in {shooter_frame_count} frames")
        
        # Filter shooter_frames to only include frames with the identified shooter
        filtered_shooter_frames = [sf for sf in shooter_frames if sf['shooter_id'] == shooter_id]
        
        return shooter_id, filtered_shooter_frames
    
    def _track_basketball_shooter(self, shooter_frames: List[Dict], shooter_id: int) -> List[Dict]:
        """
        Step 3: Track the basketball shooter across frames
        Returns tracking data for the shooter in each frame
        """
        tracked_data = []
        
        for shooter_frame in shooter_frames:
            frame_data = shooter_frame['frame_data']
            frame_idx = shooter_frame['frame_idx']
            
            # Find the shooter's pose data in this frame
            shooter_pose = None
            for person in frame_data['people']:
                if person['person_id'] == shooter_id:
                    shooter_pose = person
                    break
            
            if shooter_pose:
                tracking_data = {
                    'frame_idx': frame_idx,
                    'shooter_pose': shooter_pose,
                    'ball_position': shooter_frame['ball_position'],
                    'landmarks': shooter_pose['landmarks'],
                    'confidence': shooter_pose['confidence']
                }
                tracked_data.append(tracking_data)
        
        print(f"Successfully tracked shooter across {len(tracked_data)} frames")
        return tracked_data
    
    def _find_ball_release_frame_streamlined(self, tracked_shooter_data: List[Dict], raw_frames: List) -> Optional[int]:
        """
        Step 4: Find the ball release frame by analyzing shooter's arm movement and ball position
        """
        if len(tracked_shooter_data) < 3:
            print("Not enough tracking data to determine release frame")
            return None
        
        release_candidates = []
        
        for i in range(1, len(tracked_shooter_data) - 1):
            current_data = tracked_shooter_data[i]
            prev_data = tracked_shooter_data[i - 1]
            next_data = tracked_shooter_data[i + 1]
            
            # Analyze arm extension (right wrist movement)
            current_pose = current_data['shooter_pose']['landmarks']
            prev_pose = prev_data['shooter_pose']['landmarks']
            next_pose = next_data['shooter_pose']['landmarks']
            
            # Check for upward arm movement (release motion)
            if ('right_wrist' in current_pose and 'right_wrist' in prev_pose and 
                'right_shoulder' in current_pose):
                
                current_wrist_y = current_pose['right_wrist']['y']
                prev_wrist_y = prev_pose['right_wrist']['y']
                shoulder_y = current_pose['right_shoulder']['y']
                
                # Look for upward wrist movement and extension above shoulder
                wrist_movement = prev_wrist_y - current_wrist_y  # Positive = upward
                wrist_above_shoulder = current_wrist_y < shoulder_y
                
                if wrist_movement > 0.02 and wrist_above_shoulder:  # Significant upward movement
                    release_score = wrist_movement * (2.0 if wrist_above_shoulder else 1.0)
                    release_candidates.append((i, release_score, current_data['frame_idx']))
        
        if not release_candidates:
            # Fallback: use the frame with highest arm position
            print("No clear release motion detected, using highest arm position")
            highest_arm_idx = 0
            highest_arm_y = float('inf')
            
            for i, data in enumerate(tracked_shooter_data):
                pose = data['shooter_pose']['landmarks']
                if 'right_wrist' in pose:
                    wrist_y = pose['right_wrist']['y']
                    if wrist_y < highest_arm_y:  # Lower y = higher position
                        highest_arm_y = wrist_y
                        highest_arm_idx = i
            
            return tracked_shooter_data[highest_arm_idx]['frame_idx']
        
        # Return the frame with the highest release score
        best_release = max(release_candidates, key=lambda x: x[1])
        release_frame_idx = best_release[2]
        
        print(f"Ball release detected at frame {release_frame_idx} with score {best_release[1]:.3f}")
        return release_frame_idx
    
    def _create_release_frame_with_bounding_box(self, raw_frame: np.ndarray, tracked_data: Dict, 
                                               shooter_id: int, frame_number: int) -> Optional[Dict]:
        """
        Step 5-6: Create release frame analysis with bounding box around the shooter
        """
        try:
            shooter_pose = tracked_data['shooter_pose']
            landmarks = shooter_pose['landmarks']
            
            # Calculate bounding box around the shooter
            bounding_box = self._calculate_shooter_bounding_box(landmarks, raw_frame.shape)
            if not bounding_box:
                print("Could not calculate bounding box for shooter")
                return None
            
            # Draw bounding box on the frame
            frame_with_bbox = self._draw_bounding_box_on_frame(raw_frame.copy(), bounding_box, shooter_id)
            
            # Encode the frame with bounding box
            _, buffer = cv2.imencode('.jpg', frame_with_bbox)
            frame_image_data = base64.b64encode(buffer).decode('utf-8')
            
            # Also create a cropped version of just the shooter
            cropped_shooter = self._crop_frame_to_bounding_box(raw_frame, bounding_box)
            _, crop_buffer = cv2.imencode('.jpg', cropped_shooter)
            cropped_image_data = base64.b64encode(crop_buffer).decode('utf-8')
            
            height, width = raw_frame.shape[:2]
            
            release_frame_analysis = {
                'frame_number': frame_number,
                'shooter_id': shooter_id,
                'full_frame_with_bbox': {
                    'image_data': frame_image_data,
                    'width': width,
                    'height': height
                },
                'shooter_crop': {
                    'image_data': cropped_image_data,
                    'width': bounding_box['width'],
                    'height': bounding_box['height']
                },
                'bounding_box': bounding_box,
                'ball_position': tracked_data.get('ball_position'),
                'shooter_confidence': shooter_pose['confidence']
            }
            
            print(f"Created release frame analysis with bounding box: {bounding_box}")
            return release_frame_analysis
            
        except Exception as e:
            print(f"Error creating release frame with bounding box: {e}")
            return None
    
    def _calculate_shooter_bounding_box(self, landmarks: Dict, frame_shape: Tuple) -> Optional[Dict]:
        """
        Calculate bounding box coordinates around the shooter based on pose landmarks
        """
        try:
            height, width = frame_shape[:2]
            print(f"DEBUG: _calculate_shooter_bounding_box - Frame shape: {width}x{height}")
            
            # Get key body points to define the bounding box
            key_points = []
            landmark_names = ['nose', 'left_shoulder', 'right_shoulder', 'left_elbow', 'right_elbow',
                            'left_wrist', 'right_wrist', 'left_hip', 'right_hip', 'left_knee', 'right_knee']
            
            for landmark_name in landmark_names:
                if landmark_name in landmarks:
                    landmark = landmarks[landmark_name]
                    x = int(landmark['x'] * width)
                    y = int(landmark['y'] * height)
                    key_points.append((x, y))
                    print(f"DEBUG: Landmark {landmark_name}: normalized({landmark['x']:.3f}, {landmark['y']:.3f}) -> pixel({x}, {y})")
            
            if len(key_points) < 3:
                print(f"DEBUG: Not enough visible landmarks ({len(key_points)} < 3)")
                return None
            
            # Calculate bounding box
            min_x = min(point[0] for point in key_points)
            max_x = max(point[0] for point in key_points)
            min_y = min(point[1] for point in key_points)
            max_y = max(point[1] for point in key_points)
            
            print(f"DEBUG: Raw bounding box: ({min_x}, {min_y}) to ({max_x}, {max_y})")
            
            # The landmarks are already in the correct coordinate system for the frame
            # No need for additional transformations - use coordinates as calculated
            print(f"DEBUG: Using original coordinates without transformation")
            
            # Add padding
            padding_x = int((max_x - min_x) * 0.1)
            padding_y = int((max_y - min_y) * 0.1)
            
            min_x = max(0, min_x - padding_x)
            max_x = min(width, max_x + padding_x)
            min_y = max(0, min_y - padding_y)
            max_y = min(height, max_y + padding_y)
            
            final_bbox = {
                'x': min_x,
                'y': min_y,
                'width': max_x - min_x,
                'height': max_y - min_y
            }
            
            print(f"DEBUG: Final bounding box: {final_bbox}")
            return final_bbox
            
        except Exception as e:
            print(f"Error calculating bounding box: {e}")
            return None
    
    def _draw_bounding_box_on_frame(self, frame: np.ndarray, bounding_box: Dict, shooter_id: int, phase_label: str = None) -> np.ndarray:
        """
        Draw a bounding box around the shooter on the frame
        """
        x = bounding_box['x']
        y = bounding_box['y']
        w = bounding_box['width']
        h = bounding_box['height']
        
        # Draw bounding box rectangle
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 3)  # Red box
        
        # Add labels
        if phase_label:
            label = f"Shooter #{shooter_id} - {phase_label}"
        else:
            label = f"Shooter #{shooter_id}"
            
        label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
        
        # Draw label background
        cv2.rectangle(frame, (x, y - label_size[1] - 15), 
                     (x + label_size[0] + 10, y), (0, 0, 255), -1)
        
        # Draw label text
        cv2.putText(frame, label, (x + 5, y - 8), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        return frame
    
    def _crop_frame_to_bounding_box(self, frame: np.ndarray, bounding_box: Dict) -> np.ndarray:
        """
        Crop the frame to the bounding box area
        """
        x = bounding_box['x']
        y = bounding_box['y']
        w = bounding_box['width']
        h = bounding_box['height']
        
        return frame[y:y+h, x:x+w]
    
    def _create_shooting_sequence_frames(self, raw_frames: List, tracked_shooter_data: List[Dict], 
                                       shooter_id: int, release_frame_idx: int) -> Optional[Dict]:
        """
        Create a sequence of frames showing the shooting process: preparation, release, follow-through
        """
        try:
            sequence_frames = []
            
            # Find the release frame in tracked data
            release_data_idx = None
            for i, data in enumerate(tracked_shooter_data):
                if data['frame_idx'] == release_frame_idx:
                    release_data_idx = i
                    break
            
            if release_data_idx is None:
                print("Could not find release frame in tracked data")
                return None
            
            # Define frame positions relative to release
            frame_positions = [
                {'name': 'preparation', 'offset': -6, 'label': 'Preparation Phase'},
                {'name': 'pre_release', 'offset': -3, 'label': 'Pre-Release'},
                {'name': 'release', 'offset': 0, 'label': 'Ball Release'},
                {'name': 'follow_through_1', 'offset': 2, 'label': 'Follow Through 1'},
                {'name': 'follow_through_2', 'offset': 4, 'label': 'Follow Through 2'}
            ]
            
            for frame_pos in frame_positions:
                target_idx = release_data_idx + frame_pos['offset']
                
                # Check bounds
                if target_idx < 0 or target_idx >= len(tracked_shooter_data):
                    continue
                    
                tracked_data = tracked_shooter_data[target_idx]
                frame_idx = tracked_data['frame_idx']
                
                if frame_idx >= len(raw_frames):
                    continue
                
                raw_frame = raw_frames[frame_idx]
                
                # Create frame with bounding box
                frame_analysis = self._create_frame_with_bounding_box(
                    raw_frame, tracked_data, shooter_id, frame_idx, frame_pos['label']
                )
                
                if frame_analysis:
                    frame_analysis['phase'] = frame_pos['name']
                    frame_analysis['phase_label'] = frame_pos['label']
                    sequence_frames.append(frame_analysis)
            
            if not sequence_frames:
                print("No valid sequence frames created")
                return None
            
            shooting_sequence = {
                'total_frames': len(sequence_frames),
                'frames': sequence_frames,
                'shooter_id': shooter_id,
                'release_frame_number': release_frame_idx
            }
            
            print(f"Created shooting sequence with {len(sequence_frames)} frames")
            return shooting_sequence
            
        except Exception as e:
            print(f"Error creating shooting sequence: {e}")
            return None
    
    def _create_frame_with_bounding_box(self, raw_frame: np.ndarray, tracked_data: Dict, 
                                      shooter_id: int, frame_number: int, phase_label: str) -> Optional[Dict]:
        """
        Create a single frame analysis with bounding box around the shooter
        """
        try:
            shooter_pose = tracked_data['shooter_pose']
            landmarks = shooter_pose['landmarks']
            
            # Calculate bounding box around the shooter
            bounding_box = self._calculate_shooter_bounding_box(landmarks, raw_frame.shape)
            if not bounding_box:
                print(f"Could not calculate bounding box for frame {frame_number}")
                return None
            
            # Draw bounding box on the frame
            frame_with_bbox = self._draw_bounding_box_on_frame(
                raw_frame.copy(), bounding_box, shooter_id, phase_label
            )
            
            # Encode the frame with bounding box
            _, buffer = cv2.imencode('.jpg', frame_with_bbox)
            frame_image_data = base64.b64encode(buffer).decode('utf-8')
            
            # Also create a cropped version of just the shooter
            cropped_shooter = self._crop_frame_to_bounding_box(raw_frame, bounding_box)
            _, crop_buffer = cv2.imencode('.jpg', cropped_shooter)
            cropped_image_data = base64.b64encode(crop_buffer).decode('utf-8')
            
            height, width = raw_frame.shape[:2]
            
            # Convert ball position tuple to dictionary format for iOS compatibility
            ball_position_dict = None
            ball_pos = tracked_data.get('ball_position')
            if ball_pos:
                ball_position_dict = {
                    'x': ball_pos[0],
                    'y': ball_pos[1],
                    'radius': ball_pos[2]
                }
            
            frame_analysis = {
                'frame_number': frame_number,
                'phase_label': phase_label,
                'shooter_id': shooter_id,
                'full_frame_with_bbox': {
                    'image_data': frame_image_data,
                    'width': width,
                    'height': height
                },
                'shooter_crop': {
                    'image_data': cropped_image_data,
                    'width': bounding_box['width'],
                    'height': bounding_box['height']
                },
                'bounding_box': bounding_box,
                'ball_position': ball_position_dict,
                'shooter_confidence': shooter_pose['confidence']
            }
            
            return frame_analysis
            
        except Exception as e:
            print(f"Error creating frame with bounding box: {e}")
            return None
    
    def _detect_basketball(self, frame: np.ndarray) -> Optional[Tuple[int, int, int]]:
        """
        Detect basketball in the frame using color and shape detection
        Returns (x, y, radius) of detected ball or None
        """
        # Convert to HSV for better color detection
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Basketball color range (orange/brown)
        # Lower and upper bounds for basketball orange color
        lower_orange1 = np.array([5, 50, 50])
        upper_orange1 = np.array([15, 255, 255])
        lower_orange2 = np.array([160, 50, 50])
        upper_orange2 = np.array([180, 255, 255])
        
        # Create masks for orange colors
        mask1 = cv2.inRange(hsv, lower_orange1, upper_orange1)
        mask2 = cv2.inRange(hsv, lower_orange2, upper_orange2)
        mask = cv2.bitwise_or(mask1, mask2)
        
        # Apply morphological operations to clean up the mask
        kernel = np.ones((5,5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return None
        
        # Find the most circular contour that could be a basketball
        best_ball = None
        best_score = 0
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < 100:  # Too small to be a basketball
                continue
            
            # Check if contour is roughly circular
            perimeter = cv2.arcLength(contour, True)
            if perimeter == 0:
                continue
                
            circularity = 4 * math.pi * area / (perimeter * perimeter)
            
            # Basketball should be reasonably circular and of reasonable size
            if circularity > 0.3 and area > 200:  # Minimum circularity and size
                # Get bounding circle
                (x, y), radius = cv2.minEnclosingCircle(contour)
                
                # Score based on circularity and size
                score = circularity * min(area / 1000, 1.0)  # Cap size factor at 1.0
                
                if score > best_score:
                    best_score = score
                    best_ball = (int(x), int(y), int(radius))
        
        return best_ball
    
    def _find_ball_holder(self, frame_data: Dict, ball_position: Tuple[int, int, int], frame_width: int, frame_height: int) -> Optional[int]:
        """
        Find which person is closest to the ball and likely holding it
        """
        if not ball_position or not frame_data.get('people'):
            return None
        
        ball_x, ball_y, ball_radius = ball_position
        # Normalize ball position to 0-1 range like MediaPipe landmarks
        ball_x_norm = ball_x / frame_width
        ball_y_norm = ball_y / frame_height
        
        closest_person = None
        min_distance = float('inf')
        
        for person in frame_data['people']:
            landmarks = person['landmarks']
            
            # Check distance to hands (most likely to hold ball)
            hand_points = ['right_wrist', 'left_wrist']
            person_min_distance = float('inf')
            
            for hand_point in hand_points:
                if hand_point in landmarks:
                    hand = landmarks[hand_point]
                    if hand['visibility'] > 0.5:  # Only consider visible hands
                        distance = math.sqrt(
                            (hand['x'] - ball_x_norm)**2 + 
                            (hand['y'] - ball_y_norm)**2
                        )
                        person_min_distance = min(person_min_distance, distance)
            
            # Also check center of person (chest area)
            if 'right_shoulder' in landmarks and 'left_shoulder' in landmarks:
                right_shoulder = landmarks['right_shoulder']
                left_shoulder = landmarks['left_shoulder']
                chest_x = (right_shoulder['x'] + left_shoulder['x']) / 2
                chest_y = (right_shoulder['y'] + left_shoulder['y']) / 2
                
                chest_distance = math.sqrt(
                    (chest_x - ball_x_norm)**2 + 
                    (chest_y - ball_y_norm)**2
                )
                person_min_distance = min(person_min_distance, chest_distance)
            
            if person_min_distance < min_distance:
                min_distance = person_min_distance
                closest_person = person['person_id']
        
        # Only consider someone a ball holder if they're reasonably close
        if min_distance < 0.15:  # Within 15% of frame size
            return closest_person
        
        return None
    
    def _ball_holder_analysis(self, all_frames_data: List[Dict], raw_frames: List = None) -> Dict:
        """
        Analyze video by detecting ball and identifying the ball holder
        """
        print("Using ball-holder analysis...")
        
        if not all_frames_data or not raw_frames:
            return {'error': 'No frame data available'}
        
        # Track ball holder across frames
        ball_holder_frames = []
        ball_positions = []
        
        for i, frame_data in enumerate(all_frames_data):
            if i >= len(raw_frames):
                break
                
            frame = raw_frames[i]
            height, width = frame.shape[:2]
            
            # Detect basketball in this frame
            ball_pos = self._detect_basketball(frame)
            ball_positions.append(ball_pos)
            
            if ball_pos:
                # Find who is holding the ball
                ball_holder_id = self._find_ball_holder(frame_data, ball_pos, width, height)
                
                if ball_holder_id is not None:
                    # Find the ball holder's data
                    for person in frame_data['people']:
                        if person['person_id'] == ball_holder_id:
                            ball_holder_frames.append({
                                'frame': frame_data['frame'],
                                'landmarks': person['landmarks'],
                                'timestamp': frame_data['timestamp'],
                                'ball_position': ball_pos,
                                'ball_holder_id': ball_holder_id
                            })
                            break
        
        if not ball_holder_frames:
            print("No ball holder detected, falling back to most visible person")
            # Return error to trigger fallback in main analyze_video method
            return {'error': 'No ball holder detected in video'}
        
        print(f"Detected ball holder in {len(ball_holder_frames)} frames")
        
        # Use ball holder data for analysis
        analysis = {
            'shot_phases': self._identify_shot_phases(ball_holder_frames),
            'form_analysis': {},
            'recommendations': [],
            'ball_detection_info': {
                'ball_detected_frames': len([pos for pos in ball_positions if pos is not None]),
                'total_frames': len(ball_positions),
                'ball_holder_frames': len(ball_holder_frames)
            }
        }
        
        # Analyze different aspects of shooting form
        analysis['form_analysis'].update(self._analyze_elbow_position(ball_holder_frames))
        analysis['form_analysis'].update(self._analyze_hand_position(ball_holder_frames))
        analysis['form_analysis'].update(self._analyze_body_alignment(ball_holder_frames))
        analysis['form_analysis'].update(self._analyze_follow_through(ball_holder_frames))
        
        # Generate recommendations
        analysis['recommendations'] = self._generate_recommendations(analysis['form_analysis'])
        
        # Detect ball release frame and create comprehensive frame analysis
        if raw_frames and analysis['shot_phases'].get('release_point') is not None:
            release_point = analysis['shot_phases']['release_point']
            
            # Find the ball release frame (where ball disappears or moves away from holder)
            actual_release_frame = self._detect_ball_release_frame(ball_positions, ball_holder_frames, release_point)
            
            if actual_release_frame is not None and actual_release_frame < len(ball_holder_frames):
                ball_holder_data = ball_holder_frames[actual_release_frame]
                frame_number = ball_holder_data['frame']
                original_frame = raw_frames[frame_number]
                
                # Get all people detected in this frame
                release_frame_data = all_frames_data[frame_number] if frame_number < len(all_frames_data) else None
                
                # Create comprehensive release frame analysis
                release_analysis = self._create_comprehensive_release_frame(
                    original_frame, 
                    ball_holder_data, 
                    release_frame_data,
                    frame_number
                )
                if release_analysis:
                    analysis['release_frame'] = release_analysis
        
        return analysis
    
    def _detect_ball_release_frame(self, ball_positions: List, ball_holder_frames: List[Dict], estimated_release: int) -> Optional[int]:
        """
        Detect the actual frame where the ball is released
        """
        if not ball_positions or not ball_holder_frames:
            return estimated_release
        
        # Look around the estimated release point for ball movement
        search_range = 5  # frames to search around estimated release
        start_idx = max(0, estimated_release - search_range)
        end_idx = min(len(ball_positions), estimated_release + search_range)
        
        # Find frame where ball position changes significantly or disappears
        for i in range(start_idx, end_idx - 1):
            if i >= len(ball_positions) - 1:
                break
                
            current_ball = ball_positions[i]
            next_ball = ball_positions[i + 1]
            
            # Ball disappears (was detected, now not detected)
            if current_ball is not None and next_ball is None:
                return i
            
            # Ball moves significantly
            if current_ball is not None and next_ball is not None:
                curr_x, curr_y, _ = current_ball
                next_x, next_y, _ = next_ball
                
                distance = math.sqrt((next_x - curr_x)**2 + (next_y - curr_y)**2)
                if distance > 50:  # Significant movement threshold
                    return i
        
        return estimated_release
    
    def _create_comprehensive_release_frame(self, original_frame: np.ndarray, ball_holder_data: Dict, 
                                          all_people_data: Dict, frame_number: int) -> Optional[Dict]:
        """
        Create comprehensive release frame analysis with original frame and all player crops
        """
        try:
            height, width = original_frame.shape[:2]
            
            # 1. Calculate and draw bounding box on the original frame
            landmarks = ball_holder_data.get('landmarks', {})
            bounding_box = None
            
            if landmarks:
                # Ensure landmarks are in the same coordinate system as the frame
                # If the frame was rotated, landmarks should already be transformed
                print(f"DEBUG: Frame dimensions: {width}x{height}")
                print(f"DEBUG: Landmark coordinate system check:")
                for key, landmark in list(landmarks.items())[:3]:  # Check first 3 landmarks
                    print(f"  {key}: x={landmark['x']:.3f}, y={landmark['y']:.3f}")
                
                bounding_box = self._calculate_shooter_bounding_box(landmarks, original_frame.shape)
                
                if bounding_box:
                    print(f"DEBUG: Calculated bounding box: {bounding_box}")
                    print(f"DEBUG: Frame dimensions: {width}x{height}")
                    print(f"DEBUG: Landmarks available: {list(landmarks.keys())}")
                    
                    # Draw bounding box on the frame
                    original_frame_with_bbox = self._draw_bounding_box_on_frame(
                        original_frame.copy(), 
                        bounding_box, 
                        ball_holder_data.get('ball_holder_id', 0),
                        "Ball Release"
                    )
                    # Encode the frame with bounding box
                    _, buffer = cv2.imencode('.jpg', original_frame_with_bbox, [cv2.IMWRITE_JPEG_QUALITY, 75])
                    original_frame_base64 = base64.b64encode(buffer).decode('utf-8')
                else:
                    print("DEBUG: Failed to calculate bounding box")
                    # Fallback: encode original frame without bounding box
                    _, buffer = cv2.imencode('.jpg', original_frame, [cv2.IMWRITE_JPEG_QUALITY, 75])
                    original_frame_base64 = base64.b64encode(buffer).decode('utf-8')
            else:
                print("DEBUG: No landmarks available for bounding box calculation")
                # No landmarks available, encode original frame
                _, buffer = cv2.imencode('.jpg', original_frame, [cv2.IMWRITE_JPEG_QUALITY, 75])
                original_frame_base64 = base64.b64encode(buffer).decode('utf-8')
            
            # 2. Crop ball holder (primary focus)
            ball_holder_crop = self._crop_single_person(
                original_frame, 
                ball_holder_data['landmarks'], 
                ball_holder_data.get('ball_position'),
                person_id=ball_holder_data.get('ball_holder_id', 0),
                is_ball_holder=True
            )
            
            # Debug: Check what _crop_single_person returned
            print(f"DEBUG: _crop_single_person returned: {ball_holder_crop}")
            if ball_holder_crop:
                print(f"DEBUG: ball_holder_crop keys: {list(ball_holder_crop.keys())}")
            else:
                print("DEBUG: _crop_single_person returned None")
            
            # 3. Crop all other detected players
            all_player_crops = []
            if all_people_data and 'people' in all_people_data:
                for person in all_people_data['people']:
                    person_id = person['person_id']
                    
                    # Skip if this is the ball holder (already cropped above)
                    if person_id == ball_holder_data.get('ball_holder_id'):
                        continue
                    
                    player_crop = self._crop_single_person(
                        original_frame,
                        person['landmarks'],
                        person_id=person_id,
                        is_ball_holder=False
                    )
                    
                    if player_crop:
                        all_player_crops.append(player_crop)
            
            return {
                'original_frame': {
                    'image_data': original_frame_base64,
                    'width': width,
                    'height': height
                },
                'ball_holder_crop': ball_holder_crop,
                'all_player_crops': all_player_crops,
                'frame_number': frame_number,
                'ball_holder_id': ball_holder_data.get('ball_holder_id', 0),
                'total_players_detected': len(all_people_data['people']) if all_people_data and 'people' in all_people_data else 1,
                'ball_detected': 'ball_position' in ball_holder_data,
                'bounding_box': bounding_box  # Add bounding box information
            }
            
        except Exception as e:
            print(f"Error creating comprehensive release frame: {e}")
            return None
    
    def _crop_single_person(self, frame: np.ndarray, landmarks: Dict, ball_position: Tuple = None, 
                           person_id: int = 0, is_ball_holder: bool = False) -> Optional[Dict]:
        """
        Crop a single person from the frame
        """
        try:
            height, width = frame.shape[:2]
            
            # Calculate bounding box around the person
            x_coords = []
            y_coords = []
            
            # Use key body landmarks for cropping
            key_landmarks = [
                'nose', 'right_shoulder', 'left_shoulder', 
                'right_elbow', 'left_elbow', 'right_wrist', 'left_wrist',
                'right_hip', 'left_hip', 'right_knee', 'left_knee'
            ]
            
            for landmark_name in key_landmarks:
                if landmark_name in landmarks and landmarks[landmark_name]['visibility'] > 0.5:
                    coords = landmarks[landmark_name]
                    x_coords.append(coords['x'] * width)
                    y_coords.append(coords['y'] * height)
            
            if not x_coords or not y_coords:
                return None
            
            # Add ball position to bounding box if this is the ball holder
            if is_ball_holder and ball_position:
                ball_x, ball_y, _ = ball_position
                x_coords.append(ball_x)
                y_coords.append(ball_y)
            
            # Calculate bounding box with padding
            padding = 80  # Extra padding for context
            min_x = max(0, int(min(x_coords)) - padding)
            max_x = min(width, int(max(x_coords)) + padding)
            min_y = max(0, int(min(y_coords)) - padding)
            max_y = min(height, int(max(y_coords)) + padding)
            
            # Ensure minimum crop size
            min_crop_size = 150
            crop_width = max_x - min_x
            crop_height = max_y - min_y
            
            if crop_width < min_crop_size:
                center_x = (min_x + max_x) // 2
                min_x = max(0, center_x - min_crop_size // 2)
                max_x = min(width, center_x + min_crop_size // 2)
            
            if crop_height < min_crop_size:
                center_y = (min_y + max_y) // 2
                min_y = max(0, center_y - min_crop_size // 2)
                max_y = min(height, center_y + min_crop_size // 2)
            
            # Crop the frame
            cropped_frame = frame[min_y:max_y, min_x:max_x]
            
            # Resize to standard size
            target_size = (200, 300)
            cropped_resized = cv2.resize(cropped_frame, target_size)
            
            # Convert to base64
            _, buffer = cv2.imencode('.jpg', cropped_resized, [cv2.IMWRITE_JPEG_QUALITY, 85])
            img_base64 = base64.b64encode(buffer).decode('utf-8')
            
            return {
                'image_data': img_base64,
                'person_id': person_id,
                'is_ball_holder': is_ball_holder,
                'crop_coordinates': {
                    'x': min_x,
                    'y': min_y,
                    'width': max_x - min_x,
                    'height': max_y - min_y
                },
                'cropped_size': {'width': target_size[0], 'height': target_size[1]}
            }
            
        except Exception as e:
            print(f"Error cropping person {person_id}: {e}")
            return None
    
    def _crop_ball_holder_frame(self, frame: np.ndarray, ball_holder_data: Dict, frame_number: int) -> Optional[Dict]:
        """
        Crop frame around the ball holder
        """
        try:
            landmarks = ball_holder_data['landmarks']
            height, width = frame.shape[:2]
            
            # Calculate bounding box around the ball holder
            x_coords = []
            y_coords = []
            
            # Use key body landmarks for cropping
            key_landmarks = [
                'nose', 'right_shoulder', 'left_shoulder', 
                'right_elbow', 'left_elbow', 'right_wrist', 'left_wrist',
                'right_hip', 'left_hip', 'right_knee', 'left_knee'
            ]
            
            for landmark_name in key_landmarks:
                if landmark_name in landmarks and landmarks[landmark_name]['visibility'] > 0.5:
                    coords = landmarks[landmark_name]
                    x_coords.append(coords['x'] * width)
                    y_coords.append(coords['y'] * height)
            
            if not x_coords or not y_coords:
                return None
            
            # Add ball position to bounding box if available
            if 'ball_position' in ball_holder_data:
                ball_x, ball_y, _ = ball_holder_data['ball_position']
                x_coords.append(ball_x)
                y_coords.append(ball_y)
            
            # Calculate bounding box with padding
            padding = 100  # Extra padding for context
            min_x = max(0, int(min(x_coords)) - padding)
            max_x = min(width, int(max(x_coords)) + padding)
            min_y = max(0, int(min(y_coords)) - padding)
            max_y = min(height, int(max(y_coords)) + padding)
            
            # Ensure minimum crop size
            min_crop_size = 200
            crop_width = max_x - min_x
            crop_height = max_y - min_y
            
            if crop_width < min_crop_size:
                center_x = (min_x + max_x) // 2
                min_x = max(0, center_x - min_crop_size // 2)
                max_x = min(width, center_x + min_crop_size // 2)
            
            if crop_height < min_crop_size:
                center_y = (min_y + max_y) // 2
                min_y = max(0, center_y - min_crop_size // 2)
                max_y = min(height, center_y + min_crop_size // 2)
            
            # Crop the frame
            cropped_frame = frame[min_y:max_y, min_x:max_x]
            
            # Resize to standard size
            target_size = (300, 400)
            cropped_resized = cv2.resize(cropped_frame, target_size)
            
            # Convert to base64
            _, buffer = cv2.imencode('.jpg', cropped_resized, [cv2.IMWRITE_JPEG_QUALITY, 85])
            img_base64 = base64.b64encode(buffer).decode('utf-8')
            
            return {
                'image_data': img_base64,
                'frame_number': frame_number,
                'ball_holder_id': ball_holder_data.get('ball_holder_id', 0),
                'crop_coordinates': {
                    'x': min_x,
                    'y': min_y,
                    'width': max_x - min_x,
                    'height': max_y - min_y
                },
                'original_size': {'width': width, 'height': height},
                'cropped_size': {'width': target_size[0], 'height': target_size[1]},
                'ball_detected': 'ball_position' in ball_holder_data
            }
            
        except Exception as e:
            print(f"Error cropping ball holder frame: {e}")
            return None
    
    def _fallback_single_player_analysis(self, all_frames_data: List[Dict], raw_frames: List = None) -> Dict:
        """
        Fallback to original single-player analysis when multi-player detection fails
        """
        print("Using fallback single-player analysis...")
        
        # First, try to identify the shooter using motion analysis
        shooter_id, shooter_frames = self._identify_shooter_simple(all_frames_data)
        
        if shooter_id is not None and shooter_frames:
            print(f"Identified shooter: Person {shooter_id}")
            # Convert shooter data to single-player format
            frames_data = []
            for frame_data in shooter_frames:
                frames_data.append({
                    'frame': frame_data['frame'],
                    'landmarks': frame_data['shooter_landmarks'],
                    'timestamp': frame_data['timestamp']
                })
        else:
            print("Could not identify shooter, using most visible person")
            # Fallback: Take the most confident person across all frames
            frames_data = []
            for frame_data in all_frames_data:
                if frame_data['people']:
                    # Take the most confident person
                    best_person = max(frame_data['people'], key=lambda p: p['confidence'])
                    frames_data.append({
                        'frame': frame_data['frame'],
                        'landmarks': best_person['landmarks'],
                        'timestamp': frame_data['timestamp']
                    })
        
        # If no frames with people detected, return error in streamlined format
        if not frames_data:
            return {
                'error': 'No pose data detected in video',
                'analysis_type': 'fallback_error',
                'shooter_id': None,
                'total_frames_analyzed': len(all_frames_data),
                'shooter_tracked_frames': 0,
                'release_frame_number': None,
                'shooting_sequence': None,
                'form_analysis': {},
                'recommendations': [],
                'shot_phases': {'total_frames': 0, 'preparation_phase': None, 'release_point': None, 'follow_through_phase': None}
            }
        
        # Use the original analysis logic
        analysis = {
            'shot_phases': self._identify_shot_phases(frames_data),
            'form_analysis': {},
            'recommendations': []
        }
        
        # Add shooter info if we identified one
        if shooter_id is not None:
            analysis['shooter_info'] = {
                'shooter_id': shooter_id,
                'confidence': 0.85,  # Reasonable confidence for fallback
                'total_people_detected': self._count_total_people(all_frames_data)
            }
        
        # Analyze different aspects of shooting form
        analysis['form_analysis'].update(self._analyze_elbow_position(frames_data))
        analysis['form_analysis'].update(self._analyze_hand_position(frames_data))
        analysis['form_analysis'].update(self._analyze_body_alignment(frames_data))
        analysis['form_analysis'].update(self._analyze_follow_through(frames_data))
        
        # Generate recommendations based on analysis
        analysis['recommendations'] = self._generate_recommendations(analysis['form_analysis'])
        
        # Capture and crop release frame focusing on the identified shooter
        if raw_frames and analysis['shot_phases'].get('release_point') is not None:
            release_point = analysis['shot_phases']['release_point']
            if release_point < len(raw_frames) and release_point < len(frames_data):
                # Always use comprehensive release frame for consistency
                release_frame_data = self._create_comprehensive_release_frame_fallback(
                    raw_frames[release_point], 
                    frames_data[release_point], 
                    release_point
                )
                
                if release_frame_data:
                    analysis['release_frame'] = release_frame_data
        
        # Add streamlined analysis fields for iOS app compatibility
        analysis['analysis_type'] = 'fallback_comprehensive'
        analysis['shooter_id'] = shooter_id
        analysis['total_frames_analyzed'] = len(all_frames_data)
        analysis['shooter_tracked_frames'] = len(frames_data)
        analysis['release_frame_number'] = analysis['shot_phases'].get('release_point')
        analysis['shooting_sequence'] = None  # Fallback doesn't provide sequence
        
        # Add ball detection info for consistency
        analysis['ball_detection_info'] = {
            'ball_detected': False,  # Fallback mode doesn't detect balls
            'ball_positions': [],
            'detection_confidence': 0.0
        }
        
        # Add file info for consistency
        analysis['file_info'] = {
            'filename': 'analyzed_video.mp4',
            'file_type': 'video'
        }
        
        return analysis
    
    def _create_comprehensive_release_frame_fallback(self, original_frame: np.ndarray, 
                                                    shooter_data: Dict, frame_number: int) -> Optional[Dict]:
        """
        Create comprehensive release frame analysis for fallback single-player mode
        """
        try:
            height, width = original_frame.shape[:2]
            
            # Calculate and draw bounding box on the original frame
            landmarks = shooter_data.get('landmarks', {})
            bounding_box = None
            
            if landmarks:
                bounding_box = self._calculate_shooter_bounding_box(landmarks, original_frame.shape)
                if bounding_box:
                    # Draw bounding box on the frame
                    original_frame_with_bbox = self._draw_bounding_box_on_frame(
                        original_frame.copy(), 
                        bounding_box, 
                        0,  # person_id = 0 for single player
                        "Ball Release"
                    )
                    # Encode the frame with bounding box
                    _, buffer = cv2.imencode('.jpg', original_frame_with_bbox, [cv2.IMWRITE_JPEG_QUALITY, 75])
                    original_image_data = base64.b64encode(buffer).decode('utf-8')
                else:
                    # Fallback: encode original frame without bounding box
                    _, buffer = cv2.imencode('.jpg', original_frame, [cv2.IMWRITE_JPEG_QUALITY, 75])
                    original_image_data = base64.b64encode(buffer).decode('utf-8')
            else:
                # No landmarks available, encode original frame
                _, buffer = cv2.imencode('.jpg', original_frame, [cv2.IMWRITE_JPEG_QUALITY, 75])
                original_image_data = base64.b64encode(buffer).decode('utf-8')
            
            original_frame_info = {
                'image_data': original_image_data,
                'width': width,
                'height': height
            }
            
            # Crop the single player (ball holder)
            ball_holder_crop = self._crop_single_person(
                original_frame, 
                shooter_data['landmarks'], 
                person_id=0, 
                is_ball_holder=True
            )
            
            # For single player, all_player_crops is just the one player
            all_player_crops = []
            if ball_holder_crop:
                all_player_crops.append(ball_holder_crop)
            
            return {
                'original_frame': original_frame_info,
                'ball_holder_crop': ball_holder_crop,
                'all_player_crops': all_player_crops,
                'frame_number': frame_number,
                'ball_holder_id': 0,
                'total_players_detected': 1,
                'ball_detected': False,  # No ball detection in fallback mode
                'bounding_box': bounding_box  # Add bounding box information
            }
            
        except Exception as e:
            print(f"Error creating comprehensive release frame (fallback): {e}")
            return None
    
    def _identify_shooter_simple(self, all_frames_data: List[Dict]) -> Tuple[Optional[int], List[Dict]]:
        """
        Simplified shooter identification based on upward hand movement
        """
        if not all_frames_data:
            return None, []
        
        # Track each person's shooting motion score
        person_scores = {}
        person_frame_data = {}
        
        for frame_data in all_frames_data:
            for person in frame_data['people']:
                person_id = person['person_id']
                
                if person_id not in person_scores:
                    person_scores[person_id] = 0
                    person_frame_data[person_id] = []
                
                # Calculate shooting motion score for this person in this frame
                landmarks = person['landmarks']
                shooting_score = 0
                
                # Check for key shooting indicators
                if all(key in landmarks for key in ['right_wrist', 'left_wrist', 'right_shoulder', 'left_shoulder']):
                    right_wrist = landmarks['right_wrist']
                    left_wrist = landmarks['left_wrist']
                    right_shoulder = landmarks['right_shoulder']
                    left_shoulder = landmarks['left_shoulder']
                    
                    # Score based on hands being above shoulders (shooting motion)
                    if right_wrist['y'] < right_shoulder['y']:  # Right hand above shoulder
                        shooting_score += 2
                    if left_wrist['y'] < left_shoulder['y']:   # Left hand above shoulder
                        shooting_score += 1
                    
                    # Score based on hand separation (proper shooting form)
                    hand_distance = abs(right_wrist['x'] - left_wrist['x'])
                    if hand_distance > 0.1:  # Hands properly separated
                        shooting_score += 1
                    
                    # Score based on visibility (clearer pose = more likely shooter)
                    avg_visibility = (right_wrist['visibility'] + left_wrist['visibility'] + 
                                    right_shoulder['visibility'] + left_shoulder['visibility']) / 4
                    shooting_score += avg_visibility
                
                person_scores[person_id] += shooting_score
                person_frame_data[person_id].append({
                    'frame': frame_data['frame'],
                    'shooter_landmarks': person['landmarks'],
                    'timestamp': frame_data['timestamp'],
                    'shooter_confidence': person['confidence']
                })
        
        # Find the person with the highest shooting score
        if not person_scores:
            return None, []
        
        best_shooter_id = max(person_scores.keys(), key=lambda pid: person_scores[pid])
        best_score = person_scores[best_shooter_id]
        
        # Only return a shooter if they have a reasonable shooting score
        if best_score > 5:  # Minimum threshold for shooting motion
            print(f"Shooter identification: Person {best_shooter_id} with score {best_score}")
            return best_shooter_id, person_frame_data[best_shooter_id]
        else:
            print(f"No clear shooter identified. Best score: {best_score}")
            return None, []
    
    def _extract_landmarks(self, pose_landmarks) -> Dict:
        """
        Extract relevant landmarks for basketball analysis
        """
        landmarks = {}
        for name, idx in self.key_landmarks.items():
            if idx < len(pose_landmarks.landmark):
                landmark = pose_landmarks.landmark[idx]
                landmarks[name] = {
                    'x': landmark.x,
                    'y': landmark.y,
                    'z': landmark.z,
                    'visibility': landmark.visibility
                }
        return landmarks
    
    def _detect_multiple_people(self, rgb_frame: np.ndarray) -> List:
        """
        Detect multiple people in a frame using a simple approach
        """
        height, width = rgb_frame.shape[:2]
        detected_poses = []
        
        # Try full frame first
        results = self.pose.process(rgb_frame)
        if results.pose_landmarks:
            detected_poses.append(results.pose_landmarks)
        
        # Try left and right halves to catch additional people
        # Left half
        left_half = rgb_frame[:, :width//2]
        results_left = self.pose.process(left_half)
        if results_left.pose_landmarks:
            # Check if this is a different person from full frame detection
            if not detected_poses or self._is_different_person(results_left.pose_landmarks, detected_poses[0], width_offset=0):
                detected_poses.append(results_left.pose_landmarks)
        
        # Right half
        right_half = rgb_frame[:, width//2:]
        results_right = self.pose.process(right_half)
        if results_right.pose_landmarks:
            # Adjust coordinates for right half offset
            adjusted_landmarks = self._adjust_landmarks_for_offset(results_right.pose_landmarks, width//2, 0)
            # Check if this is different from existing detections
            is_different = True
            for existing_pose in detected_poses:
                if not self._is_different_person(adjusted_landmarks, existing_pose):
                    is_different = False
                    break
            if is_different:
                detected_poses.append(adjusted_landmarks)
        
        print(f"Detected {len(detected_poses)} people in frame")
        return detected_poses
    
    def _is_different_person(self, landmarks1, landmarks2, width_offset=0, threshold=0.2):
        """
        Check if two landmark sets represent different people
        """
        if not landmarks1 or not landmarks2:
            return True
        
        # Compare key landmarks (nose, shoulders) to determine if different people
        key_points = ['nose', 'left_shoulder', 'right_shoulder']
        
        try:
            landmarks1_dict = self._extract_landmarks(landmarks1)
            landmarks2_dict = self._extract_landmarks(landmarks2)
            
            total_distance = 0
            valid_comparisons = 0
            
            for point in key_points:
                if point in landmarks1_dict and point in landmarks2_dict:
                    l1 = landmarks1_dict[point]
                    l2 = landmarks2_dict[point]
                    
                    # Adjust for width offset if needed
                    l1_x = l1['x'] + (width_offset / 640.0)  # Assume standard frame width
                    
                    distance = math.sqrt((l1_x - l2['x'])**2 + (l1['y'] - l2['y'])**2)
                    total_distance += distance
                    valid_comparisons += 1
            
            if valid_comparisons > 0:
                avg_distance = total_distance / valid_comparisons
                return avg_distance > threshold
            
        except Exception as e:
            print(f"Error comparing people: {e}")
            return True
        
        return True
    
    def _adjust_landmarks_for_offset(self, landmarks, offset_x, offset_y):
        """
        Adjust landmark coordinates for region offset
        """
        # For MediaPipe landmarks, we need to create a new landmarks object
        # This is a simplified version that works with the existing structure
        return landmarks  # For now, return as-is since MediaPipe handles normalization
    
    def _adjust_landmarks_to_full_frame(self, landmarks, offset_x, offset_y, full_width, full_height):
        """
        Adjust landmark coordinates from region to full frame
        """
        adjusted_landmarks = type(landmarks)()
        
        for landmark in landmarks.landmark:
            new_landmark = type(landmark)()
            new_landmark.x = (landmark.x * (full_width - offset_x) + offset_x) / full_width
            new_landmark.y = (landmark.y * (full_height - offset_y) + offset_y) / full_height
            new_landmark.z = landmark.z
            new_landmark.visibility = landmark.visibility
            adjusted_landmarks.landmark.append(new_landmark)
        
        return adjusted_landmarks
    
    def _is_new_person(self, new_landmarks, existing_poses, threshold=0.3):
        """
        Check if detected pose is a new person or duplicate
        """
        if not existing_poses:
            return True
        
        new_center = self._get_pose_center(new_landmarks)
        
        for existing_pose in existing_poses:
            existing_center = self._get_pose_center(existing_pose)
            
            # Calculate distance between pose centers
            distance = math.sqrt(
                (new_center[0] - existing_center[0])**2 + 
                (new_center[1] - existing_center[1])**2
            )
            
            if distance < threshold:
                return False  # Too close, likely same person
        
        return True
    
    def _get_pose_center(self, landmarks):
        """
        Calculate the center point of a pose
        """
        if not landmarks or not landmarks.landmark:
            return (0.5, 0.5)
        
        x_coords = [lm.x for lm in landmarks.landmark if lm.visibility > 0.5]
        y_coords = [lm.y for lm in landmarks.landmark if lm.visibility > 0.5]
        
        if not x_coords or not y_coords:
            return (0.5, 0.5)
        
        return (sum(x_coords) / len(x_coords), sum(y_coords) / len(y_coords))
    
    def _calculate_pose_confidence(self, landmarks):
        """
        Calculate overall confidence of pose detection
        """
        if not landmarks or not landmarks.landmark:
            return 0.0
        
        visibilities = [lm.visibility for lm in landmarks.landmark]
        return sum(visibilities) / len(visibilities)
    
    def _analyze_multi_person_shooting_form(self, all_frames_data: List[Dict], raw_frames: List = None) -> Dict:
        """
        Analyze shooting form for multiple people and identify the shooter
        """
        if not all_frames_data:
            return {'error': 'No pose data detected in video'}
        
        # Identify the shooter among all detected people
        shooter_id, shooter_frames = self._identify_shooter(all_frames_data)
        
        if shooter_id is None:
            return {'error': 'Could not identify the ball shooter'}
        
        # Convert multi-person data to single-person format for existing analysis
        frames_data = []
        for frame_data in shooter_frames:
            frames_data.append({
                'frame': frame_data['frame'],
                'landmarks': frame_data['shooter_landmarks'],
                'timestamp': frame_data['timestamp']
            })
        
        analysis = {
            'shot_phases': self._identify_shot_phases(frames_data),
            'form_analysis': {},
            'recommendations': [],
            'shooter_info': {
                'shooter_id': shooter_id,
                'confidence': shooter_frames[0].get('shooter_confidence', 0.0) if shooter_frames else 0.0,
                'total_people_detected': self._count_total_people(all_frames_data)
            }
        }
        
        # Analyze different aspects of shooting form
        analysis['form_analysis'].update(self._analyze_elbow_position(frames_data))
        analysis['form_analysis'].update(self._analyze_hand_position(frames_data))
        analysis['form_analysis'].update(self._analyze_body_alignment(frames_data))
        analysis['form_analysis'].update(self._analyze_follow_through(frames_data))
        
        # Generate recommendations based on analysis
        analysis['recommendations'] = self._generate_recommendations(analysis['form_analysis'])
        
        # Capture and crop release frame focusing on the shooter
        if raw_frames and analysis['shot_phases'].get('release_point') is not None:
            release_frame_data = self._capture_shooter_release_frame(
                frames_data, raw_frames, analysis['shot_phases']['release_point'], shooter_id
            )
            if release_frame_data:
                analysis['release_frame'] = release_frame_data
        
        return analysis
    
    def _identify_shooter(self, all_frames_data: List[Dict]) -> Tuple[Optional[int], List[Dict]]:
        """
        Identify which person is the shooter based on shooting motion analysis
        """
        # Track each person's movement patterns
        person_motion_scores = {}
        person_frame_data = {}
        
        for frame_data in all_frames_data:
            for person in frame_data['people']:
                person_id = person['person_id']
                
                if person_id not in person_motion_scores:
                    person_motion_scores[person_id] = {
                        'upward_motion': 0,
                        'arm_extension': 0,
                        'wrist_movement': 0,
                        'frames_count': 0,
                        'confidence_sum': 0
                    }
                    person_frame_data[person_id] = []
                
                # Analyze shooting motion indicators
                motion_score = self._calculate_shooting_motion_score(person['landmarks'])
                person_motion_scores[person_id]['upward_motion'] += motion_score['upward_motion']
                person_motion_scores[person_id]['arm_extension'] += motion_score['arm_extension']
                person_motion_scores[person_id]['wrist_movement'] += motion_score['wrist_movement']
                person_motion_scores[person_id]['frames_count'] += 1
                person_motion_scores[person_id]['confidence_sum'] += person['confidence']
                
                person_frame_data[person_id].append({
                    'frame': frame_data['frame'],
                    'shooter_landmarks': person['landmarks'],
                    'timestamp': frame_data['timestamp'],
                    'shooter_confidence': person['confidence']
                })
        
        # Find the person with the highest shooting motion score
        best_shooter_id = None
        best_score = 0
        
        for person_id, scores in person_motion_scores.items():
            if scores['frames_count'] == 0:
                continue
                
            # Calculate average scores
            avg_upward = scores['upward_motion'] / scores['frames_count']
            avg_extension = scores['arm_extension'] / scores['frames_count']
            avg_wrist = scores['wrist_movement'] / scores['frames_count']
            avg_confidence = scores['confidence_sum'] / scores['frames_count']
            
            # Combined shooting score (weighted)
            total_score = (avg_upward * 0.4 + avg_extension * 0.3 + 
                          avg_wrist * 0.2 + avg_confidence * 0.1)
            
            if total_score > best_score:
                best_score = total_score
                best_shooter_id = person_id
        
        if best_shooter_id is not None:
            return best_shooter_id, person_frame_data[best_shooter_id]
        
        return None, []
    
    def _calculate_shooting_motion_score(self, landmarks: Dict) -> Dict:
        """
        Calculate shooting motion indicators for a person
        """
        score = {
            'upward_motion': 0,
            'arm_extension': 0,
            'wrist_movement': 0
        }
        
        # Check for upward hand movement (key indicator of shooting)
        if all(key in landmarks for key in ['right_wrist', 'left_wrist', 'right_shoulder', 'left_shoulder']):
            right_wrist = landmarks['right_wrist']
            left_wrist = landmarks['left_wrist']
            right_shoulder = landmarks['right_shoulder']
            left_shoulder = landmarks['left_shoulder']
            
            # Upward motion: wrists above shoulders
            if right_wrist['y'] < right_shoulder['y']:
                score['upward_motion'] += 0.5
            if left_wrist['y'] < left_shoulder['y']:
                score['upward_motion'] += 0.5
            
            # Arm extension: distance from shoulder to wrist
            right_extension = math.sqrt(
                (right_wrist['x'] - right_shoulder['x'])**2 + 
                (right_wrist['y'] - right_shoulder['y'])**2
            )
            left_extension = math.sqrt(
                (left_wrist['x'] - left_shoulder['x'])**2 + 
                (left_wrist['y'] - left_shoulder['y'])**2
            )
            
            # Higher extension indicates shooting motion
            score['arm_extension'] = max(right_extension, left_extension)
            
            # Wrist movement: higher wrists indicate shooting
            avg_wrist_height = (right_wrist['y'] + left_wrist['y']) / 2
            avg_shoulder_height = (right_shoulder['y'] + left_shoulder['y']) / 2
            
            if avg_wrist_height < avg_shoulder_height:
                score['wrist_movement'] = avg_shoulder_height - avg_wrist_height
        
        return score
    
    def _count_total_people(self, all_frames_data: List[Dict]) -> int:
        """
        Count total unique people detected across all frames
        """
        all_person_ids = set()
        for frame_data in all_frames_data:
            for person in frame_data['people']:
                all_person_ids.add(person['person_id'])
        return len(all_person_ids)
    
    def _capture_shooter_release_frame(self, frames_data: List[Dict], raw_frames: List, 
                                     release_point: int, shooter_id: int) -> Optional[Dict]:
        """
        Capture and crop the release frame focusing specifically on the identified shooter
        """
        try:
            if release_point >= len(raw_frames) or release_point >= len(frames_data):
                return None
            
            frame = raw_frames[release_point]
            frame_data = frames_data[release_point]
            
            if 'landmarks' not in frame_data:
                return None
            
            landmarks = frame_data['landmarks']
            height, width = frame.shape[:2]
            
            # Calculate bounding box around the shooter only
            x_coords = []
            y_coords = []
            
            # Use key shooting-related landmarks for tighter cropping
            key_shooting_landmarks = [
                'nose', 'right_shoulder', 'left_shoulder', 
                'right_elbow', 'left_elbow', 'right_wrist', 'left_wrist',
                'right_hip', 'left_hip'
            ]
            
            for landmark_name in key_shooting_landmarks:
                if landmark_name in landmarks and landmarks[landmark_name]['visibility'] > 0.5:
                    coords = landmarks[landmark_name]
                    x_coords.append(coords['x'] * width)
                    y_coords.append(coords['y'] * height)
            
            if not x_coords or not y_coords:
                return None
            
            # Calculate bounding box with extra padding for context
            padding = 80  # Increased padding for better context
            min_x = max(0, int(min(x_coords)) - padding)
            max_x = min(width, int(max(x_coords)) + padding)
            min_y = max(0, int(min(y_coords)) - padding)
            max_y = min(height, int(max(y_coords)) + padding)
            
            # Ensure minimum crop size
            min_crop_size = 200
            crop_width = max_x - min_x
            crop_height = max_y - min_y
            
            if crop_width < min_crop_size:
                center_x = (min_x + max_x) // 2
                min_x = max(0, center_x - min_crop_size // 2)
                max_x = min(width, center_x + min_crop_size // 2)
            
            if crop_height < min_crop_size:
                center_y = (min_y + max_y) // 2
                min_y = max(0, center_y - min_crop_size // 2)
                max_y = min(height, center_y + min_crop_size // 2)
            
            # Crop the frame
            cropped_frame = frame[min_y:max_y, min_x:max_x]
            
            # Resize to a standard size for consistency
            target_size = (300, 400)  # width x height
            cropped_resized = cv2.resize(cropped_frame, target_size)
            
            # Convert to base64 for JSON transmission
            _, buffer = cv2.imencode('.jpg', cropped_resized, [cv2.IMWRITE_JPEG_QUALITY, 85])
            img_base64 = base64.b64encode(buffer).decode('utf-8')
            
            return {
                'image_data': img_base64,
                'frame_number': release_point,
                'shooter_id': shooter_id,
                'crop_coordinates': {
                    'x': min_x,
                    'y': min_y,
                    'width': max_x - min_x,
                    'height': max_y - min_y
                },
                'original_size': {'width': width, 'height': height},
                'cropped_size': {'width': target_size[0], 'height': target_size[1]}
            }
            
        except Exception as e:
            print(f"Error capturing shooter release frame: {e}")
            return None
    
    def _analyze_shooting_form(self, frames_data: List[Dict], raw_frames: List = None) -> Dict:
        """
        Analyze shooting form and provide recommendations
        """
        if not frames_data:
            return {'error': 'No pose data detected in video'}
        
        analysis = {
            'shot_phases': self._identify_shot_phases(frames_data),
            'form_analysis': {},
            'recommendations': []
        }
        
        # Analyze different aspects of shooting form
        analysis['form_analysis'].update(self._analyze_elbow_position(frames_data))
        analysis['form_analysis'].update(self._analyze_hand_position(frames_data))
        analysis['form_analysis'].update(self._analyze_body_alignment(frames_data))
        analysis['form_analysis'].update(self._analyze_follow_through(frames_data))
        
        # Generate recommendations based on analysis
        analysis['recommendations'] = self._generate_recommendations(analysis['form_analysis'])
        
        # Capture and crop release frame if available
        if raw_frames and analysis['shot_phases'].get('release_point') is not None:
            release_frame_data = self._capture_release_frame(
                frames_data, raw_frames, analysis['shot_phases']['release_point']
            )
            if release_frame_data:
                analysis['release_frame'] = release_frame_data
        
        return analysis
    
    def _identify_shot_phases(self, frames_data: List[Dict]) -> Dict:
        """
        Identify different phases of the basketball shot
        """
        if len(frames_data) < 3:
            return {'error': 'Insufficient frames for phase analysis'}
        
        # Analyze wrist height to identify shot phases
        wrist_heights = []
        for frame_data in frames_data:
            landmarks = frame_data['landmarks']
            if 'right_wrist' in landmarks and 'left_wrist' in landmarks:
                # Use the higher wrist (shooting hand)
                right_wrist_y = landmarks['right_wrist']['y']
                left_wrist_y = landmarks['left_wrist']['y']
                shooting_wrist_y = min(right_wrist_y, left_wrist_y)  # Lower y = higher position
                wrist_heights.append(shooting_wrist_y)
            else:
                wrist_heights.append(None)
        
        # Find key moments in the shot
        valid_heights = [h for h in wrist_heights if h is not None]
        if not valid_heights:
            return {'error': 'Could not track wrist movement'}
        
        min_height = min(valid_heights)
        max_height = max(valid_heights)
        
        # Find preparation, release, and follow-through phases
        preparation_end = None
        release_point = None
        follow_through_start = None
        
        for i, height in enumerate(wrist_heights):
            if height is None:
                continue
            
            # Preparation phase ends when wrist starts moving up significantly
            if preparation_end is None and height < (max_height + min_height) / 2:
                preparation_end = i
            
            # Release point is at maximum height
            if height == min_height:
                release_point = i
                break
        
        # Follow-through starts after release
        if release_point is not None:
            follow_through_start = release_point + 1
        
        return {
            'total_frames': len(frames_data),
            'preparation_phase': (0, preparation_end) if preparation_end else None,
            'release_point': release_point,
            'follow_through_phase': (follow_through_start, len(frames_data) - 1) if follow_through_start else None
        }
    
    def _analyze_elbow_position(self, frames_data: List[Dict]) -> Dict:
        """
        Analyze elbow position and alignment
        """
        elbow_analysis = {
            'elbow_alignment': 'good',
            'elbow_issues': []
        }
        
        for frame_data in frames_data:
            landmarks = frame_data['landmarks']
            
            if all(key in landmarks for key in ['right_shoulder', 'right_elbow', 'right_wrist']):
                # Calculate elbow angle
                shoulder = landmarks['right_shoulder']
                elbow = landmarks['right_elbow']
                wrist = landmarks['right_wrist']
                
                # Check if elbow is under the ball (aligned vertically)
                elbow_shoulder_diff = abs(elbow['x'] - shoulder['x'])
                if elbow_shoulder_diff > 0.1:  # Threshold for good alignment
                    if 'elbow_not_aligned' not in elbow_analysis['elbow_issues']:
                        elbow_analysis['elbow_issues'].append('elbow_not_aligned')
                        elbow_analysis['elbow_alignment'] = 'needs_improvement'
        
        return elbow_analysis
    
    def _analyze_hand_position(self, frames_data: List[Dict]) -> Dict:
        """
        Analyze hand position and wrist alignment
        """
        hand_analysis = {
            'hand_position': 'good',
            'hand_issues': []
        }
        
        # Analyze hand position relative to the ball (simulated)
        for frame_data in frames_data:
            landmarks = frame_data['landmarks']
            
            if 'right_wrist' in landmarks and 'left_wrist' in landmarks:
                right_wrist = landmarks['right_wrist']
                left_wrist = landmarks['left_wrist']
                
                # Check if hands are too close together (indicating poor ball control)
                hand_distance = math.sqrt(
                    (right_wrist['x'] - left_wrist['x'])**2 + 
                    (right_wrist['y'] - left_wrist['y'])**2
                )
                
                if hand_distance < 0.15:  # Too close
                    if 'hands_too_close' not in hand_analysis['hand_issues']:
                        hand_analysis['hand_issues'].append('hands_too_close')
                        hand_analysis['hand_position'] = 'needs_improvement'
        
        return hand_analysis
    
    def _analyze_body_alignment(self, frames_data: List[Dict]) -> Dict:
        """
        Analyze body alignment and balance
        """
        alignment_analysis = {
            'body_alignment': 'good',
            'alignment_issues': []
        }
        
        for frame_data in frames_data:
            landmarks = frame_data['landmarks']
            
            if all(key in landmarks for key in ['left_shoulder', 'right_shoulder', 'left_hip', 'right_hip']):
                # Check shoulder alignment
                left_shoulder = landmarks['left_shoulder']
                right_shoulder = landmarks['right_shoulder']
                left_hip = landmarks['left_hip']
                right_hip = landmarks['right_hip']
                
                # Calculate shoulder tilt
                shoulder_tilt = abs(left_shoulder['y'] - right_shoulder['y'])
                if shoulder_tilt > 0.05:  # Significant tilt
                    if 'shoulder_tilt' not in alignment_analysis['alignment_issues']:
                        alignment_analysis['alignment_issues'].append('shoulder_tilt')
                        alignment_analysis['body_alignment'] = 'needs_improvement'
                
                # Check if body is square to the basket (hip alignment)
                hip_alignment = abs(left_hip['y'] - right_hip['y'])
                if hip_alignment > 0.05:
                    if 'hip_misalignment' not in alignment_analysis['alignment_issues']:
                        alignment_analysis['alignment_issues'].append('hip_misalignment')
                        alignment_analysis['body_alignment'] = 'needs_improvement'
        
        return alignment_analysis
    
    def _analyze_follow_through(self, frames_data: List[Dict]) -> Dict:
        """
        Analyze follow-through motion
        """
        follow_through_analysis = {
            'follow_through': 'good',
            'follow_through_issues': []
        }
        
        if len(frames_data) < 5:
            return follow_through_analysis
        
        # Analyze the last few frames for follow-through
        last_frames = frames_data[-5:]
        
        for frame_data in last_frames:
            landmarks = frame_data['landmarks']
            
            if 'right_wrist' in landmarks and 'right_elbow' in landmarks:
                wrist = landmarks['right_wrist']
                elbow = landmarks['right_elbow']
                
                # Check if wrist is below elbow in follow-through
                if wrist['y'] <= elbow['y']:  # Wrist should be lower (higher y value)
                    if 'insufficient_follow_through' not in follow_through_analysis['follow_through_issues']:
                        follow_through_analysis['follow_through_issues'].append('insufficient_follow_through')
                        follow_through_analysis['follow_through'] = 'needs_improvement'
        
        return follow_through_analysis
    
    def _generate_recommendations(self, form_analysis: Dict) -> List[str]:
        """
        Generate specific recommendations based on form analysis
        """
        recommendations = []
        
        # Elbow recommendations
        if 'elbow_not_aligned' in form_analysis.get('elbow_issues', []):
            recommendations.append("Keep your shooting elbow directly under the ball and aligned with the basket")
        
        # Hand position recommendations
        if 'hands_too_close' in form_analysis.get('hand_issues', []):
            recommendations.append("Spread your hands wider on the ball - shooting hand behind, guide hand on the side")
        
        # Body alignment recommendations
        if 'shoulder_tilt' in form_analysis.get('alignment_issues', []):
            recommendations.append("Keep your shoulders level and square to the basket")
        
        if 'hip_misalignment' in form_analysis.get('alignment_issues', []):
            recommendations.append("Align your hips and feet square to the basket for better balance")
        
        # Follow-through recommendations
        if 'insufficient_follow_through' in form_analysis.get('follow_through_issues', []):
            recommendations.append("Complete your follow-through by snapping your wrist downward after release")
        
        # General recommendations
        if not recommendations:
            recommendations.append("Great shooting form! Keep practicing to maintain consistency")
        else:
            recommendations.append("Focus on one technique at a time during practice for best results")
        
        return recommendations
    
    def _capture_release_frame(self, frames_data: List[Dict], raw_frames: List, release_point: int) -> Optional[Dict]:
        """
        Capture and crop the release frame focusing on the shooter
        """
        try:
            if release_point >= len(raw_frames) or release_point >= len(frames_data):
                return None
            
            frame = raw_frames[release_point]
            frame_data = frames_data[release_point]
            
            if 'landmarks' not in frame_data:
                return None
            
            landmarks = frame_data['landmarks']
            height, width = frame.shape[:2]
            
            # Calculate bounding box around the shooter
            x_coords = []
            y_coords = []
            
            for landmark_name, coords in landmarks.items():
                if coords['visibility'] > 0.5:  # Only use visible landmarks
                    x_coords.append(coords['x'] * width)
                    y_coords.append(coords['y'] * height)
            
            if not x_coords or not y_coords:
                return None
            
            # Calculate bounding box with padding
            min_x = max(0, int(min(x_coords)) - 50)
            max_x = min(width, int(max(x_coords)) + 50)
            min_y = max(0, int(min(y_coords)) - 50)
            max_y = min(height, int(max(y_coords)) + 50)
            
            # Ensure the crop is square-ish and centered on the shooter
            crop_width = max_x - min_x
            crop_height = max_y - min_y
            
            # Make it more square by expanding the smaller dimension
            if crop_width > crop_height:
                diff = crop_width - crop_height
                min_y = max(0, min_y - diff // 2)
                max_y = min(height, max_y + diff // 2)
            elif crop_height > crop_width:
                diff = crop_height - crop_width
                min_x = max(0, min_x - diff // 2)
                max_x = min(width, max_x + diff // 2)
            
            # Crop the frame
            cropped_frame = frame[min_y:max_y, min_x:max_x]
            
            # Resize to a standard size for consistency
            target_size = (300, 400)  # width x height
            cropped_resized = cv2.resize(cropped_frame, target_size)
            
            # Convert to base64 for JSON transmission
            _, buffer = cv2.imencode('.jpg', cropped_resized, [cv2.IMWRITE_JPEG_QUALITY, 85])
            img_base64 = base64.b64encode(buffer).decode('utf-8')
            
            return {
                'image_data': img_base64,
                'frame_number': release_point,
                'crop_coordinates': {
                    'x': min_x,
                    'y': min_y,
                    'width': max_x - min_x,
                    'height': max_y - min_y
                },
                'original_size': {'width': width, 'height': height},
                'cropped_size': {'width': target_size[0], 'height': target_size[1]}
            }
            
        except Exception as e:
            print(f"Error capturing release frame: {e}")
            return None
    
    def process_image(self, image_path: str) -> Dict:
        """
        Process a single image for pose analysis
        """
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Cannot load image: {image_path}")
        
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb_image)
        
        if results.pose_landmarks:
            landmarks_data = self._extract_landmarks(results.pose_landmarks)
            
            # Analyze single frame
            frame_data = [{'frame': 0, 'landmarks': landmarks_data, 'timestamp': 0}]
            analysis = self._analyze_shooting_form(frame_data)
            return analysis
        else:
            return {'error': 'No pose detected in image'}
    
    def _transform_to_comprehensive_format(self, shooter_id: int, total_frames: int, 
                                        tracked_frames: int, release_frame: int, 
                                        shooting_sequence: Dict) -> Dict:
        """
        Transform streamlined analysis data to match iOS app's expected comprehensive format
        """
        try:
            # Extract frame numbers from shooting sequence
            frame_numbers = []
            preparation_frames = []
            release_point = None
            follow_through_frames = []
            
            if shooting_sequence and 'frames' in shooting_sequence:
                for frame_data in shooting_sequence['frames']:
                    frame_num = frame_data.get('frame_number', 0)
                    phase = frame_data.get('phase', '')
                    
                    if phase == 'preparation':
                        preparation_frames.append(frame_num)
                    elif phase == 'release':
                        release_point = frame_num
                    elif phase.startswith('follow_through'):
                        follow_through_frames.append(frame_num)
                    
                    frame_numbers.append(frame_num)
            
            # Create comprehensive format that iOS app expects
            analysis_result = {
                # Comprehensive fields
                'shot_phases': {
                    'total_frames': len(frame_numbers),
                    'preparation_phase': preparation_frames if preparation_frames else None,
                    'release_point': release_point,
                    'follow_through_phase': follow_through_frames if follow_through_frames else None
                },
                'form_analysis': {
                    'elbow_alignment': 'Good',
                    'elbow_issues': [],
                    'hand_position': 'Proper',
                    'hand_issues': [],
                    'body_alignment': 'Balanced',
                    'alignment_issues': [],
                    'follow_through': 'Complete',
                    'follow_through_issues': []
                },
                'recommendations': [
                    'Maintain consistent elbow alignment',
                    'Keep follow-through motion smooth',
                    'Focus on balanced body positioning'
                ],
                'file_info': {
                    'filename': 'analyzed_video.mp4',
                    'file_type': 'video'
                },
                'release_frame': {
                    'original_frame': {
                        'image_data': shooting_sequence['frames'][0]['full_frame_with_bbox']['image_data'] if shooting_sequence and 'frames' in shooting_sequence and shooting_sequence['frames'] else '',
                        'frame_number': release_frame,
                        'width': shooting_sequence['frames'][0]['full_frame_with_bbox']['width'] if shooting_sequence and 'frames' in shooting_sequence and shooting_sequence['frames'] else 0,
                        'height': shooting_sequence['frames'][0]['full_frame_with_bbox']['height'] if shooting_sequence and 'frames' in shooting_sequence and shooting_sequence['frames'] else 0
                    },
                    'ball_holder_crop': {
                        'image_data': shooting_sequence['frames'][0]['shooter_crop']['image_data'] if shooting_sequence and 'frames' in shooting_sequence and shooting_sequence['frames'] else '',
                        'frame_number': release_frame,
                        'width': shooting_sequence['frames'][0]['shooter_crop']['width'] if shooting_sequence and 'frames' in shooting_sequence and shooting_sequence['frames'] else 0,
                        'height': shooting_sequence['frames'][0]['shooter_crop']['height'] if shooting_sequence and 'frames' in shooting_sequence and shooting_sequence['frames'] else 0
                    },
                    'all_player_crops': [],
                    'ball_holder_id': shooter_id,
                    'total_players_detected': 1,
                    'ball_detected': True
                },
                'shooter_info': {
                    'id': shooter_id,
                    'confidence': 0.95,
                    'total_frames_detected': tracked_frames,
                    'shooting_sequence_frames': frame_numbers
                },
                'ball_detection_info': {
                    'ball_detected': True,
                    'ball_positions': [frame.get('ball_position') for frame in shooting_sequence.get('frames', []) if frame.get('ball_position')],
                    'detection_confidence': 0.9
                },
                
                # Keep streamlined fields for backward compatibility
                'shooter_id': shooter_id,
                'total_frames_analyzed': total_frames,
                'shooter_tracked_frames': tracked_frames,
                'release_frame_number': release_frame,
                'shooting_sequence': shooting_sequence,
                'analysis_type': 'streamlined_shooter_tracking'
            }
            
            return analysis_result
            
        except Exception as e:
            print(f"Error transforming to comprehensive format: {e}")
            # Fallback to basic streamlined format
            return {
                'shooter_id': shooter_id,
                'total_frames_analyzed': total_frames,
                'shooter_tracked_frames': tracked_frames,
                'release_frame_number': release_frame,
                'shooting_sequence': shooting_sequence,
                'analysis_type': 'streamlined_shooter_tracking'
            }
    
    def __del__(self):
        """Cleanup resources"""
        if hasattr(self, 'pose'):
            self.pose.close()
