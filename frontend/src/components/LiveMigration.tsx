import React, { useState, useEffect, useRef } from 'react';
import { 
  Music, 
  CheckCircle, 
  AlertCircle, 
  Clock, 
  TrendingUp, 
  Shuffle,
  Volume2,
  ExternalLink,
  Pause,
  Play,
  SkipForward
} from 'lucide-react';
import { AuthenticationData } from './Authentication';

interface LiveMigrationProps {
  authData: AuthenticationData;
  selectedPlaylist?: string;
}

interface MigrationProgress {
  status: 'initializing' | 'running' | 'paused' | 'completed' | 'error';
  totalTracks: number;
  processedTracks: number;
  successfulMatches: number;
  skippedTracks: number;
  currentTrack?: {
    name: string;
    artist: string;
    album?: string;
    imageUrl?: string;
    matchStatus: 'searching' | 'found' | 'not-found' | 'added';
  };
  destinationPlaylist?: {
    id: string;
    name: string;
    url: string;
    trackCount: number;
  };
  recentlyAdded: Array<{
    id: string;
    name: string;
    artist: string;
    addedAt: string;
    imageUrl?: string;
  }>;
  estimatedTimeRemaining?: number;
  migrationSpeed: number; // tracks per minute
}

export const LiveMigration: React.FC<LiveMigrationProps> = ({
  authData
}) => {
  const [progress, setProgress] = useState<MigrationProgress>({
    status: 'initializing',
    totalTracks: 0,
    processedTracks: 0,
    successfulMatches: 0,
    skippedTracks: 0,
    recentlyAdded: [],
    migrationSpeed: 0
  });

  const [isPaused, setIsPaused] = useState(false);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  // Mock real-time updates for demonstration
  useEffect(() => {
    const startMigration = async () => {
      // Initialize migration
      setProgress(prev => ({
        ...prev,
        status: 'initializing',
        totalTracks: 127, // Mock total
        destinationPlaylist: {
          id: 'new-playlist-id',
          name: `Migrated from ${authData.sourceAuth?.service || 'Source'}`,
          url: 'https://spotify.com/playlist/example',
          trackCount: 0
        }
      }));

      // Start processing after a delay
      setTimeout(() => {
        setProgress(prev => ({ ...prev, status: 'running' }));
        startRealTimeUpdates();
      }, 2000);
    };

    startMigration();

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  const startRealTimeUpdates = () => {
    if (intervalRef.current) return;

    const mockTracks = [
      { name: 'Bohemian Rhapsody', artist: 'Queen', album: 'A Night at the Opera' },
      { name: 'Stairway to Heaven', artist: 'Led Zeppelin', album: 'Led Zeppelin IV' },
      { name: 'Hotel California', artist: 'Eagles', album: 'Hotel California' },
      { name: 'Sweet Child O\' Mine', artist: 'Guns N\' Roses', album: 'Appetite for Destruction' },
      { name: 'Billie Jean', artist: 'Michael Jackson', album: 'Thriller' },
      { name: 'Like a Rolling Stone', artist: 'Bob Dylan', album: 'Highway 61 Revisited' },
      { name: 'Smells Like Teen Spirit', artist: 'Nirvana', album: 'Nevermind' },
      { name: 'What\'s Going On', artist: 'Marvin Gaye', album: 'What\'s Going On' },
      { name: 'Imagine', artist: 'John Lennon', album: 'Imagine' },
      { name: 'Hey Jude', artist: 'The Beatles', album: 'Hey Jude' }
    ];

    let trackIndex = 0;

    intervalRef.current = setInterval(() => {
      if (isPaused) return;

      setProgress(prev => {
        if (prev.processedTracks >= prev.totalTracks) {
          if (intervalRef.current) {
            clearInterval(intervalRef.current);
            intervalRef.current = null;
          }
          return { ...prev, status: 'completed' };
        }

        const currentTrack = mockTracks[trackIndex % mockTracks.length];
        const isSuccessful = Math.random() > 0.1; // 90% success rate
        
        trackIndex++;

        const newProcessed = prev.processedTracks + 1;
        const newSuccessful = prev.successfulMatches + (isSuccessful ? 1 : 0);
        const newSkipped = prev.skippedTracks + (isSuccessful ? 0 : 1);

        const newRecentlyAdded = isSuccessful ? [
          {
            id: `track-${newProcessed}`,
            name: currentTrack.name,
            artist: currentTrack.artist,
            addedAt: new Date().toISOString(),
            imageUrl: `https://picsum.photos/64/64?random=${newProcessed}`
          },
          ...prev.recentlyAdded.slice(0, 4)
        ] : prev.recentlyAdded;

        const migrationSpeed = (newProcessed / (Date.now() / 60000)) || 0;
        const estimatedTimeRemaining = (prev.totalTracks - newProcessed) / (migrationSpeed || 1);

        return {
          ...prev,
          processedTracks: newProcessed,
          successfulMatches: newSuccessful,
          skippedTracks: newSkipped,
          currentTrack: {
            ...currentTrack,
            matchStatus: isSuccessful ? 'found' : 'not-found'
          },
          recentlyAdded: newRecentlyAdded,
          destinationPlaylist: prev.destinationPlaylist ? {
            ...prev.destinationPlaylist,
            trackCount: newSuccessful
          } : undefined,
          migrationSpeed,
          estimatedTimeRemaining
        };
      });
    }, 1500); // Update every 1.5 seconds
  };

  const togglePause = () => {
    setIsPaused(!isPaused);
    if (isPaused && progress.status !== 'completed') {
      startRealTimeUpdates();
    }
  };

  const completionPercentage = progress.totalTracks > 0 
    ? (progress.processedTracks / progress.totalTracks) * 100 
    : 0;

  const successRate = progress.processedTracks > 0
    ? (progress.successfulMatches / progress.processedTracks) * 100
    : 0;

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-3xl font-bold text-white mb-2">
          🎵 Live Migration in Progress
        </h2>
        <p className="text-spotify-gray">
          Watch your playlist grow in real-time
        </p>
      </div>

      {/* Main Progress */}
      <div className="card bg-gradient-to-r from-spotify-green/20 to-blue-500/20 border-spotify-green/30">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-4">
            <div className="relative">
              <div className="w-16 h-16 rounded-full bg-spotify-green/20 flex items-center justify-center">
                {progress.status === 'running' && !isPaused ? (
                  <Music className="h-8 w-8 text-spotify-green animate-pulse" />
                ) : progress.status === 'completed' ? (
                  <CheckCircle className="h-8 w-8 text-green-400" />
                ) : (
                  <Clock className="h-8 w-8 text-spotify-gray" />
                )}
              </div>
              {progress.status === 'running' && (
                <div className="absolute -top-1 -right-1 w-6 h-6 bg-green-400 rounded-full flex items-center justify-center">
                  <div className="w-2 h-2 bg-white rounded-full animate-ping"></div>
                </div>
              )}
            </div>
            
            <div>
              <h3 className="text-xl font-semibold text-white">
                {progress.processedTracks} / {progress.totalTracks} tracks processed
              </h3>
              <p className="text-spotify-gray">
                {progress.status === 'running' && !isPaused && 'Migration in progress...'}
                {progress.status === 'paused' && 'Migration paused'}
                {progress.status === 'completed' && 'Migration completed successfully!'}
                {progress.status === 'initializing' && 'Preparing migration...'}
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            {progress.status === 'running' && (
              <button
                onClick={togglePause}
                className="btn-secondary flex items-center space-x-2"
              >
                {isPaused ? <Play className="h-4 w-4" /> : <Pause className="h-4 w-4" />}
                <span>{isPaused ? 'Resume' : 'Pause'}</span>
              </button>
            )}
            
            {progress.destinationPlaylist && (
              <a
                href={progress.destinationPlaylist.url}
                target="_blank"
                rel="noopener noreferrer"
                className="btn-primary flex items-center space-x-2"
              >
                <ExternalLink className="h-4 w-4" />
                <span>View Playlist</span>
              </a>
            )}
          </div>
        </div>

        {/* Progress Bar */}
        <div className="relative">
          <div className="w-full bg-gray-700 rounded-full h-3 overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-spotify-green to-blue-400 transition-all duration-500 ease-out"
              style={{ width: `${completionPercentage}%` }}
            >
              <div className="h-full bg-white/20 animate-pulse"></div>
            </div>
          </div>
          <div className="flex justify-between text-sm text-spotify-gray mt-2">
            <span>{completionPercentage.toFixed(1)}% complete</span>
            {progress.estimatedTimeRemaining && progress.estimatedTimeRemaining > 0 && (
              <span>~{Math.round(progress.estimatedTimeRemaining)} min remaining</span>
            )}
          </div>
        </div>
      </div>

      {/* Live Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card bg-white/10 backdrop-blur border-gray-700">
          <div className="flex items-center space-x-3">
            <CheckCircle className="h-8 w-8 text-green-400" />
            <div>
              <div className="text-2xl font-bold text-white">{progress.successfulMatches}</div>
              <div className="text-sm text-spotify-gray">Songs Added</div>
              <div className="text-xs text-green-300">{successRate.toFixed(1)}% success rate</div>
            </div>
          </div>
        </div>

        <div className="card bg-white/10 backdrop-blur border-gray-700">
          <div className="flex items-center space-x-3">
            <TrendingUp className="h-8 w-8 text-blue-400" />
            <div>
              <div className="text-2xl font-bold text-white">{progress.migrationSpeed.toFixed(1)}</div>
              <div className="text-sm text-spotify-gray">Songs/Min</div>
              <div className="text-xs text-blue-300">Migration speed</div>
            </div>
          </div>
        </div>

        <div className="card bg-white/10 backdrop-blur border-gray-700">
          <div className="flex items-center space-x-3">
            <AlertCircle className="h-8 w-8 text-orange-400" />
            <div>
              <div className="text-2xl font-bold text-white">{progress.skippedTracks}</div>
              <div className="text-sm text-spotify-gray">Skipped</div>
              <div className="text-xs text-orange-300">Not found</div>
            </div>
          </div>
        </div>
      </div>

      {/* Current Track & Recently Added */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Current Track */}
        {progress.currentTrack && progress.status === 'running' && (
          <div className="card bg-white/10 backdrop-blur border-gray-700">
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center space-x-2">
              <Volume2 className="h-5 w-5" />
              <span>Currently Processing</span>
            </h3>
            
            <div className="flex items-center space-x-4">
              <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
                <Music className="h-8 w-8 text-white" />
              </div>
              
              <div className="flex-1">
                <div className="text-white font-medium">{progress.currentTrack.name}</div>
                <div className="text-spotify-gray">{progress.currentTrack.artist}</div>
                {progress.currentTrack.album && (
                  <div className="text-xs text-spotify-gray">{progress.currentTrack.album}</div>
                )}
                
                <div className="flex items-center space-x-2 mt-2">
                  {progress.currentTrack.matchStatus === 'searching' && (
                    <div className="flex items-center space-x-1 text-yellow-400">
                      <Shuffle className="h-4 w-4 animate-spin" />
                      <span className="text-xs">Searching...</span>
                    </div>
                  )}
                  {progress.currentTrack.matchStatus === 'found' && (
                    <div className="flex items-center space-x-1 text-green-400">
                      <CheckCircle className="h-4 w-4" />
                      <span className="text-xs">Match found!</span>
                    </div>
                  )}
                  {progress.currentTrack.matchStatus === 'not-found' && (
                    <div className="flex items-center space-x-1 text-orange-400">
                      <SkipForward className="h-4 w-4" />
                      <span className="text-xs">No match</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Recently Added */}
        <div className="card bg-white/10 backdrop-blur border-gray-700">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center space-x-2">
            <CheckCircle className="h-5 w-5 text-green-400" />
            <span>Recently Added</span>
          </h3>
          
          <div className="space-y-3">
            {progress.recentlyAdded.length === 0 ? (
              <p className="text-spotify-gray text-sm">No songs added yet...</p>
            ) : (
              progress.recentlyAdded.map((track, index) => (
                <div 
                  key={track.id}
                  className={`flex items-center space-x-3 p-2 rounded-lg transition-all duration-500 ${
                    index === 0 ? 'bg-green-500/20 border border-green-500/30' : 'bg-white/5'
                  }`}
                >
                  <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-blue-500 rounded flex items-center justify-center">
                    <Music className="h-5 w-5 text-white" />
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <div className="text-white text-sm font-medium truncate">{track.name}</div>
                    <div className="text-spotify-gray text-xs truncate">{track.artist}</div>
                  </div>
                  
                  {index === 0 && (
                    <div className="text-green-400 text-xs animate-pulse">New!</div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Migration Complete */}
      {progress.status === 'completed' && (
        <div className="card bg-gradient-to-r from-green-500/20 to-blue-500/20 border-green-500/30">
          <div className="text-center">
            <CheckCircle className="h-16 w-16 text-green-400 mx-auto mb-4" />
            <h3 className="text-2xl font-bold text-white mb-2">Migration Complete! 🎉</h3>
            <p className="text-spotify-gray mb-6">
              Successfully migrated {progress.successfulMatches} out of {progress.totalTracks} tracks
            </p>
            
            {progress.destinationPlaylist && (
              <a
                href={progress.destinationPlaylist.url}
                target="_blank"
                rel="noopener noreferrer"
                className="btn-primary inline-flex items-center space-x-2"
              >
                <ExternalLink className="h-4 w-4" />
                <span>Open Your New Playlist</span>
              </a>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
