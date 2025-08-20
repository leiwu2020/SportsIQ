import requests
import json
import time

def test_video_analysis():
    """Test the video analysis function with the specified video file"""
    
    # Backend URL
    base_url = "http://localhost:5002"
    
    # Test video file
    video_file = "1755639755870.MP4"
    
    print(f"Testing video analysis with: {video_file}")
    print(f"Backend URL: {base_url}")
    
    # Check if video file exists
    import os
    if not os.path.exists(video_file):
        print(f"Error: Video file {video_file} not found!")
        return
    
    print(f"Video file found: {os.path.getsize(video_file)} bytes")
    
    # Test health endpoint first
    try:
        health_response = requests.get(f"{base_url}/health", timeout=10)
        print(f"Health check status: {health_response.status_code}")
        if health_response.status_code == 200:
            print("Backend is healthy!")
        else:
            print("Backend health check failed!")
            return
    except Exception as e:
        print(f"Health check failed: {e}")
        return
    
    # Test demo analysis first
    print("\nTesting demo analysis...")
    try:
        demo_response = requests.get(f"{base_url}/analyze/demo", timeout=30)
        print(f"Demo analysis status: {demo_response.status_code}")
        if demo_response.status_code == 200:
            demo_data = demo_response.json()
            print(f"Demo analysis successful! Response keys: {list(demo_data.keys())}")
            print(f"Analysis type: {demo_data.get('analysis_type', 'N/A')}")
            print(f"Shooting sequence frames: {len(demo_data.get('shooting_sequence', []))}")
        else:
            print(f"Demo analysis failed: {demo_response.text}")
    except Exception as e:
        print(f"Demo analysis error: {e}")
    
    # Now test actual video analysis
    print(f"\nTesting video analysis with {video_file}...")
    
    try:
        with open(video_file, 'rb') as f:
            files = {'file': (video_file, f, 'video/mp4')}
            
            print("Uploading video for analysis...")
            start_time = time.time()
            
            response = requests.post(
                f"{base_url}/analyze",
                files=files,
                timeout=120  # 2 minutes timeout for analysis
            )
            
            end_time = time.time()
            analysis_time = end_time - start_time
            
            print(f"Analysis completed in {analysis_time:.2f} seconds")
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    analysis_data = response.json()
                    print("✅ Video analysis successful!")
                    print(f"Response keys: {list(analysis_data.keys())}")
                    
                    # Check for key fields
                    if 'analysis_type' in analysis_data:
                        print(f"Analysis type: {analysis_data['analysis_type']}")
                    
                    if 'shooting_sequence' in analysis_data:
                        sequence = analysis_data['shooting_sequence']
                        if sequence:
                            print(f"Shooting sequence frames: {len(sequence)}")
                            if sequence:
                                first_frame = sequence[0]
                                print(f"First frame keys: {list(first_frame.keys())}")
                        else:
                            print("Shooting sequence is empty/null")
                    
                    if 'error' in analysis_data:
                        print(f"⚠️ Analysis returned error: {analysis_data['error']}")
                    
                    # Save response to file for inspection
                    with open('analysis_response.json', 'w') as f:
                        json.dump(analysis_data, f, indent=2)
                    print("Full response saved to analysis_response.json")
                    
                except json.JSONDecodeError as e:
                    print(f"❌ Failed to decode JSON response: {e}")
                    print(f"Raw response: {response.text[:500]}...")
                    
            else:
                print(f"❌ Analysis failed with status {response.status_code}")
                print(f"Error response: {response.text}")
                
    except Exception as e:
        print(f"❌ Video analysis error: {e}")

if __name__ == "__main__":
    test_video_analysis()
