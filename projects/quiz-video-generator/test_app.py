#!/usr/bin/env python3
"""
Quick test script to verify the application setup
"""
import os
import sys

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    try:
        from app import create_app
        from app.database import init_db, get_db
        from app.models import Settings, Quiz, Question, Video
        from app.video_generator import VideoGenerator
        print("✓ All imports successful")
        return True
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False

def test_database():
    """Test database initialization"""
    print("\nTesting database...")
    try:
        from app.database import init_db
        if os.path.exists('quiz_generator.db'):
            print("✓ Database file exists")
        else:
            print("Creating database...")
            init_db()
            print("✓ Database created")
        return True
    except Exception as e:
        print(f"✗ Database error: {e}")
        return False

def test_dependencies():
    """Test required dependencies"""
    print("\nTesting dependencies...")
    dependencies = {
        'Flask': 'flask',
        'Pillow': 'PIL',
        'ElevenLabs': 'elevenlabs',
        'Requests': 'requests'
    }
    
    all_ok = True
    for name, module in dependencies.items():
        try:
            __import__(module)
            print(f"✓ {name} installed")
        except ImportError:
            print(f"✗ {name} not installed")
            all_ok = False
    
    return all_ok

def test_ffmpeg():
    """Test ffmpeg availability"""
    print("\nTesting ffmpeg...")
    import subprocess
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, 
                              timeout=5)
        if result.returncode == 0:
            print("✓ ffmpeg is available")
            return True
        else:
            print("✗ ffmpeg returned an error")
            return False
    except FileNotFoundError:
        print("✗ ffmpeg not found in PATH")
        return False
    except Exception as e:
        print(f"✗ ffmpeg error: {e}")
        return False

def test_directories():
    """Test required directories"""
    print("\nTesting directories...")
    directories = ['videos', 'frames', 'static', 'templates', 'sample_data']
    all_ok = True
    for dir_name in directories:
        if os.path.isdir(dir_name):
            print(f"✓ {dir_name}/ exists")
        else:
            print(f"✗ {dir_name}/ missing")
            all_ok = False
    return all_ok

def test_sample_data():
    """Test sample data files"""
    print("\nTesting sample data...")
    import json
    files = ['sample_data/geography.json', 'sample_data/movies.json']
    all_ok = True
    for filepath in files:
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                print(f"✓ {filepath} valid ({len(data.get('questions', []))} questions)")
            except Exception as e:
                print(f"✗ {filepath} invalid: {e}")
                all_ok = False
        else:
            print(f"✗ {filepath} missing")
            all_ok = False
    return all_ok

def main():
    """Run all tests"""
    print("=" * 50)
    print("Quiz Video Generator - Setup Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_dependencies,
        test_ffmpeg,
        test_directories,
        test_database,
        test_sample_data
    ]
    
    results = [test() for test in tests]
    
    print("\n" + "=" * 50)
    if all(results):
        print("✓ All tests passed! Application is ready to run.")
        print("\nTo start the application:")
        print("  python3 app.py")
        print("\nThen visit: http://localhost:5000")
    else:
        print("✗ Some tests failed. Please fix the issues above.")
        sys.exit(1)
    print("=" * 50)

if __name__ == '__main__':
    main()
