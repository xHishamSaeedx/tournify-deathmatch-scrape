from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import List
import logging

from ...schemas.match import (
    ScrapingRequest, 
    ScrapingResponse, 
    GameMode, 
    MapName
)
from ...services.match_parser import MatchParser
from ...services.selenium_parser import SeleniumMatchParser
from ...core.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/v1", tags=["valorant-matches"])

# Initialize match parsers
match_parser = MatchParser()
selenium_parser = SeleniumMatchParser()


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "valorant-match-scraper",
        "version": settings.api_version
    }


@router.post("/scrape-match", response_model=ScrapingResponse)
async def scrape_match(request: ScrapingRequest):
    """
    Scrape match data from a tracker.gg URL
    """
    try:
        logger.info(f"Received scrape request for URL: {request.match_url}")
        
        # Validate URL
        if not request.match_url.startswith("https://tracker.gg/valorant"):
            raise HTTPException(
                status_code=400,
                detail="Invalid URL. Only tracker.gg/valorant URLs are supported."
            )
        
        # Try Selenium parser first (more reliable for tracker.gg)
        response = selenium_parser.scrape_match(request.match_url)
        
        # If Selenium fails, fall back to requests parser
        if not response.success:
            logger.info("Selenium parser failed, trying requests parser...")
            response = match_parser.scrape_match(request.match_url)
        
        if not response.success:
            raise HTTPException(
                status_code=422,
                detail=response.error_message or "Failed to scrape match data"
            )
        
        logger.info(f"Successfully scraped match: {request.match_url}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in scrape_match: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/scrape-match/{match_id}")
async def scrape_match_by_id(match_id: str):
    """
    Scrape match data by match ID
    """
    try:
        # Construct URL from match ID
        match_url = f"https://tracker.gg/valorant/match/{match_id}"
        
        logger.info(f"Scraping match by ID: {match_id}")
        
        # Scrape the match
        response = match_parser.scrape_match(match_url)
        
        if not response.success:
            raise HTTPException(
                status_code=404,
                detail=response.error_message or f"Match with ID {match_id} not found"
            )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in scrape_match_by_id: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/game-modes")
async def get_game_modes():
    """Get list of available game modes"""
    return {
        "game_modes": [
            {"value": mode.value, "name": mode.name} 
            for mode in GameMode
        ]
    }


@router.get("/maps")
async def get_maps():
    """Get list of available maps"""
    return {
        "maps": [
            {"value": map_name.value, "name": map_name.name} 
            for map_name in MapName
        ]
    }


@router.get("/stats")
async def get_scraping_stats():
    """Get scraping service statistics"""
    return {
        "service": "valorant-match-scraper",
        "version": settings.api_version,
        "base_url": settings.base_url,
        "max_retries": settings.max_retries,
        "request_timeout": settings.request_timeout,
        "delay_between_requests": settings.delay_between_requests
    }


@router.post("/batch-scrape")
async def batch_scrape_matches(urls: List[str]):
    """
    Scrape multiple matches in batch
    """
    try:
        if len(urls) > 10:  # Limit batch size
            raise HTTPException(
                status_code=400,
                detail="Batch size too large. Maximum 10 URLs allowed."
            )
        
        results = []
        for url in urls:
            try:
                response = match_parser.scrape_match(url)
                results.append(response)
            except Exception as e:
                logger.warning(f"Failed to scrape {url}: {str(e)}")
                results.append(ScrapingResponse(
                    success=False,
                    error_message=str(e),
                    processing_time=0.0
                ))
        
        return {
            "total_requests": len(urls),
            "successful": sum(1 for r in results if r.success),
            "failed": sum(1 for r in results if not r.success),
            "results": results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in batch_scrape: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


# Note: Exception handlers should be registered on the main app, not on routers
# These are handled globally in app/main.py 