# Valorant Match Scraper

A FastAPI-based web service for scraping Valorant match data from tracker.gg. This service provides RESTful APIs to extract match statistics, player performance data, and game information from Valorant match pages.

## Features

- **Match Data Scraping**: Extract comprehensive match data from tracker.gg URLs
- **Player Statistics**: Detailed player performance metrics including K/D ratio, headshots, damage dealt
- **Multiple Game Modes**: Support for Deathmatch, Unrated, Competitive, and other game modes
- **Map Information**: Track which maps were played in each match
- **Batch Processing**: Scrape multiple matches simultaneously
- **RESTful API**: Clean, documented API endpoints with automatic OpenAPI documentation
- **Error Handling**: Robust error handling with detailed error messages
- **Rate Limiting**: Built-in request delays to respect website policies

## Project Structure

```
valorant_match_scraper/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── endpoints.py    # API route definitions
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py           # Application configuration
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── match.py            # Pydantic data models
│   └── services/
│       ├── __init__.py
│       └── match_parser.py     # Web scraping logic
├── requirements.txt            # Python dependencies
├── test_schemas.py            # Schema validation tests
└── README.md                  # This file
```

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd valorant_match_scraper
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Starting the Server

Run the FastAPI application:

```bash
python -m app.main
```

Or using uvicorn directly:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at:
- **API Base URL**: `http://localhost:8000`
- **Interactive Documentation**: `http://localhost:8000/docs`
- **Alternative Documentation**: `http://localhost:8000/redoc`

### API Endpoints

#### Health Check
```http
GET /health
GET /api/v1/health
```

#### Scrape Single Match
```http
POST /api/v1/scrape-match
Content-Type: application/json

{
  "match_url": "https://tracker.gg/valorant/match/example-match-id",
  "include_player_details": true,
  "include_round_data": false
}
```

#### Scrape Match by ID
```http
GET /api/v1/scrape-match/{match_id}
```

#### Batch Scrape Multiple Matches
```http
POST /api/v1/batch-scrape
Content-Type: application/json

[
  "https://tracker.gg/valorant/match/match1",
  "https://tracker.gg/valorant/match/match2"
]
```

#### Get Available Game Modes
```http
GET /api/v1/game-modes
```

#### Get Available Maps
```http
GET /api/v1/maps
```

#### Get Service Statistics
```http
GET /api/v1/stats
```

### Example Usage

#### Python Client Example

```python
import requests

# Scrape a single match
url = "http://localhost:8000/api/v1/scrape-match"
data = {
    "match_url": "https://tracker.gg/valorant/match/your-match-id",
    "include_player_details": True
}

response = requests.post(url, json=data)
match_data = response.json()

if match_data["success"]:
    print(f"Match: {match_data['match_data']['game_mode']}")
    print(f"Map: {match_data['match_data']['map_name']}")
    print(f"Winner: {match_data['match_data']['winner']}")
    
    for player in match_data['match_data']['players']:
        print(f"{player['player_name']}: {player['kills']}/{player['deaths']}/{player['assists']}")
```

#### cURL Example

```bash
# Scrape a match
curl -X POST "http://localhost:8000/api/v1/scrape-match" \
     -H "Content-Type: application/json" \
     -d '{
       "match_url": "https://tracker.gg/valorant/match/example-id",
       "include_player_details": true
     }'

# Get health status
curl "http://localhost:8000/api/v1/health"
```

## Data Models

### MatchResult
```python
{
  "match_id": "string",
  "match_url": "string",
  "game_mode": "deathmatch|unrated|competitive|...",
  "map_name": "bind|haven|split|...",
  "match_duration": 900,  # seconds
  "match_date": "2024-01-01T12:00:00",
  "red_team_score": 13,
  "blue_team_score": 11,
  "winner": "Red|Blue|Tie",
  "players": [...],  # List of PlayerPerformance objects
  "total_rounds": 24,
  "overtime_rounds": 0
}
```

### PlayerPerformance
```python
{
  "player_name": "string",
  "team": "Red|Blue",
  "kills": 15,
  "deaths": 8,
  "assists": 3,
  "score": 4500,
  "kd_ratio": 1.875,
  "headshots": 8,
  "headshot_percentage": 53.33,
  "damage_dealt": 3200,
  "damage_taken": 1800,
  "utility_used": 12,
  "first_bloods": 2,
  "clutches": 1
}
```

## Configuration

The application uses Pydantic Settings for configuration. You can override settings using environment variables:

```bash
# Environment variables
export API_TITLE="Custom API Title"
export API_VERSION="2.0.0"
export BASE_URL="https://tracker.gg/valorant"
export REQUEST_TIMEOUT=30
export MAX_RETRIES=5
export DELAY_BETWEEN_REQUESTS=1.5
export LOG_LEVEL="DEBUG"
```

Or create a `.env` file:

```env
API_TITLE=Valorant Match Scraper API
API_VERSION=1.0.0
BASE_URL=https://tracker.gg/valorant
REQUEST_TIMEOUT=30
MAX_RETRIES=3
DELAY_BETWEEN_REQUESTS=1.0
LOG_LEVEL=INFO
```

## Error Handling

The API provides detailed error responses:

```json
{
  "detail": "Error description",
  "error": "Detailed error message (in DEBUG mode)"
}
```

Common HTTP status codes:
- `200`: Success
- `400`: Bad Request (invalid URL, malformed request)
- `404`: Not Found (match not found)
- `422`: Unprocessable Entity (scraping failed)
- `500`: Internal Server Error

## Development

### Running Tests

```bash
python test_schemas.py
```

### Code Structure

- **`app/main.py`**: FastAPI application setup and middleware
- **`app/api/v1/endpoints.py`**: API route definitions
- **`app/services/match_parser.py`**: Web scraping logic using BeautifulSoup
- **`app/schemas/match.py`**: Pydantic data models for request/response validation
- **`app/core/config.py`**: Application configuration using Pydantic Settings

### Adding New Features

1. **New Endpoints**: Add routes in `app/api/v1/endpoints.py`
2. **New Data Models**: Define schemas in `app/schemas/match.py`
3. **New Scraping Logic**: Extend `app/services/match_parser.py`
4. **Configuration**: Update `app/core/config.py`

## Limitations

- Only supports tracker.gg/valorant URLs
- Rate limiting to respect website policies
- Batch processing limited to 10 URLs per request
- Some match data may not be available depending on the match page structure

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Check the API documentation at `/docs`
- Review the error messages in the response
- Check the application logs for detailed error information 