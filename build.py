import os
import shutil
from flask import Flask
from flask_frozen import Freezer
from app import create_app

def build_static_site():
    # Create Flask app
    app = create_app('production')
    
    # Initialize Frozen-Flask
    freezer = Freezer(app)
    
    # Create dist directory if it doesn't exist
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    os.makedirs('dist')
    
    # Copy static files
    shutil.copytree('app/static', 'dist/static')
    
    # Freeze the app
    freezer.freeze()
    
    print("Build completed successfully!")

if __name__ == '__main__':
    build_static_site()
