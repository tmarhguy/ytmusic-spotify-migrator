import React, { useState } from 'react';
import { CheckCircle, XCircle, Music, Headphones, ExternalLink, AlertTriangle } from 'lucide-react';
import { MigrationSession, SpotifyTrack } from '../types';
import { api } from '../utils/api';

interface InteractiveDecisionProps {
  session: MigrationSession;
  onDecisionMade: (session: MigrationSession) => void;
  onComplete: (session: MigrationSession) => void;
}

export const InteractiveDecision: React.FC<InteractiveDecisionProps> = ({
  session,
  onDecisionMade,
  onComplete
}) => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleDecision = async (decision: 'accept' | 'reject' | 'manual', candidateId?: string) => {
    setIsSubmitting(true);
    setError(null);

    try {
      const response = await api.makeDecision(session.session_id, decision, candidateId);

      if (response.migration_complete) {
        onComplete(response.session);
      } else {
        onDecisionMade(response.session);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit decision');
    } finally {
      setIsSubmitting(false);
    }
  };

  const decision = session.current_decision_needed || session.pending_decision;
  if (!decision) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="card bg-white/10 backdrop-blur border-gray-700">
          <div className="text-center">
            <AlertTriangle className="h-12 w-12 text-yellow-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-white mb-2">
              No Decision Required
            </h3>
            <p className="text-spotify-gray">
              The migration is continuing automatically.
            </p>
          </div>
        </div>
      </div>
    );
  }

  const { song, candidates, match_scores } = decision;

  return (
    <div className="max-w-6xl mx-auto">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-white mb-4">
          Manual Review Required
        </h2>
        <p className="text-spotify-gray text-lg">
          We found multiple potential matches. Please choose the best one:
        </p>
      </div>

      {/* Source Song */}
      <div className="card bg-white/10 backdrop-blur border-gray-700 mb-6">
        <div className="flex items-center space-x-4 mb-4">
          <div className="bg-youtube-red/20 p-3 rounded-full">
            <Music className="h-6 w-6 text-youtube-red" />
          </div>
          <div>
            <h3 className="text-xl font-semibold text-white">Original Song</h3>
            <p className="text-spotify-gray">From your YouTube Music library</p>
          </div>
        </div>

        <div className="bg-gray-800/50 rounded-lg p-4">
          <h4 className="text-lg font-medium text-white mb-2">
            {song.title}
          </h4>
          <p className="text-spotify-gray mb-2">
            by {song.artist}
          </p>
          {song.album && (
            <p className="text-sm text-spotify-gray">
              Album: {song.album}
            </p>
          )}
        </div>
      </div>

      {/* Candidates */}
      <div className="space-y-4 mb-6">
        <h3 className="text-xl font-semibold text-white">
          Spotify Matches ({candidates.length} found)
        </h3>

        {candidates.map((candidate: SpotifyTrack, index: number) => {
          const score = match_scores?.[index] || candidate.match_score || 0;
          const scorePercentage = (score * 100).toFixed(1);

          return (
            <div key={candidate.id || candidate.spotify_id} className="card bg-white/10 backdrop-blur border-gray-700">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-3">
                    <div className="bg-spotify-green/20 p-2 rounded-lg">
                      <Headphones className="h-5 w-5 text-spotify-green" />
                    </div>
                    <div>
                      <h4 className="text-lg font-medium text-white">
                        {candidate.name || candidate.title}
                      </h4>
                      <p className="text-spotify-gray">
                        by {candidate.artists?.map((a: any) => a.name).join(', ') || candidate.artist}
                      </p>
                    </div>
                    <div className="ml-auto">
                      <span className={`px-3 py-1 rounded-full text-sm font-medium ${score >= 0.9 ? 'bg-green-500/20 text-green-300' :
                          score >= 0.8 ? 'bg-yellow-500/20 text-yellow-300' :
                            'bg-red-500/20 text-red-300'
                        }`}>
                        {scorePercentage}% match
                      </span>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                    <div>
                      <span className="text-spotify-gray">Album:</span>
                      <p className="text-white">{candidate.album || 'Unknown'}</p>
                    </div>
                    <div>
                      <span className="text-spotify-gray">Duration:</span>
                      <p className="text-white">
                        {candidate.duration_ms ? 
                          `${Math.floor(candidate.duration_ms / 60000)}:${String(Math.floor((candidate.duration_ms % 60000) / 1000)).padStart(2, '0')}` :
                          'Unknown'
                        }
                      </p>
                    </div>
                    <div>
                      <span className="text-spotify-gray">Popularity:</span>
                      <p className="text-white">{candidate.popularity || 'Unknown'}/100</p>
                    </div>
                  </div>

                  {(candidate.external_urls?.spotify || candidate.external_url) && (
                    <div className="mt-3">
                      <a
                        href={candidate.external_urls?.spotify || candidate.external_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center space-x-2 text-spotify-green hover:text-green-300 transition-colors"
                      >
                        <ExternalLink className="h-4 w-4" />
                        <span>Listen on Spotify</span>
                      </a>
                    </div>
                  )}
                </div>
              </div>

              <div className="mt-4 flex justify-end">
                <button
                  onClick={() => handleDecision('manual', candidate.id || candidate.spotify_id)}
                  disabled={isSubmitting}
                  className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Select This Match
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Action Buttons */}
      <div className="flex justify-center space-x-4">
        <button
          onClick={() => handleDecision('reject')}
          disabled={isSubmitting}
          className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
        >
          <XCircle className="h-5 w-5" />
          <span>Skip This Song</span>
        </button>

        {candidates.length > 0 && (
          <button
            onClick={() => handleDecision('accept')}
            disabled={isSubmitting}
            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            <CheckCircle className="h-5 w-5" />
            <span>Accept Best Match</span>
          </button>
        )}
      </div>

      {error && (
        <div className="mt-6 p-4 bg-red-500/20 border border-red-500/50 rounded-lg flex items-center space-x-2">
          <AlertTriangle className="h-5 w-5 text-red-400" />
          <span className="text-red-200">{error}</span>
        </div>
      )}

      {/* Progress Context */}
      <div className="mt-8 text-center">
        <p className="text-spotify-gray">
          Song {session.processed_songs + 1} of {session.total_songs} •
          {session.accepted_songs} accepted • {session.rejected_songs} rejected
        </p>
      </div>
    </div>
  );
};
