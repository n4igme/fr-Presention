#!/usr/bin/env python3
"""
Setup script for the Student Attendance System
This script will install all required dependencies
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required Python packages"""
    print("Installing required packages...")
    
    # Check if requirements.txt exists
    if not os.path.exists('requirements.txt'):
        print("Error: requirements.txt not found!")
        return False
    
    try:
        # Install packages from requirements.txt
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("Successfully installed required packages!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing packages: {e}")
        return False

def main():
    print("Setting up Student Attendance System...")
    print("This script will install all required dependencies.")
    
    if install_requirements():
        print("\nSetup completed successfully!")
        print("\nTo start the application:")
        print("1. Run: python app.py")
        print("2. Open your browser and go to: http://localhost:5000")
        print("3. Login with username: admin, password: admin123")
    else:
        print("\nSetup failed. Please install dependencies manually.")

if __name__ == "__main__":
    main()