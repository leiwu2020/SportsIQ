#!/usr/bin/env python3
"""
Direct test of the pose analyzer without Flask server
"""
import sys
import os
sys.path.append('backend')

def test_direct_analysis():
    """Test the pose analyzer directly"""
    
    try:
        print("Testing direct pose analyzer import...")
        from pose_analyzer import BasketballPoseAnalyzer
        print("✅ Successfully imported BasketballPoseAnalyzer")
        
        # Initialize the analyzer
        print("Initializing pose analyzer...")
        analyzer = BasketballPoseAnalyzer()
        print("✅ Pose analyzer initialized successfully")
        
        # Test video file
        video_file = "1755639755870.MP4"
        
        if not os.path.exists(video_file):
            print(f"❌ Video file {video_file} not found!")
            return
        
        print(f"✅ Video file found: {os.path.getsize(video_file)} bytes")
        
        # Test the analysis
        print(f"\nStarting analysis of {video_file}...")
        print("This may take a few minutes...")
        
        try:
            result = analyzer.analyze_video(video_file)
            print("✅ Analysis completed successfully!")
            
            # Print key information
            print(f"\nAnalysis Result Summary:")
            print(f"Keys in result: {list(result.keys())}")
            
            if 'analysis_type' in result:
                print(f"Analysis type: {result['analysis_type']}")
            
            if 'shooting_sequence' in result:
                sequence = result['shooting_sequence']
                if sequence:
                    print(f"Shooting sequence frames: {len(sequence)}")
                    if sequence:
                        first_frame = sequence[0]
                        print(f"First frame keys: {list(first_frame.keys())}")
                else:
                    print("Shooting sequence is empty/null")
            
            if 'error' in result:
                print(f"⚠️ Analysis returned error: {result['error']}")
            
            # Save result to file
            import json
            with open('direct_analysis_result.json', 'w') as f:
                json.dump(result, f, indent=2)
            print("Full result saved to direct_analysis_result.json")
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            import traceback
            traceback.print_exc()
            
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print("Make sure you're in the conda environment: conda activate sportsIQ")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_direct_analysis()

