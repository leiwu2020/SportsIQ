# SportsIQ - Basketball Shot Analysis App

SportsIQ is an iPhone app that analyzes basketball shooting form using computer vision and provides personalized correction recommendations.

## Features

- **Video Recording**: Record basketball shots directly in the app
- **Photo Library Integration**: Analyze existing videos from your photo library
- **Real-time Analysis**: Uses MediaPipe pose estimation for accurate form analysis
- **Detailed Feedback**: Get specific recommendations for:
  - Shot arc and trajectory
  - Hand position and grip
  - Elbow alignment
  - Body posture and balance
  - Follow-through technique
- **Shot Phase Detection**: Identifies preparation, release, and follow-through phases

## Architecture

### Backend (Python)
- **Flask API**: RESTful API for video/image analysis
- **MediaPipe**: Google's pose estimation for human pose detection
- **OpenCV**: Computer vision processing
- **Basketball-specific Analysis**: Custom algorithms for shooting form evaluation

### Frontend (iOS)
- **SwiftUI**: Modern iOS interface
- **Camera Integration**: Native video recording capabilities
- **Photo Library Access**: Select existing videos for analysis
- **Real-time Results**: Beautiful analysis results display

## Setup Instructions

### Backend Setup

1. **Activate the conda environment**:
   ```bash
   conda activate sportsIQ
   ```

2. **Navigate to the backend directory**:
   ```bash
   cd backend
   ```

3. **Start the Flask server**:
   ```bash
   python app.py
   ```

   The server will start on `http://localhost:5000`

### iOS App Setup

1. **Open Xcode**:
   ```bash
   open ios_app/SportsIQ.xcodeproj
   ```

2. **Configure the development team** in Xcode project settings

3. **Build and run** the app on your iOS device or simulator

## API Endpoints

### Backend API

- `GET /health` - Health check endpoint
- `POST /analyze` - Analyze uploaded video/image file
- `GET /analyze/demo` - Get demo analysis results
- `GET /tips` - Get general basketball shooting tips

### Example Usage

```bash
# Test the health endpoint
curl http://localhost:5000/health

# Get demo analysis
curl http://localhost:5000/analyze/demo

# Upload and analyze a video file
curl -X POST -F "file=@shot_video.mp4" http://localhost:5000/analyze
```

## Analysis Features

### Form Analysis Categories

1. **Elbow Alignment**
   - Checks if shooting elbow is under the ball
   - Ensures proper vertical alignment

2. **Hand Position**
   - Analyzes hand placement on the ball
   - Checks shooting vs guide hand positioning

3. **Body Alignment**
   - Evaluates shoulder and hip alignment
   - Checks overall body balance

4. **Follow Through**
   - Analyzes wrist snap and follow-through motion
   - Ensures complete shooting motion

### Shot Phase Detection

- **Preparation Phase**: Initial setup and shooting stance
- **Release Point**: Moment of ball release at peak of motion
- **Follow Through**: Post-release motion and form completion

## Technology Stack

### Backend
- Python 3.11
- Flask (Web framework)
- MediaPipe (Pose estimation)
- OpenCV (Computer vision)
- NumPy (Numerical computing)
- SciPy (Scientific computing)

### iOS App
- Swift 5.0
- SwiftUI (UI framework)
- AVFoundation (Camera/video handling)
- UIKit (iOS integration)

## Development Notes

### Backend Development
- The pose analyzer uses MediaPipe's pose estimation model
- Analysis algorithms are specifically tuned for basketball shooting form
- Supports both video and static image analysis
- Results include detailed recommendations based on detected issues

### iOS Development
- Uses modern SwiftUI for the interface
- Implements proper camera permissions and handling
- Network layer handles communication with Python backend
- Responsive UI with loading states and error handling

## Future Enhancements

- **Advanced Analytics**: Shot success prediction, arc analysis
- **Progress Tracking**: Historical analysis and improvement tracking
- **Social Features**: Share results and compete with friends
- **Offline Mode**: On-device analysis using Core ML
- **Professional Features**: Coach dashboard, team analytics

## Troubleshooting

### Common Issues

1. **Backend server not starting**:
   - Ensure conda environment is activated
   - Check all dependencies are installed
   - Verify port 5000 is available

2. **iOS app can't connect to backend**:
   - Ensure backend server is running
   - Check network connectivity
   - Update NetworkManager baseURL if needed

3. **Camera permissions**:
   - Grant camera and photo library permissions in iOS settings
   - Check Info.plist contains proper usage descriptions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is for educational and personal use. Please respect applicable licenses for MediaPipe and other dependencies.

