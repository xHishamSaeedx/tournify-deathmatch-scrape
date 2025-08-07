#!/usr/bin/env python3
"""
Test script for Selenium-based Valorant Match Scraper
"""

import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

def test_selenium_parser():
    """Test the Selenium parser"""
    print("🧪 Testing Selenium Match Parser")
    print("=" * 40)
    
    try:
        from app.services.selenium_parser import SeleniumMatchParser
        
        # Create parser instance
        parser = SeleniumMatchParser()
        
        if not parser.driver:
            print("❌ Selenium driver failed to initialize")
            return False
        
        print("✅ Selenium driver initialized successfully")
        
        # Test with a dummy URL (we'll get blocked but can test the setup)
        test_url = "https://tracker.gg/valorant/match/e1695f06-0410-4dbb-9b99-bc868af6e46b"
        
        print(f"🔍 Testing with URL: {test_url}")
        
        # Try to scrape (will likely fail due to 403, but we can test the setup)
        response = parser.scrape_match(test_url)
        
        print(f"📊 Response success: {response.success}")
        print(f"⏱️  Processing time: {response.processing_time:.2f}s")
        
        if response.error_message:
            print(f"⚠️  Error message: {response.error_message}")
        
        # Show the actual response data
        if response.success and response.match_data:
            print(f"🎮 Game Mode: {response.match_data.game_mode}")
            print(f"🗺️  Map: {response.match_data.map_name}")
            print(f"👥 Players found: {len(response.match_data.players)}")
            
            for i, player in enumerate(response.match_data.players):
                print(f"  Player {i+1}: {player.player_name} ({player.team}) - {player.kills}/{player.deaths}/{player.assists}")
        
        # Clean up
        parser.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

def test_imports():
    """Test all imports"""
    print("Testing imports...")
    
    try:
        from selenium import webdriver
        print("✓ Selenium imported")
        
        from webdriver_manager.chrome import ChromeDriverManager
        print("✓ WebDriver Manager imported")
        
        from app.services.selenium_parser import SeleniumMatchParser
        print("✓ SeleniumMatchParser imported")
        
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Selenium Valorant Match Scraper Test")
    print("=" * 40)
    
    success = True
    
    if not test_imports():
        success = False
    
    if not test_selenium_parser():
        success = False
    
    print("\n" + "=" * 40)
    if success:
        print("✅ Selenium parser is ready!")
        print("\nNote: Tracker.gg may still block requests, but the parser setup is working.")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 