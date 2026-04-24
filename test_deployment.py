#!/usr/bin/env python
"""
Local testing script before Vercel deployment
Run this to verify everything works locally
"""
import os
import sys

# Add root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all imports work"""
    print("🔍 Testing imports...")
    try:
        from dotenv import load_dotenv
        print("  ✅ python-dotenv")
        
        from flask import Flask
        print("  ✅ Flask")
        
        from database_init import db
        print("  ✅ database_init")
        
        from models.voters import Voter
        print("  ✅ models.voters")
        
        from routes.auth import auth_bp
        print("  ✅ routes.auth")
        
        print("\n✅ All imports successful!\n")
        return True
    except Exception as e:
        print(f"\n❌ Import failed: {e}\n")
        return False


def test_app_creation():
    """Test if Flask app can be created"""
    print("🔍 Testing Flask app creation...")
    try:
        from api.index import app
        print("  ✅ Flask app created successfully")
        print(f"  - Debug mode: {app.debug}")
        print(f"  - Database URI: {app.config['SQLALCHEMY_DATABASE_URI'][:50]}...")
        print(f"  - Upload folder: {app.config['UPLOAD_FOLDER']}")
        print("\n✅ App configuration looks good!\n")
        return True
    except Exception as e:
        print(f"\n❌ App creation failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_env_vars():
    """Test environment variables"""
    print("🔍 Checking environment variables...")
    from dotenv import load_dotenv
    load_dotenv()
    
    important_vars = [
        "SECRET_KEY",
        "DATABASE_URL",
        "FLASK_ENV",
        "groq_api",
        "RECAPTCHA_SITE_KEY",
        "BREVO_API_KEY"
    ]
    
    found = 0
    for var in important_vars:
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var}: Set (length: {len(value)})")
            found += 1
        else:
            print(f"  ⚠️  {var}: Not set (will be needed for Vercel)")
    
    print(f"\n  Found {found}/{len(important_vars)} variables\n")
    return found > 0


if __name__ == "__main__":
    print("=" * 60)
    print("DIGITAL CIVIC PARTICIPATION PLATFORM")
    print("Pre-Deployment Local Test")
    print("=" * 60 + "\n")
    
    results = {
        "Imports": test_imports(),
        "App Creation": test_app_creation(),
        "Environment Variables": test_env_vars(),
    }
    
    print("=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    all_pass = all(results.values())
    print("=" * 60)
    
    if all_pass:
        print("\n✅ All tests passed! You're ready to deploy.")
        print("\nNext steps:")
        print("1. Add environment variables to Vercel (see VERCEL_SETUP.md)")
        print("2. Set up PostgreSQL database")
        print("3. git push to trigger Vercel deployment")
    else:
        print("\n❌ Some tests failed. Fix errors before deploying.")
    
    print("\n" + "=" * 60 + "\n")
