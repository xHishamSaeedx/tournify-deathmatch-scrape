#!/usr/bin/env python3
"""
Test the API with real match URL
"""

import requests
import json

def test_api():
    """Test the API with real match URL"""
    print("🧪 Testing API with Real Match URL")
    print("=" * 50)
    
    # API endpoint
    url = "http://localhost:8000/api/v1/scrape-match"
    
    # Test data
    data = {
        "match_url": "https://tracker.gg/valorant/match/e1695f06-0410-4dbb-9b99-bc868af6e46b",
        "include_player_details": True
    }
    
    try:
        print(f"🔍 Testing URL: {data['match_url']}")
        print(f"📡 Sending request to: {url}")
        
        # Send request
        response = requests.post(url, json=data)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"⏱️  Response Time: {response.elapsed.total_seconds():.2f}s")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(f"🎮 Game Mode: {result.get('match_data', {}).get('game_mode', 'Unknown')}")
            print(f"🗺️  Map: {result.get('match_data', {}).get('map_name', 'Unknown')}")
            print(f"👥 Players: {len(result.get('match_data', {}).get('players', []))}")
            
            # Show player details
            players = result.get('match_data', {}).get('players', [])
            for i, player in enumerate(players):
                print(f"  Player {i+1}: {player.get('player_name', 'Unknown')} ({player.get('team', 'Unknown')}) - {player.get('kills', 0)}/{player.get('deaths', 0)}/{player.get('assists', 0)}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_api() 