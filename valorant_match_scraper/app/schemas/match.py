from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class GameMode(str, Enum):
    DEATHMATCH = "deathmatch"
    UNRATED = "unrated"
    COMPETITIVE = "competitive"
    SPIKE_RUSH = "spike_rush"
    ESCALATION = "escalation"
    REPLICATION = "replication"
    CUSTOM = "custom"


class MapName(str, Enum):
    BIND = "bind"
    HAVEN = "haven"
    SPLIT = "split"
    ASCENT = "ascent"
    ICEBOX = "icebox"
    BREEZE = "breeze"
    FRACTURE = "fracture"
    PEARL = "pearl"
    LOTUS = "lotus"
    SUNSET = "sunset"


class PlayerPerformance(BaseModel):
    """Player performance in a match"""
    player_name: str = Field(..., description="Player's display name")
    team: str = Field(..., description="Team (Red/Blue)")
    kills: int = Field(..., description="Number of kills")
    deaths: int = Field(..., description="Number of deaths")
    assists: int = Field(..., description="Number of assists")
    score: int = Field(..., description="Total score")
    kd_ratio: float = Field(..., description="Kill/Death ratio")
    headshots: int = Field(0, description="Number of headshots")
    headshot_percentage: float = Field(0.0, description="Headshot percentage")
    damage_dealt: int = Field(0, description="Total damage dealt")
    damage_taken: int = Field(0, description="Total damage taken")
    utility_used: int = Field(0, description="Number of utility items used")
    first_bloods: int = Field(0, description="Number of first bloods")
    clutches: int = Field(0, description="Number of clutches")


class MatchResult(BaseModel):
    """Complete match result data"""
    match_id: str = Field(..., description="Unique match identifier")
    match_url: str = Field(..., description="URL to the match page")
    game_mode: GameMode = Field(..., description="Game mode played")
    map_name: MapName = Field(..., description="Map played")
    match_duration: int = Field(..., description="Match duration in seconds")
    match_date: datetime = Field(..., description="When the match was played")
    red_team_score: int = Field(..., description="Red team final score")
    blue_team_score: int = Field(..., description="Blue team final score")
    winner: str = Field(..., description="Winning team (Red/Blue)")
    players: List[PlayerPerformance] = Field(..., description="All players' performance data")
    total_rounds: int = Field(0, description="Total number of rounds played")
    overtime_rounds: int = Field(0, description="Number of overtime rounds")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ScrapingRequest(BaseModel):
    """Request model for scraping matches"""
    match_url: str = Field(..., description="URL of the match to scrape")
    include_player_details: bool = Field(True, description="Whether to include detailed player stats")
    include_round_data: bool = Field(False, description="Whether to include round-by-round data")


class ScrapingResponse(BaseModel):
    """Response model for scraping operations"""
    success: bool = Field(..., description="Whether scraping was successful")
    match_data: Optional[MatchResult] = Field(None, description="Scraped match data")
    error_message: Optional[str] = Field(None, description="Error message if scraping failed")
    processing_time: float = Field(..., description="Time taken to process the request") 