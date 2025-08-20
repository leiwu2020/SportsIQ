#!/usr/bin/env python3
"""
Test script for the SportsIQ Basketball Analysis API
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_health():
    """Test the health endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_demo_analysis():
    """Test the demo analysis endpoint"""
    print("\nTesting demo analysis endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/analyze/demo")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Demo Analysis Results:")
            print(f"- Shot Phases: {data.get('shot_phases', {})}")
            print(f"- Form Analysis: {data.get('form_analysis', {})}")
            print(f"- Recommendations: {len(data.get('recommendations', []))} tips")
            
            # Print recommendations
            for i, rec in enumerate(data.get('recommendations', []), 1):
                print(f"  {i}. {rec}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_shooting_tips():
    """Test the shooting tips endpoint"""
    print("\nTesting shooting tips endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/tips")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Shooting Tips Categories:")
            for category, tips in data.items():
                print(f"- {category.replace('_', ' ').title()}: {len(tips)} tips")
        
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Run all API tests"""
    print("SportsIQ API Test Suite")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health),
        ("Demo Analysis", test_demo_analysis),
        ("Shooting Tips", test_shooting_tips),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 30)
        success = test_func()
        results.append((test_name, success))
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\nResults: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! The API is working correctly.")
        print("\nNext steps:")
        print("1. Open Xcode: open ios_app/SportsIQ.xcodeproj")
        print("2. Build and run the iOS app")
        print("3. Test video recording and analysis features")
    else:
        print(f"\n⚠️ {len(results) - passed} test(s) failed. Check server status.")

if __name__ == "__main__":
    main()
