import React, { useEffect, useState } from 'react';
import { Play, CheckCircle, XCircle, Clock, Music, AlertTriangle } from 'lucide-react';
import { MigrationSession } from '../types';
import { api } from '../utils/api';

interface MigrationProgressProps {
  session: MigrationSession;
  onComplete: (session: MigrationSession) => void;
  onInteractionNeeded: (session: MigrationSession) => void;
}

export const MigrationProgress: React.FC<MigrationProgressProps> = ({
  session: initialSession,
  onComplete,
  onInteractionNeeded
}) => {
  const [session, setSession] = useState(initialSession);
  const [isPolling, setIsPolling] = useState(true);

  useEffect(() => {
    let interval: NodeJS.Timeout;

    if (isPolling && (session.status === 'processing' || session.status === 'awaiting_decision')) {
      interval = setInterval(async () => {
        try {
          const updatedSession = await api.getMigrationStatus(session.session_id);
          setSession(updatedSession);

          if (updatedSession.status === 'completed') {
            setIsPolling(false);
            onComplete(updatedSession);
          } else if (updatedSession.status === 'awaiting_decision') {
            setIsPolling(false);
            onInteractionNeeded(updatedSession);
          } else if (updatedSession.status === 'error') {
            setIsPolling(false);
          }
        } catch (error) {
          console.error('Failed to update status:', error);
          setIsPolling(false);
        }
      }, 1000);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [session.session_id, session.status, isPolling, onComplete, onInteractionNeeded]);

  const getStatusIcon = () => {
    switch (session.status) {
      case 'processing':
        return <Play className="h-6 w-6 text-spotify-green animate-pulse" />;
      case 'completed':
        return <CheckCircle className="h-6 w-6 text-green-400" />;
      case 'awaiting_decision':
        return <AlertTriangle className="h-6 w-6 text-yellow-400" />;
      case 'error':
        return <XCircle className="h-6 w-6 text-red-400" />;
      default:
        return <Clock className="h-6 w-6 text-spotify-gray" />;
    }
  };

  const getStatusText = () => {
    switch (session.status) {
      case 'processing':
        return 'Migration in progress...';
      case 'completed':
        return 'Migration completed!';
      case 'awaiting_decision':
        return 'Waiting for your decision';
      case 'error':
        return 'Migration failed';
      default:
        return 'Preparing migration...';
    }
  };

  const progressPercentage = session.total_songs > 0
    ? ((session.processed_songs / session.total_songs) * 100)
    : 0;

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-white mb-4">
          Migration Progress
        </h2>
        <p className="text-spotify-gray text-lg">
          Session ID: {session.session_id}
        </p>
      </div>

      {/* Status Card */}
      <div className="card bg-white/10 backdrop-blur border-gray-700 mb-6">
        <div className="flex items-center space-x-4 mb-6">
          {getStatusIcon()}
          <div>
            <h3 className="text-xl font-semibold text-white">
              {getStatusText()}
            </h3>
            <p className="text-spotify-gray">
              {session.processed_songs} of {session.total_songs} songs processed
            </p>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mb-6">
          <div className="flex justify-between text-sm text-spotify-gray mb-2">
            <span>Progress</span>
            <span>{progressPercentage.toFixed(1)}%</span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-3">
            <div
              className="bg-gradient-to-r from-spotify-green to-green-400 h-3 rounded-full transition-all duration-500 ease-out"
              style={{ width: `${progressPercentage}%` }}
            />
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-gray-800/50 rounded-lg p-4 text-center">
            <div className="flex items-center justify-center mb-2">
              <CheckCircle className="h-5 w-5 text-green-400" />
            </div>
            <div className="text-2xl font-bold text-white">{session.accepted_songs}</div>
            <div className="text-sm text-spotify-gray">Accepted</div>
          </div>

          <div className="bg-gray-800/50 rounded-lg p-4 text-center">
            <div className="flex items-center justify-center mb-2">
              <XCircle className="h-5 w-5 text-red-400" />
            </div>
            <div className="text-2xl font-bold text-white">{session.rejected_songs || 0}</div>
            <div className="text-sm text-spotify-gray">Rejected</div>
          </div>

          <div className="bg-gray-800/50 rounded-lg p-4 text-center">
            <div className="flex items-center justify-center mb-2">
              <AlertTriangle className="h-5 w-5 text-yellow-400" />
            </div>
            <div className="text-2xl font-bold text-white">{session.manual_songs}</div>
            <div className="text-sm text-spotify-gray">Manual Review</div>
          </div>

          <div className="bg-gray-800/50 rounded-lg p-4 text-center">
            <div className="flex items-center justify-center mb-2">
              <Music className="h-5 w-5 text-spotify-green" />
            </div>
            <div className="text-2xl font-bold text-white">{session.total_songs}</div>
            <div className="text-sm text-spotify-gray">Total</div>
          </div>
        </div>
      </div>

      {/* Current Song (if processing) */}
      {session.status === 'processing' && session.current_song && (
        <div className="card bg-white/10 backdrop-blur border-gray-700">
          <div className="flex items-center space-x-4">
            <div className="bg-spotify-green/20 p-3 rounded-full">
              <Music className="h-6 w-6 text-spotify-green" />
            </div>
            <div>
              <h4 className="text-lg font-medium text-white">Currently Processing</h4>
              <p className="text-spotify-gray">
                {session.current_song.title} - {session.current_song.artist}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Recent Activity */}
      {session.recent_activity && session.recent_activity.length > 0 && (
        <div className="card bg-white/10 backdrop-blur border-gray-700">
          <h4 className="text-lg font-medium text-white mb-4">Recent Activity</h4>
          <div className="space-y-3 max-h-60 overflow-y-auto">
            {session.recent_activity.map((activity, index) => (
              <div key={index} className="flex items-center space-x-3 text-sm">
                <div className="flex-shrink-0">
                  {activity.action === 'accepted' && <CheckCircle className="h-4 w-4 text-green-400" />}
                  {activity.action === 'rejected' && <XCircle className="h-4 w-4 text-red-400" />}
                  {activity.action === 'manual' && <AlertTriangle className="h-4 w-4 text-yellow-400" />}
                </div>
                <div className="flex-1">
                  <span className="text-white">{activity.song_title}</span>
                  <span className="text-spotify-gray"> - {activity.artist}</span>
                </div>
                <div className="text-xs text-spotify-gray">
                  {activity.timestamp}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Error Display */}
      {session.status === 'error' && session.error_message && (
        <div className="card bg-red-500/20 border-red-500/50">
          <div className="flex items-center space-x-3">
            <XCircle className="h-6 w-6 text-red-400" />
            <div>
              <h4 className="text-lg font-medium text-red-200">Migration Failed</h4>
              <p className="text-red-300">{session.error_message}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
