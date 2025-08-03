"""
FastAPI backend for YT2Spot migration tool.
Serves both the CLI and web frontend.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.responses import RedirectResponse, HTMLResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import uuid
import json
from datetime import datetime
from pathlib import Path
import tempfile
import os
import secrets
import base64
import urllib.parse

# Import existing YT2Spot modules
from yt2spot.input_parser import parse_input_file
from yt2spot.spotify_client import SpotifyClient
from yt2spot.matcher.search import search_spotify_tracks
from yt2spot.matcher.scoring import score_candidates
from yt2spot.matcher.decision import make_decision
from yt2spot.config import ConfigManager

app = FastAPI(
    title="YT2Spot API",
    description="YouTube Music to Spotify Migration API",
    version="1.0.0"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3002", "http://127.0.0.1:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# In-memory storage for migration sessions
migration_sessions: Dict[str, Dict[str, Any]] = {}

# --- OAuth Endpoints ---
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID', 'your_spotify_client_id')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET', 'your_spotify_client_secret')
SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI', 'http://localhost:8000/api/auth/spotify/callback')

YTMUSIC_CLIENT_ID = os.getenv('YTMUSIC_CLIENT_ID', 'your_ytmusic_client_id')
YTMUSIC_CLIENT_SECRET = os.getenv('YTMUSIC_CLIENT_SECRET', 'your_ytmusic_client_secret')
YTMUSIC_REDIRECT_URI = os.getenv('YTMUSIC_REDIRECT_URI', 'http://localhost:8000/api/auth/youtube-music/callback')

@app.get('/api/auth/spotify')
async def spotify_auth(type: str = 'source'):
    state = base64.urlsafe_b64encode(secrets.token_bytes(16)).decode()
    scope = 'playlist-read-private playlist-modify-public playlist-modify-private user-read-email'
    params = {
        'client_id': SPOTIFY_CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': SPOTIFY_REDIRECT_URI,
        'scope': scope,
        'state': state,
        'show_dialog': 'true'
    }
    url = f"https://accounts.spotify.com/authorize?{urllib.parse.urlencode(params)}"
    return RedirectResponse(url)

@app.get('/api/auth/spotify/callback')
async def spotify_callback(request: Request):
    code = request.query_params.get('code')
    state = request.query_params.get('state')
    error = request.query_params.get('error')
    if error:
        return HTMLResponse(f"<script>window.opener.postMessage({{type: 'AUTH_ERROR', error: '{error}'}}, window.origin);window.close();</script>")
    # Exchange code for token
    token_url = 'https://accounts.spotify.com/api/token'
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': SPOTIFY_REDIRECT_URI,
        'client_id': SPOTIFY_CLIENT_ID,
        'client_secret': SPOTIFY_CLIENT_SECRET
    }
    import requests
    resp = requests.post(token_url, data=data)
    token_info = resp.json()
    access_token = token_info.get('access_token')
    # Get user info
    user_resp = requests.get('https://api.spotify.com/v1/me', headers={'Authorization': f'Bearer {access_token}'})
    user_info = user_resp.json()
    # Get playlists
    playlists_resp = requests.get('https://api.spotify.com/v1/me/playlists', headers={'Authorization': f'Bearer {access_token}'})
    playlists = playlists_resp.json().get('items', [])
    playlist_data = [
        {
            'id': p['id'],
            'name': p['name'],
            'trackCount': p['tracks']['total'],
            'imageUrl': p['images'][0]['url'] if p['images'] else None
        } for p in playlists
    ]
    # Send result to frontend
    result = {
        'type': 'AUTH_SUCCESS',
        'accessToken': access_token,
        'user': {
            'id': user_info.get('id'),
            'name': user_info.get('display_name'),
            'imageUrl': user_info.get('images')[0]['url'] if user_info.get('images') else None
        },
        'playlists': playlist_data
    }
    return HTMLResponse(f"<script>window.opener.postMessage({json.dumps(result)}, window.origin);window.close();</script>")

# YouTube Music OAuth (placeholder, as Google OAuth for YT Music is more complex)
@app.get('/api/auth/youtube-music')
async def ytmusic_auth(type: str = 'source'):
    # This is a placeholder. Real YT Music OAuth requires Google OAuth setup.
    return HTMLResponse("<h2>YouTube Music OAuth not implemented. Please use file upload for now.</h2>")

@app.get('/api/auth/youtube-music/callback')
async def ytmusic_callback(request: Request):
    # Placeholder for YT Music OAuth callback
    return HTMLResponse("<script>window.opener.postMessage({type: 'AUTH_ERROR', error: 'YouTube Music OAuth not implemented'}, window.origin);window.close();</script>")

# Pydantic models
class MigrationStartRequest(BaseModel):
    hard_threshold: float = 0.87
    reject_threshold: float = 0.60
    max_candidates: int = 5
    dry_run: bool = False

class MigrationStatus(BaseModel):
    session_id: str
    status: str  # "processing", "completed", "error", "awaiting_decision"
    progress: Dict[str, Any]
    current_song: Optional[Dict[str, Any]] = None
    pending_decision: Optional[Dict[str, Any]] = None

class MatchDecision(BaseModel):
    session_id: str
    action: str  # "accept", "reject", "skip"
    selected_track_id: Optional[str] = None

class MigrationResult(BaseModel):
    session_id: str
    total_songs: int
    successful: int
    rejected: int
    skipped: int
    success_rate: float
    results: List[Dict[str, Any]]
    rejected_songs: List[Dict[str, Any]]

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "YT2Spot API is running!", "version": "1.0.0"}

@app.post("/upload", response_model=Dict[str, Any])
async def upload_file(file: UploadFile = File(...)):
    """Upload music file and parse songs."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Validate file type
    allowed_extensions = {'.txt', '.csv', '.json'}
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        # Parse the file using existing logic
        songs = parse_input_file(tmp_file_path)
        
        # Clean up temp file
        os.unlink(tmp_file_path)
        
        return {
            "filename": file.filename,
            "total_songs": len(songs),
            "songs": [song.model_dump() for song in songs[:10]],  # Preview first 10
            "preview_truncated": len(songs) > 10
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing file: {str(e)}")

@app.post("/migrate/start", response_model=Dict[str, str])
async def start_migration(
    background_tasks: BackgroundTasks,
    request: MigrationStartRequest,
    file: UploadFile = File(...)
):
    """Start a new migration session."""
    session_id = str(uuid.uuid4())
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        # Parse songs
        songs = parse_input_file(tmp_file_path)
        
        # Initialize session
        migration_sessions[session_id] = {
            "status": "processing",
            "songs": songs,
            "config": request.model_dump(),
            "results": [],
            "rejected_songs": [],
            "progress": {
                "current": 0,
                "total": len(songs),
                "successful": 0,
                "rejected": 0,
                "skipped": 0
            },
            "current_song": None,
            "pending_decision": None,
            "created_at": datetime.utcnow(),
            "temp_file": tmp_file_path
        }
        
        # Start migration in background
        background_tasks.add_task(process_migration, session_id)
        
        return {"session_id": session_id, "total_songs": len(songs)}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error starting migration: {str(e)}")

@app.get("/migrate/status/{session_id}", response_model=MigrationStatus)
async def get_migration_status(session_id: str):
    """Get current status of migration session."""
    if session_id not in migration_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = migration_sessions[session_id]
    
    return MigrationStatus(
        session_id=session_id,
        status=session["status"],
        progress=session["progress"],
        current_song=session["current_song"],
        pending_decision=session["pending_decision"]
    )

@app.post("/migrate/decision")
async def submit_decision(decision: MatchDecision):
    """Submit user decision for ambiguous match."""
    if decision.session_id not in migration_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = migration_sessions[decision.session_id]
    
    if session["status"] != "awaiting_decision":
        raise HTTPException(status_code=400, detail="Session not awaiting decision")
    
    # Store the decision and resume processing
    session["user_decision"] = decision.model_dump()
    session["status"] = "processing"
    session["pending_decision"] = None
    
    return {"message": "Decision submitted"}

@app.get("/migrate/results/{session_id}", response_model=MigrationResult)
async def get_migration_results(session_id: str):
    """Get final migration results."""
    if session_id not in migration_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = migration_sessions[session_id]
    
    if session["status"] not in ["completed", "error"]:
        raise HTTPException(status_code=400, detail="Migration not completed")
    
    progress = session["progress"]
    total = progress["total"]
    successful = progress["successful"]
    
    return MigrationResult(
        session_id=session_id,
        total_songs=total,
        successful=successful,
        rejected=progress["rejected"],
        skipped=progress["skipped"],
        success_rate=successful / total * 100 if total > 0 else 0,
        results=session["results"],
        rejected_songs=session["rejected_songs"]
    )

async def process_migration(session_id: str):
    """Background task to process migration."""
    session = migration_sessions[session_id]
    
    try:
        songs = session["songs"]
        config_dict = session["config"]
        
        # Initialize Spotify client
        config_manager = ConfigManager()
        config = config_manager.create_session_config("dummy_input")
        spotify_client = SpotifyClient(config)
        
        if not spotify_client.authenticate():
            session["status"] = "error"
            session["error"] = "Failed to authenticate with Spotify"
            return
        
        # Process each song
        for i, song in enumerate(songs):
            session["progress"]["current"] = i + 1
            session["current_song"] = {
                "title": song.title,
                "artist": song.artist,
                "album": song.album or "",
                "index": i + 1,
                "total": len(songs)
            }
            
            try:
                # Search for matches
                candidates = search_spotify_tracks(spotify_client, song, config_dict["max_candidates"])
                
                if not candidates:
                    # No matches found
                    session["progress"]["rejected"] += 1
                    session["rejected_songs"].append({
                        "song": song.model_dump(),
                        "reason": "No matches found"
                    })
                    continue
                
                # Score candidates
                scored_candidates = score_candidates(song, candidates)
                
                # Make decision
                decision = make_decision(
                    scored_candidates,
                    config_dict["hard_threshold"],
                    config_dict["reject_threshold"],
                    interactive=True  # Always interactive for web UI
                )
                
                if decision["action"] == "prompt":
                    # Wait for user decision
                    session["status"] = "awaiting_decision"
                    session["pending_decision"] = {
                        "song": song.model_dump(),
                        "candidates": [
                            {
                                "spotify_id": c.spotify_track.id,
                                "title": c.spotify_track.name,
                                "artist": ", ".join([artist.name for artist in c.spotify_track.artists]),
                                "album": c.spotify_track.album.name,
                                "match_score": c.match_score,
                                "preview_url": c.spotify_track.preview_url,
                                "external_url": c.spotify_track.external_urls.get("spotify")
                            }
                            for c in scored_candidates[:3]  # Top 3 matches
                        ]
                    }
                    
                    # Wait for user decision
                    while session.get("status") == "awaiting_decision":
                        await asyncio.sleep(1)
                    
                    # Process user decision
                    user_decision = session.get("user_decision")
                    if user_decision:
                        if user_decision["action"] == "accept" and user_decision["selected_track_id"]:
                            # Like the selected track
                            if not config_dict["dry_run"]:
                                spotify_client.like_track(user_decision["selected_track_id"])
                            
                            session["progress"]["successful"] += 1
                            session["results"].append({
                                "song": song.model_dump(),
                                "matched_track_id": user_decision["selected_track_id"],
                                "action": "liked"
                            })
                        else:
                            session["progress"]["rejected"] += 1
                            session["rejected_songs"].append({
                                "song": song.model_dump(),
                                "reason": "User rejected"
                            })
                    
                    # Clear user decision
                    session.pop("user_decision", None)
                    
                elif decision["action"] == "accept":
                    # Auto-accept
                    best_match = decision["track"]
                    if not config_dict["dry_run"]:
                        spotify_client.like_track(best_match.spotify_track.id)
                    
                    session["progress"]["successful"] += 1
                    session["results"].append({
                        "song": song.model_dump(),
                        "matched_track_id": best_match.spotify_track.id,
                        "match_score": best_match.match_score,
                        "action": "auto_liked"
                    })
                    
                else:
                    # Auto-reject
                    session["progress"]["rejected"] += 1
                    session["rejected_songs"].append({
                        "song": song.model_dump(),
                        "reason": "Below threshold",
                        "best_score": scored_candidates[0].match_score if scored_candidates else 0
                    })
                
            except Exception as e:
                session["progress"]["rejected"] += 1
                session["rejected_songs"].append({
                    "song": song.model_dump(),
                    "reason": f"Error: {str(e)}"
                })
        
        # Migration completed
        session["status"] = "completed"
        session["current_song"] = None
        
        # Clean up temp file
        if "temp_file" in session:
            try:
                os.unlink(session["temp_file"])
            except:
                pass
        
    except Exception as e:
        session["status"] = "error"
        session["error"] = str(e)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
