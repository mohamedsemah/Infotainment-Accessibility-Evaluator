#!/usr/bin/env python3
"""
Simple test script to verify the installation works
"""

def test_imports():
    """Test that all required modules can be imported"""
    try:
        import fastapi
        print("✅ FastAPI imported successfully")
    except ImportError as e:
        print(f"❌ FastAPI import failed: {e}")
        return False
    
    try:
        import uvicorn
        print("✅ Uvicorn imported successfully")
    except ImportError as e:
        print(f"❌ Uvicorn import failed: {e}")
        return False
    
    try:
        import pydantic
        print("✅ Pydantic imported successfully")
    except ImportError as e:
        print(f"❌ Pydantic import failed: {e}")
        return False
    
    try:
        import jinja2
        print("✅ Jinja2 imported successfully")
    except ImportError as e:
        print(f"❌ Jinja2 import failed: {e}")
        return False
    
    try:
        from PIL import Image
        print("✅ Pillow imported successfully")
    except ImportError as e:
        print(f"❌ Pillow import failed: {e}")
        return False
    
    try:
        import tinycss2
        print("✅ tinycss2 imported successfully")
    except ImportError as e:
        print(f"❌ tinycss2 import failed: {e}")
        return False
    
    try:
        import bs4
        print("✅ BeautifulSoup4 imported successfully")
    except ImportError as e:
        print(f"❌ BeautifulSoup4 import failed: {e}")
        return False
    
    try:
        import lxml
        print("✅ lxml imported successfully")
    except ImportError as e:
        print(f"❌ lxml import failed: {e}")
        return False
    
    try:
        import watchdog
        print("✅ watchdog imported successfully")
    except ImportError as e:
        print(f"❌ watchdog import failed: {e}")
        return False
    
    try:
        import websockets
        print("✅ websockets imported successfully")
    except ImportError as e:
        print(f"❌ websockets import failed: {e}")
        return False
    
    try:
        import httpx
        print("✅ httpx imported successfully")
    except ImportError as e:
        print(f"❌ httpx import failed: {e}")
        return False
    
    try:
        import sqlalchemy
        print("✅ SQLAlchemy imported successfully")
    except ImportError as e:
        print(f"❌ SQLAlchemy import failed: {e}")
        return False
    
    try:
        import reportlab
        print("✅ ReportLab imported successfully")
    except ImportError as e:
        print(f"❌ ReportLab import failed: {e}")
        return False
    
    try:
        import pandas
        print("✅ Pandas imported successfully")
    except ImportError as e:
        print(f"❌ Pandas import failed: {e}")
        return False
    
    try:
        import pytest
        print("✅ pytest imported successfully")
    except ImportError as e:
        print(f"❌ pytest import failed: {e}")
        return False
    
    return True

def test_basic_functionality():
    """Test basic functionality of key modules"""
    try:
        from fastapi import FastAPI
        app = FastAPI()
        print("✅ FastAPI app creation works")
    except Exception as e:
        print(f"❌ FastAPI app creation failed: {e}")
        return False
    
    try:
        from pydantic import BaseModel
        class TestModel(BaseModel):
            name: str
        model = TestModel(name="test")
        print("✅ Pydantic model creation works")
    except Exception as e:
        print(f"❌ Pydantic model creation failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("Testing Infotainment Accessibility Evaluator installation...")
    print("=" * 60)
    
    print("\n1. Testing imports...")
    imports_ok = test_imports()
    
    print("\n2. Testing basic functionality...")
    functionality_ok = test_basic_functionality()
    
    print("\n" + "=" * 60)
    if imports_ok and functionality_ok:
        print("🎉 All tests passed! Installation is working correctly.")
        print("\nYou can now run the application with:")
        print("  uvicorn main:app --reload")
    else:
        print("❌ Some tests failed. Please check the error messages above.")
        print("\nTry installing with the minimal requirements:")
        print("  pip install -r requirements-minimal.txt")
