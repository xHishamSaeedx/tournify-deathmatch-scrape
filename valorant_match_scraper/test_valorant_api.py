#!/usr/bin/env python3
"""
Test script for Valorant API
Makes a GET request to /val/match/v1/matches/{matchId} endpoint
"""

import requests
import json
from datetime import datetime

def test_valorant_api():
    """Test the Valorant API with the specified match ID"""
    print("🧪 Testing Valorant API")
    print("=" * 50)
    
    # API Configuration
    match_id = "e1695f06-0410-4dbb-9b99-bc868af6e46b"
    region = "AP"
    api_key = "RGAPI-c34e511e-bfbd-419e-8d65-384c400c0587"
    
    # Construct the API URL
    base_url = f"https://{region.lower()}.api.riotgames.com"
    endpoint = f"/val/match/v1/matches/{match_id}"
    url = base_url + endpoint
    
    # Headers
    headers = {
        "X-Riot-Token": api_key,
        "User-Agent": "Tournify-Match-Scraper/1.0"
    }
    
    try:
        print(f"🔍 Match ID: {match_id}")
        print(f"🌍 Region: {region}")
        print(f"📡 API URL: {url}")
        print(f"🔑 API Key: {api_key[:10]}...")
        print("-" * 50)
        
        # Make the GET request
        print("🚀 Sending GET request...")
        response = requests.get(url, headers=headers)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"⏱️  Response Time: {response.elapsed.total_seconds():.2f}s")
        print(f"📄 Content-Type: {response.headers.get('content-type', 'Unknown')}")
        
        if response.status_code == 200:
            print("✅ Success! Match data retrieved")
            print("-" * 50)
            
            # Parse the response
            match_data = response.json()
            
            # Display basic match information
            match_info = match_data.get('matchInfo', {})
            print(f"🎮 Game Mode: {match_info.get('gameMode', 'Unknown')}")
            print(f"🗺️  Map ID: {match_info.get('mapId', 'Unknown')}")
            print(f"⏰ Game Length: {match_info.get('gameLengthMillis', 0) // 1000}s")
            print(f"🏆 Is Completed: {match_info.get('isCompleted', False)}")
            print(f"🏅 Is Ranked: {match_info.get('isRanked', False)}")
            print(f"🌍 Region: {match_info.get('region', 'Unknown')}")
            
            # Display player information
            players = match_data.get('players', [])
            print(f"\n👥 Players ({len(players)}):")
            for i, player in enumerate(players):
                player_name = f"{player.get('gameName', 'Unknown')}#{player.get('tagLine', '')}"
                team_id = player.get('teamId', 'Unknown')
                character_id = player.get('characterId', 'Unknown')
                stats = player.get('stats', {})
                
                print(f"  {i+1}. {player_name}")
                print(f"     Team: {team_id}")
                print(f"     Agent: {character_id}")
                print(f"     Score: {stats.get('score', 0)}")
                print(f"     K/D/A: {stats.get('kills', 0)}/{stats.get('deaths', 0)}/{stats.get('assists', 0)}")
                print(f"     Rounds Played: {stats.get('roundsPlayed', 0)}")
                print()
            
            # Display team information
            teams = match_data.get('teams', [])
            print(f"🏆 Teams ({len(teams)}):")
            for team in teams:
                team_id = team.get('teamId', 'Unknown')
                won = team.get('won', False)
                rounds_won = team.get('roundsWon', 0)
                rounds_played = team.get('roundsPlayed', 0)
                num_points = team.get('numPoints', 0)
                
                print(f"  Team {team_id}: {'✅ Won' if won else '❌ Lost'}")
                print(f"    Rounds: {rounds_won}/{rounds_played}")
                print(f"    Points: {num_points}")
                print()
            
            # Save the full response to a file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"match_data_{match_id}_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(match_data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Full match data saved to: {filename}")
            
        elif response.status_code == 404:
            print("❌ Error: Match not found")
            print("This could mean:")
            print("  - The match ID is incorrect")
            print("  - The match is not available in the specified region")
            print("  - The match is too old or not accessible")
        elif response.status_code == 401:
            print("❌ Error: Unauthorized")
            print("Check your API key")
        elif response.status_code == 403:
            print("❌ Error: Forbidden")
            print("API key may be invalid or expired")
        elif response.status_code == 429:
            print("❌ Error: Rate limit exceeded")
            print("Try again later")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Check your internet connection")
    except requests.exceptions.Timeout:
        print("❌ Timeout Error: Request took too long")
    except json.JSONDecodeError:
        print("❌ JSON Decode Error: Invalid response format")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Unexpected Error: {str(e)}")

if __name__ == "__main__":
    test_valorant_api() 