from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import tempfile
import uuid
from werkzeug.utils import secure_filename
from pose_analyzer import BasketballPoseAnalyzer
import traceback
import base64
import cv2
import numpy as np

app = Flask(__name__)
CORS(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'jpg', 'jpeg', 'png'}

# Initialize the pose analyzer
pose_analyzer = BasketballPoseAnalyzer()

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_video_file(filename):
    """Check if the file is a video"""
    video_extensions = {'mp4', 'avi', 'mov', 'mkv'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in video_extensions

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'SportsIQ API is running'})

@app.route('/analyze', methods=['POST'])
def analyze_shot():
    """
    Analyze basketball shooting form from uploaded video or image
    """
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not supported. Please upload MP4, AVI, MOV, MKV, JPG, JPEG, or PNG files'}), 400
        
        # Create temporary file
        temp_dir = tempfile.gettempdir()
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        temp_filepath = os.path.join(temp_dir, unique_filename)
        
        try:
            # Save uploaded file
            file.save(temp_filepath)
            
            # Analyze the file
            if is_video_file(filename):
                analysis_result = pose_analyzer.analyze_video(temp_filepath)
            else:
                analysis_result = pose_analyzer.process_image(temp_filepath)
            
            # Add metadata
            analysis_result['file_info'] = {
                'filename': filename,
                'file_type': 'video' if is_video_file(filename) else 'image'
            }
            
            return jsonify(analysis_result)
            
        except Exception as e:
            return jsonify({'error': f'Analysis failed: {str(e)}'}), 500
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_filepath):
                os.remove(temp_filepath)
    
    except Exception as e:
        app.logger.error(f"Error in analyze_shot: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/tips', methods=['GET'])
def get_shooting_tips():
    """
    Get general basketball shooting tips
    """
    tips = {
        'basic_form': [
            "Keep your shooting elbow directly under the ball",
            "Use your legs for power, not just your arms",
            "Follow through by snapping your wrist downward",
            "Keep your guide hand on the side of the ball",
            "Aim for a 45-50 degree arc on your shot"
        ],
        'preparation': [
            "Square your feet to the basket",
            "Keep your shooting hand behind the ball",
            "Maintain consistent hand placement",
            "Keep your head up and eyes on the target"
        ],
        'release': [
            "Release the ball at the peak of your jump",
            "Snap your wrist on release",
            "Follow through until your wrist points down",
            "Keep your elbow straight on follow-through"
        ],
        'practice_drills': [
            "Form shooting close to the basket",
            "One-handed shooting to develop proper release",
            "Wall shooting to practice arc and rotation",
            "Free throw practice for consistency"
        ]
    }
    
    return jsonify(tips)

def create_demo_release_frame():
    """
    Create a demo release frame image for testing
    """
    # Create a simple demo image with a basketball player silhouette
    img = np.ones((400, 300, 3), dtype=np.uint8) * 240  # Light gray background
    
    # Draw a simple basketball player figure
    # Head (circle)
    cv2.circle(img, (150, 80), 25, (100, 100, 100), -1)
    
    # Body (rectangle)
    cv2.rectangle(img, (130, 105), (170, 220), (100, 100, 100), -1)
    
    # Arms
    # Left arm (guide hand)
    cv2.rectangle(img, (100, 120), (130, 140), (100, 100, 100), -1)
    cv2.rectangle(img, (80, 140), (100, 160), (100, 100, 100), -1)
    
    # Right arm (shooting hand) - extended upward
    cv2.rectangle(img, (170, 120), (200, 140), (100, 100, 100), -1)
    cv2.rectangle(img, (200, 100), (220, 120), (100, 100, 100), -1)
    
    # Legs
    cv2.rectangle(img, (135, 220), (150, 280), (100, 100, 100), -1)
    cv2.rectangle(img, (155, 220), (170, 280), (100, 100, 100), -1)
    
    # Basketball (small circle above shooting hand)
    cv2.circle(img, (210, 90), 12, (255, 140, 0), -1)
    
    # Add text overlay
    cv2.putText(img, "Release Frame", (80, 350), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (50, 50, 50), 2)
    cv2.putText(img, "Demo Analysis", (85, 380), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 1)
    
    # Convert to base64
    _, buffer = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 85])
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    
    return img_base64

@app.route('/analyze/demo', methods=['GET'])
def demo_analysis():
    """
    Return a demo analysis for testing purposes
    """
    # Create a simple demo image (basketball player silhouette)
    demo_image_base64 = create_demo_release_frame()
    
    demo_result = {
        'shot_phases': {
            'total_frames': 30,
            'preparation_phase': (0, 10),
            'release_point': 15,
            'follow_through_phase': (16, 29)
        },
        'form_analysis': {
            'elbow_alignment': 'good',
            'elbow_issues': [],
            'hand_position': 'needs_improvement',
            'hand_issues': ['hands_too_close'],
            'body_alignment': 'good',
            'alignment_issues': [],
            'follow_through': 'good',
            'follow_through_issues': []
        },
        'recommendations': [
            "Spread your hands wider on the ball - shooting hand behind, guide hand on the side",
            "Focus on one technique at a time during practice for best results"
        ],
        'file_info': {
            'filename': 'demo_shot.mp4',
            'file_type': 'video'
        },
        'release_frame': {
            'original_frame': {
                'image_data': demo_image_base64,
                'width': 640,
                'height': 480
            },
            'ball_holder_crop': {
                'image_data': demo_image_base64,
                'person_id': 0,
                'is_ball_holder': True,
                'crop_coordinates': {
                    'x': 100,
                    'y': 50,
                    'width': 300,
                    'height': 400
                },
                'cropped_size': {'width': 200, 'height': 300}
            },
            'all_player_crops': [
                {
                    'image_data': demo_image_base64,
                    'person_id': 1,
                    'is_ball_holder': False,
                    'crop_coordinates': {
                        'x': 350,
                        'y': 80,
                        'width': 200,
                        'height': 300
                    },
                    'cropped_size': {'width': 200, 'height': 300}
                },
                {
                    'image_data': demo_image_base64,
                    'person_id': 2,
                    'is_ball_holder': False,
                    'crop_coordinates': {
                        'x': 50,
                        'y': 100,
                        'width': 180,
                        'height': 280
                    },
                    'cropped_size': {'width': 200, 'height': 300}
                }
            ],
            'frame_number': 15,
            'ball_holder_id': 0,
            'total_players_detected': 3,
            'ball_detected': True
        },
        'ball_detection_info': {
            'ball_detected_frames': 25,
            'total_frames': 30,
            'ball_holder_frames': 22
        }
    }
    
    return jsonify(demo_result)

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return jsonify({'error': 'File too large. Maximum size is 100MB'}), 413

@app.errorhandler(404)
def not_found(e):
    """Handle not found error"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    """Handle internal server error"""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Create uploads directory if it doesn't exist
    os.makedirs('uploads', exist_ok=True)
    
    # Run the app
    print("Starting SportsIQ Basketball Analysis API...")
    print("API will be available at: http://localhost:5001")
    print("Health check: http://localhost:5001/health")
    print("Demo analysis: http://localhost:5001/analyze/demo")
    
    app.run(debug=True, host='0.0.0.0', port=5001)
