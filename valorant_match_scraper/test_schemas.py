from pydantic import BaseModel

class MatchRequest(BaseModel):
    match_url: str

class PlayerResult(BaseModel):
    player_id: str
    kills: int
    acs: int
    position: int

print("Test schemas created successfully")
print(f"MatchRequest: {MatchRequest}")
print(f"PlayerResult: {PlayerResult}") 