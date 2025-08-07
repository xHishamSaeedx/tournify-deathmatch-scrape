import requests
from bs4 import BeautifulSoup
import time
import logging
from typing import Optional, Dict, Any
from datetime import datetime
import re

from ..core.config import settings
from ..schemas.match import MatchResult, PlayerPerformance, GameMode, MapName, ScrapingResponse

# Configure logging
logging.basicConfig(level=getattr(logging, settings.log_level))
logger = logging.getLogger(__name__)


class MatchParser:
    """Service for parsing Valorant match data from tracker.gg"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })
    
    def scrape_match(self, match_url: str) -> ScrapingResponse:
        """Scrape match data from a tracker.gg URL"""
        start_time = time.time()
        
        try:
            logger.info(f"Starting to scrape match: {match_url}")
            
            # Fetch the page
            response = self._make_request(match_url)
            if not response:
                return ScrapingResponse(
                    success=False,
                    error_message="Failed to fetch match page",
                    processing_time=time.time() - start_time
                )
            
            # Parse the HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract match data
            match_data = self._parse_match_data(soup, match_url)
            
            if not match_data:
                return ScrapingResponse(
                    success=False,
                    error_message="Failed to parse match data",
                    processing_time=time.time() - start_time
                )
            
            processing_time = time.time() - start_time
            logger.info(f"Successfully scraped match in {processing_time:.2f}s")
            
            return ScrapingResponse(
                success=True,
                match_data=match_data,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Error scraping match: {str(e)}")
            return ScrapingResponse(
                success=False,
                error_message=f"Unexpected error: {str(e)}",
                processing_time=time.time() - start_time
            )
    
    def _make_request(self, url: str) -> Optional[requests.Response]:
        """Make HTTP request with retry logic"""
        for attempt in range(settings.max_retries):
            try:
                # Add a small delay before each request to avoid rate limiting
                if attempt > 0:
                    time.sleep(settings.delay_between_requests * (attempt + 1))
                
                response = self.session.get(url, timeout=settings.request_timeout)
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                logger.warning(f"Request attempt {attempt + 1} failed: {str(e)}")
                if attempt < settings.max_retries - 1:
                    time.sleep(settings.delay_between_requests)
                else:
                    logger.error(f"All request attempts failed for {url}")
                    return None
    
    def _parse_match_data(self, soup: BeautifulSoup, match_url: str) -> Optional[MatchResult]:
        """Parse match data from BeautifulSoup object"""
        try:
            # Extract basic match info
            match_info = self._extract_match_info(soup)
            if not match_info:
                return None
            
            # Extract player data
            players = self._extract_player_data(soup)
            if not players:
                logger.warning("No player data found")
                return None
            
            # Create match result
            match_result = MatchResult(
                match_id=match_info.get('match_id', 'unknown'),
                match_url=match_url,
                game_mode=match_info.get('game_mode', GameMode.DEATHMATCH),
                map_name=match_info.get('map_name', MapName.ASCENT),
                match_duration=match_info.get('duration', 0),
                match_date=match_info.get('date', datetime.now()),
                red_team_score=match_info.get('red_score', 0),
                blue_team_score=match_info.get('blue_score', 0),
                winner=match_info.get('winner', 'Unknown'),
                players=players,
                total_rounds=match_info.get('total_rounds', 0),
                overtime_rounds=match_info.get('overtime_rounds', 0)
            )
            
            return match_result
            
        except Exception as e:
            logger.error(f"Error parsing match data: {str(e)}")
            return None
    
    def _extract_match_info(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract basic match information"""
        match_info = {}
        
        try:
            # Extract match ID from URL or page
            match_info['match_id'] = 'unknown'  # Will be extracted from URL or page
            
            # Extract game mode
            game_mode_elem = soup.find('div', class_='game-mode')
            if game_mode_elem:
                mode_text = game_mode_elem.get_text().strip().lower()
                if 'deathmatch' in mode_text:
                    match_info['game_mode'] = GameMode.DEATHMATCH
                elif 'unrated' in mode_text:
                    match_info['game_mode'] = GameMode.UNRATED
                elif 'competitive' in mode_text:
                    match_info['game_mode'] = GameMode.COMPETITIVE
                else:
                    match_info['game_mode'] = GameMode.DEATHMATCH
            else:
                match_info['game_mode'] = GameMode.DEATHMATCH
            
            # Extract map name
            map_elem = soup.find('div', class_='map-name')
            if map_elem:
                map_text = map_elem.get_text().strip().lower()
                for map_name in MapName:
                    if map_name.value in map_text:
                        match_info['map_name'] = map_name
                        break
                else:
                    match_info['map_name'] = MapName.ASCENT
            else:
                match_info['map_name'] = MapName.ASCENT
            
            # Extract scores
            score_elems = soup.find_all('div', class_='score')
            if len(score_elems) >= 2:
                match_info['red_score'] = int(score_elems[0].get_text().strip())
                match_info['blue_score'] = int(score_elems[1].get_text().strip())
                
                # Determine winner
                if match_info['red_score'] > match_info['blue_score']:
                    match_info['winner'] = 'Red'
                elif match_info['blue_score'] > match_info['red_score']:
                    match_info['winner'] = 'Blue'
                else:
                    match_info['winner'] = 'Tie'
            else:
                match_info['red_score'] = 0
                match_info['blue_score'] = 0
                match_info['winner'] = 'Unknown'
            
            # Extract duration
            duration_elem = soup.find('div', class_='duration')
            if duration_elem:
                duration_text = duration_elem.get_text().strip()
                match_info['duration'] = self._parse_duration(duration_text)
            else:
                match_info['duration'] = 0
            
            # Extract date
            date_elem = soup.find('div', class_='match-date')
            if date_elem:
                date_text = date_elem.get_text().strip()
                match_info['date'] = self._parse_date(date_text)
            else:
                match_info['date'] = datetime.now()
            
            # Extract round info
            match_info['total_rounds'] = 0
            match_info['overtime_rounds'] = 0
            
        except Exception as e:
            logger.error(f"Error extracting match info: {str(e)}")
        
        return match_info
    
    def _extract_player_data(self, soup: BeautifulSoup) -> list[PlayerPerformance]:
        """Extract player performance data"""
        players = []
        
        try:
            # Find player containers
            player_containers = soup.find_all('div', class_='player-stats')
            
            for container in player_containers:
                try:
                    player_data = self._parse_player_container(container)
                    if player_data:
                        players.append(player_data)
                except Exception as e:
                    logger.warning(f"Error parsing player container: {str(e)}")
                    continue
            
            # If no structured data found, try alternative parsing
            if not players:
                players = self._parse_alternative_player_data(soup)
            
        except Exception as e:
            logger.error(f"Error extracting player data: {str(e)}")
        
        return players
    
    def _parse_player_container(self, container: BeautifulSoup) -> Optional[PlayerPerformance]:
        """Parse individual player container"""
        try:
            # Extract player name
            name_elem = container.find('div', class_='player-name')
            player_name = name_elem.get_text().strip() if name_elem else "Unknown Player"
            
            # Extract team
            team_elem = container.find('div', class_='team')
            team = team_elem.get_text().strip() if team_elem else "Unknown"
            
            # Extract stats
            kills = self._extract_stat(container, 'kills', 0)
            deaths = self._extract_stat(container, 'deaths', 0)
            assists = self._extract_stat(container, 'assists', 0)
            score = self._extract_stat(container, 'score', 0)
            
            # Calculate K/D ratio
            kd_ratio = kills / deaths if deaths > 0 else kills
            
            # Extract additional stats
            headshots = self._extract_stat(container, 'headshots', 0)
            damage_dealt = self._extract_stat(container, 'damage-dealt', 0)
            damage_taken = self._extract_stat(container, 'damage-taken', 0)
            
            # Calculate headshot percentage
            headshot_percentage = (headshots / kills * 100) if kills > 0 else 0.0
            
            return PlayerPerformance(
                player_name=player_name,
                team=team,
                kills=kills,
                deaths=deaths,
                assists=assists,
                score=score,
                kd_ratio=kd_ratio,
                headshots=headshots,
                headshot_percentage=headshot_percentage,
                damage_dealt=damage_dealt,
                damage_taken=damage_taken,
                utility_used=0,  # Not typically available in deathmatch
                first_bloods=0,  # Not typically available in deathmatch
                clutches=0  # Not typically available in deathmatch
            )
            
        except Exception as e:
            logger.warning(f"Error parsing player container: {str(e)}")
            return None
    
    def _parse_alternative_player_data(self, soup: BeautifulSoup) -> list[PlayerPerformance]:
        """Alternative parsing method for player data"""
        players = []
        
        try:
            # Look for table-based player data
            player_tables = soup.find_all('table', class_='player-table')
            
            for table in player_tables:
                rows = table.find_all('tr')
                for row in rows[1:]:  # Skip header row
                    cells = row.find_all('td')
                    if len(cells) >= 6:
                        try:
                            player_name = cells[0].get_text().strip()
                            team = cells[1].get_text().strip()
                            kills = int(cells[2].get_text().strip())
                            deaths = int(cells[3].get_text().strip())
                            assists = int(cells[4].get_text().strip())
                            score = int(cells[5].get_text().strip())
                            
                            kd_ratio = kills / deaths if deaths > 0 else kills
                            
                            players.append(PlayerPerformance(
                                player_name=player_name,
                                team=team,
                                kills=kills,
                                deaths=deaths,
                                assists=assists,
                                score=score,
                                kd_ratio=kd_ratio
                            ))
                        except (ValueError, IndexError):
                            continue
            
        except Exception as e:
            logger.error(f"Error in alternative player parsing: {str(e)}")
        
        return players
    
    def _extract_stat(self, container: BeautifulSoup, stat_name: str, default: int = 0) -> int:
        """Extract a specific stat from player container"""
        try:
            stat_elem = container.find('div', class_=stat_name)
            if stat_elem:
                stat_text = stat_elem.get_text().strip()
                return int(stat_text)
        except (ValueError, AttributeError):
            pass
        return default
    
    def _parse_duration(self, duration_text: str) -> int:
        """Parse duration string to seconds"""
        try:
            # Handle formats like "15:30" or "1:23:45"
            parts = duration_text.split(':')
            if len(parts) == 2:
                minutes, seconds = map(int, parts)
                return minutes * 60 + seconds
            elif len(parts) == 3:
                hours, minutes, seconds = map(int, parts)
                return hours * 3600 + minutes * 60 + seconds
        except (ValueError, IndexError):
            pass
        return 0
    
    def _parse_date(self, date_text: str) -> datetime:
        """Parse date string to datetime"""
        try:
            # Handle various date formats
            date_formats = [
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d",
                "%m/%d/%Y",
                "%d/%m/%Y"
            ]
            
            for fmt in date_formats:
                try:
                    return datetime.strptime(date_text, fmt)
                except ValueError:
                    continue
            
        except Exception:
            pass
        
        return datetime.now()
