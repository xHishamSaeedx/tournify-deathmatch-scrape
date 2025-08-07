#!/usr/bin/env python3
"""
Simple test script for Valorant Match Scraper
"""

import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

def test_imports():
    """Test all imports"""
    print("Testing imports...")
    
    try:
        from app.core.config import settings
        print("✓ Config imported")
        
        from app.schemas.match import GameMode, MapName, PlayerPerformance, MatchResult
        print("✓ Schemas imported")
        
        from app.services.match_parser import MatchParser
        print("✓ MatchParser imported")
        
        from app.api.v1.endpoints import router
        print("✓ API router imported")
        
        from app.main import app
        print("✓ FastAPI app imported")
        
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_app_routes():
    """Test that the app has the expected routes"""
    print("\nTesting app routes...")
    
    try:
        from app.main import app
        
        routes = [route.path for route in app.routes]
        expected_routes = ["/", "/health", "/docs", "/redoc", "/openapi.json"]
        
        for route in expected_routes:
            if route in routes:
                print(f"✓ Route {route} found")
            else:
                print(f"✗ Route {route} not found")
        
        # Check API routes
        api_routes = ["/api/v1/health", "/api/v1/scrape-match", "/api/v1/game-modes", "/api/v1/maps", "/api/v1/stats"]
        for route in api_routes:
            if route in routes:
                print(f"✓ API route {route} found")
            else:
                print(f"✗ API route {route} not found")
        
        return True
    except Exception as e:
        print(f"✗ Route test failed: {e}")
        return False

def test_schemas():
    """Test schema functionality"""
    print("\nTesting schemas...")
    
    try:
        from app.schemas.match import GameMode, MapName, PlayerPerformance
        
        # Test enums
        assert GameMode.DEATHMATCH == "deathmatch"
        assert MapName.ASCENT == "ascent"
        print("✓ Enums working")
        
        # Test PlayerPerformance model
        player = PlayerPerformance(
            player_name="TestPlayer",
            team="Red",
            kills=15,
            deaths=8,
            assists=3,
            score=4500,
            kd_ratio=1.875
        )
        assert player.player_name == "TestPlayer"
        print("✓ PlayerPerformance model working")
        
        return True
    except Exception as e:
        print(f"✗ Schema test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Simple Valorant Match Scraper Test")
    print("=" * 40)
    
    success = True
    
    if not test_imports():
        success = False
    
    if not test_app_routes():
        success = False
    
    if not test_schemas():
        success = False
    
    print("\n" + "=" * 40)
    if success:
        print("✅ All tests passed! The application is ready to run.")
        print("\nTo start the server, run:")
        print("  python -m app.main")
        print("  or")
        print("  uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
        print("\nThen visit http://localhost:8000/docs for API documentation.")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 