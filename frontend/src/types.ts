export interface Song {
  title: string;
  artist: string;
  album?: string;
  duration?: string;
}

export interface SpotifyTrack {
  id: string;
  spotify_id: string;
  name: string;
  title: string;
  artist: string;
  artists?: Array<{ name: string }>;
  album: string;
  match_score: number;
  preview_url?: string;
  external_url?: string;
  external_urls?: { spotify: string };
  duration_ms?: number;
  popularity?: number;
}

export interface MigrationConfig {
  hard_threshold: number;
  reject_threshold: number;
  max_candidates: number;
  dry_run: boolean;
}

export interface MigrationProgress {
  current: number;
  total: number;
  successful: number;
  rejected: number;
  skipped: number;
}

export interface PendingDecision {
  song: Song;
  candidates: SpotifyTrack[];
  match_scores?: number[];
}

export interface MigrationSession {
  session_id: string;
  status: 'processing' | 'completed' | 'error' | 'awaiting_decision';
  progress: MigrationProgress;
  current_song?: Song & { index: number; total: number };
  pending_decision?: PendingDecision;
  
  // Additional fields for display
  total_songs: number;
  processed_songs: number;
  accepted_songs: number;
  rejected_songs: number;
  manual_songs: number;
  
  // Decision flow
  current_decision_needed?: {
    song: Song;
    candidates: SpotifyTrack[];
    match_scores?: number[];
  };
  
  // Optional activity and error tracking
  recent_activity?: Array<{
    action: string;
    song_title: string;
    artist: string;
    timestamp: string;
  }>;
  error_message?: string;
  duration?: string;
  created_at?: string;
  completed_at?: string;
  temp_file?: string;
  config?: MigrationConfig;
  results?: Array<{
    song: Song;
    matched_track_id?: string;
    match_score?: number;
    action: string;
  }>;
}

export interface MigrationResult {
  session_id: string;
  total_songs: number;
  successful: number;
  rejected: number;
  skipped: number;
  success_rate: number;
  results: Array<{
    song: Song;
    matched_track_id?: string;
    match_score?: number;
    action: string;
  }>;
  rejected_songs: Array<{
    song: Song;
    reason: string;
    best_score?: number;
  }>;
}

export interface UploadResponse {
  filename: string;
  total_songs: number;
  songs: Song[];
  preview_truncated: boolean;
}

export interface StartMigrationResponse {
  session_id: string;
  total_songs: number;
}
