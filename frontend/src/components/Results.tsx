import React from 'react';
import { CheckCircle, XCircle, AlertTriangle, Download, Music, BarChart3 } from 'lucide-react';
import { MigrationSession } from '../types';
import { api } from '../utils/api';

interface ResultsProps {
  session: MigrationSession;
  onStartNew: () => void;
}

export const Results: React.FC<ResultsProps> = ({ session, onStartNew }) => {
  const successRate = session.total_songs > 0
    ? ((session.accepted_songs / session.total_songs) * 100)
    : 0;

  const handleDownloadReport = async () => {
    try {
      const results = await api.getMigrationResults(session.session_id);

      // Create a detailed report
      const report = {
        session_id: session.session_id,
        timestamp: new Date().toISOString(),
        summary: {
          total_songs: session.total_songs,
          accepted_songs: session.accepted_songs,
          rejected_songs: session.rejected_songs,
          manual_songs: session.manual_songs,
          success_rate: successRate.toFixed(1) + '%',
          duration: session.duration || 'Unknown'
        },
        accepted_songs: results.accepted_songs || [],
        rejected_songs: results.rejected_songs || [],
        manual_songs: results.manual_songs || []
      };

      const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `migration-report-${session.session_id}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to download report:', error);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <div className="bg-spotify-green/20 p-6 rounded-full w-24 h-24 mx-auto mb-6 flex items-center justify-center">
          <CheckCircle className="h-12 w-12 text-spotify-green" />
        </div>
        <h2 className="text-3xl font-bold text-white mb-4">
          Migration Complete!
        </h2>
        <p className="text-spotify-gray text-lg">
          Your music library has been successfully migrated to Spotify
        </p>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="card bg-white/10 backdrop-blur border-gray-700">
          <div className="text-center">
            <div className="bg-spotify-green/20 p-3 rounded-lg w-fit mx-auto mb-3">
              <Music className="h-6 w-6 text-spotify-green" />
            </div>
            <div className="text-2xl font-bold text-white">{session.total_songs}</div>
            <div className="text-sm text-spotify-gray">Total Songs</div>
          </div>
        </div>

        <div className="card bg-white/10 backdrop-blur border-gray-700">
          <div className="text-center">
            <div className="bg-green-500/20 p-3 rounded-lg w-fit mx-auto mb-3">
              <CheckCircle className="h-6 w-6 text-green-400" />
            </div>
            <div className="text-2xl font-bold text-white">{session.accepted_songs}</div>
            <div className="text-sm text-spotify-gray">Successfully Migrated</div>
          </div>
        </div>

        <div className="card bg-white/10 backdrop-blur border-gray-700">
          <div className="text-center">
            <div className="bg-yellow-500/20 p-3 rounded-lg w-fit mx-auto mb-3">
              <AlertTriangle className="h-6 w-6 text-yellow-400" />
            </div>
            <div className="text-2xl font-bold text-white">{session.manual_songs}</div>
            <div className="text-sm text-spotify-gray">Manual Selections</div>
          </div>
        </div>

        <div className="card bg-white/10 backdrop-blur border-gray-700">
          <div className="text-center">
            <div className="bg-red-500/20 p-3 rounded-lg w-fit mx-auto mb-3">
              <XCircle className="h-6 w-6 text-red-400" />
            </div>
            <div className="text-2xl font-bold text-white">{session.rejected_songs || 0}</div>
            <div className="text-sm text-spotify-gray">Not Found</div>
          </div>
        </div>
      </div>

      {/* Success Rate */}
      <div className="card bg-white/10 backdrop-blur border-gray-700 mb-8">
        <div className="flex items-center space-x-4 mb-6">
          <div className="bg-spotify-green/20 p-3 rounded-lg">
            <BarChart3 className="h-6 w-6 text-spotify-green" />
          </div>
          <div>
            <h3 className="text-xl font-semibold text-white">Migration Success Rate</h3>
            <p className="text-spotify-gray">Overall performance of the migration</p>
          </div>
        </div>

        <div className="mb-4">
          <div className="flex justify-between text-sm text-spotify-gray mb-2">
            <span>Success Rate</span>
            <span>{successRate.toFixed(1)}%</span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-4">
            <div
              className="bg-gradient-to-r from-spotify-green to-green-400 h-4 rounded-full transition-all duration-1000 ease-out"
              style={{ width: `${successRate}%` }}
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div className="bg-gray-800/50 rounded-lg p-3">
            <span className="text-spotify-gray">Automatic Matches:</span>
            <div className="text-white font-medium">
              {(session.accepted_songs || 0) - (session.manual_songs || 0)} songs
            </div>
          </div>
          <div className="bg-gray-800/50 rounded-lg p-3">
            <span className="text-spotify-gray">Manual Selections:</span>
            <div className="text-white font-medium">{session.manual_songs || 0} songs</div>
          </div>
          <div className="bg-gray-800/50 rounded-lg p-3">
            <span className="text-spotify-gray">Migration Time:</span>
            <div className="text-white font-medium">{session.duration || 'Unknown'}</div>
          </div>
        </div>
      </div>

      {/* Session Details */}
      <div className="card bg-white/10 backdrop-blur border-gray-700 mb-8">
        <h3 className="text-lg font-semibold text-white mb-4">Session Details</h3>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-spotify-gray">Session ID:</span>
            <span className="text-white font-mono">{session.session_id}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-spotify-gray">Started:</span>
            <span className="text-white">{session.created_at || 'Unknown'}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-spotify-gray">Completed:</span>
            <span className="text-white">{session.completed_at || 'Just now'}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-spotify-gray">Configuration:</span>
            <span className="text-white">
              {session.config ?
                `${(session.config.hard_threshold * 100).toFixed(0)}% auto-accept, ${(session.config.reject_threshold * 100).toFixed(0)}% auto-reject` :
                'Default settings'
              }
            </span>
          </div>
        </div>
      </div>

      {/* Next Steps */}
      <div className="card bg-gradient-to-r from-spotify-green/20 to-green-500/20 border-spotify-green/30">
        <h3 className="text-lg font-semibold text-white mb-4">What's Next?</h3>
        <div className="space-y-3 text-sm text-spotify-gray">
          <p>• Check your Spotify library - all migrated songs have been liked for you</p>
          <p>• Consider creating playlists to organize your newly migrated music</p>
          <p>• Download the detailed report below for your records</p>
          <p>• Share this tool with friends who want to migrate their music too!</p>
        </div>
      </div>

      {/* Actions */}
      <div className="flex flex-col sm:flex-row justify-center space-y-4 sm:space-y-0 sm:space-x-4 mt-8">
        <button
          onClick={handleDownloadReport}
          className="btn-secondary flex items-center justify-center space-x-2"
        >
          <Download className="h-5 w-5" />
          <span>Download Detailed Report</span>
        </button>

        <button
          onClick={onStartNew}
          className="btn-primary flex items-center justify-center space-x-2"
        >
          <Music className="h-5 w-5" />
          <span>Migrate Another Library</span>
        </button>
      </div>

      <div className="text-center mt-8">
        <p className="text-sm text-spotify-gray">
          Made with ❤️ by YT2Spot Migration Tool
        </p>
      </div>
    </div>
  );
};
