import React, { useState } from 'react';
import { CheckCircle, ExternalLink, AlertTriangle, Loader2, Music } from 'lucide-react';
import { ServiceOption } from './ServiceSelector';

interface AuthenticationProps {
  sourceService: ServiceOption;
  destinationService: ServiceOption;
  onAuthComplete: (authData: AuthenticationData) => void;
}

export interface AuthenticationData {
  sourceAuth: {
    service: string;
    accessToken: string;
    user: {
      id: string;
      name: string;
      imageUrl?: string;
    };
    playlists?: Array<{
      id: string;
      name: string;
      trackCount: number;
      imageUrl?: string;
    }>;
  } | null;
  destinationAuth: {
    service: string;
    accessToken: string;
    user: {
      id: string;
      name: string;
      imageUrl?: string;
    };
  } | null;
}

export const Authentication: React.FC<AuthenticationProps> = ({
  sourceService,
  destinationService,
  onAuthComplete
}) => {
  const [authData, setAuthData] = useState<AuthenticationData>({
    sourceAuth: null,
    destinationAuth: null
  });
  const [authingService, setAuthingService] = useState<string | null>(null);
  const [selectedPlaylist, setSelectedPlaylist] = useState<string | null>(null);

  const handleAuth = async (service: ServiceOption, type: 'source' | 'destination') => {
    setAuthingService(service.id);
    
    try {
      // For file upload, skip OAuth
      if (service.id === 'file-upload') {
        const mockAuth = {
          service: service.id,
          accessToken: 'file-upload-token',
          user: {
            id: 'local-user',
            name: 'Local Files',
            imageUrl: undefined
          }
        };
        
        setAuthData(prev => ({
          ...prev,
          [type === 'source' ? 'sourceAuth' : 'destinationAuth']: mockAuth
        }));
        setAuthingService(null);
        return;
      }

      // Real OAuth flow
      const authWindow = window.open(
        `/api/auth/${service.id}?type=${type}`,
        'auth',
        'width=600,height=700,scrollbars=yes,resizable=yes'
      );

      // Listen for auth completion
      const messageHandler = (event: MessageEvent) => {
        if (event.origin !== window.location.origin) return;
        
        if (event.data.type === 'AUTH_SUCCESS') {
          const authResult = {
            service: service.id,
            accessToken: event.data.accessToken,
            user: event.data.user,
            playlists: event.data.playlists
          };
          
          setAuthData(prev => ({
            ...prev,
            [type === 'source' ? 'sourceAuth' : 'destinationAuth']: authResult
          }));
          
          authWindow?.close();
          setAuthingService(null);
        } else if (event.data.type === 'AUTH_ERROR') {
          console.error('Auth error:', event.data.error);
          setAuthingService(null);
        }
      };

      window.addEventListener('message', messageHandler);
      
      // Cleanup when auth window is closed
      const checkClosed = setInterval(() => {
        if (authWindow?.closed) {
          window.removeEventListener('message', messageHandler);
          clearInterval(checkClosed);
          setAuthingService(null);
        }
      }, 1000);

    } catch (error) {
      console.error('Auth error:', error);
      setAuthingService(null);
    }
  };

  const canProceed = authData.sourceAuth && authData.destinationAuth && 
    (sourceService.id === 'file-upload' || selectedPlaylist);

  const handleProceed = () => {
    if (canProceed) {
      onAuthComplete(authData);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-white mb-4">
          🔐 Connect Your Accounts
        </h2>
        <p className="text-spotify-gray text-lg">
          Secure authentication to access your music libraries
        </p>
      </div>

      {/* Migration Summary */}
      <div className="card bg-white/10 backdrop-blur border-gray-700 mb-8">
        <div className="flex items-center justify-center space-x-8">
          <div className="text-center">
            <div className="flex items-center justify-center mb-3">
              {sourceService.icon}
            </div>
            <div className="text-white font-medium">{sourceService.name}</div>
            <div className="text-xs text-spotify-gray">Source</div>
          </div>
          
          <div className="text-spotify-green">→</div>
          
          <div className="text-center">
            <div className="flex items-center justify-center mb-3">
              {destinationService.icon}
            </div>
            <div className="text-white font-medium">{destinationService.name}</div>
            <div className="text-xs text-spotify-gray">Destination</div>
          </div>
        </div>
      </div>

      {/* Authentication Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        {/* Source Authentication */}
        <div className="card bg-white/10 backdrop-blur border-gray-700">
          <div className="flex items-center space-x-3 mb-4">
            {sourceService.icon}
            <div>
              <h3 className="text-lg font-semibold text-white">{sourceService.name}</h3>
              <p className="text-sm text-spotify-gray">Source Platform</p>
            </div>
          </div>

          {authData.sourceAuth ? (
            <div className="space-y-4">
              <div className="flex items-center space-x-3 p-3 bg-green-500/20 rounded-lg">
                <CheckCircle className="h-5 w-5 text-green-400" />
                <div>
                  <div className="text-white font-medium">{authData.sourceAuth.user.name}</div>
                  <div className="text-xs text-green-300">Connected successfully</div>
                </div>
              </div>

              {/* Playlist Selection for Source */}
              {authData.sourceAuth.playlists && authData.sourceAuth.playlists.length > 0 && (
                <div>
                  <label className="block text-sm font-medium text-spotify-gray mb-2">
                    Select Playlist to Migrate
                  </label>
                  <select
                    value={selectedPlaylist || ''}
                    onChange={(e) => setSelectedPlaylist(e.target.value)}
                    className="w-full p-3 bg-gray-800 border border-gray-600 rounded-lg text-white focus:border-spotify-green focus:outline-none"
                  >
                    <option value="">Choose a playlist...</option>
                    {authData.sourceAuth.playlists.map((playlist) => (
                      <option key={playlist.id} value={playlist.id}>
                        {playlist.name} ({playlist.trackCount} songs)
                      </option>
                    ))}
                  </select>
                </div>
              )}
            </div>
          ) : (
            <div>
              {sourceService.authRequired ? (
                <button
                  onClick={() => handleAuth(sourceService, 'source')}
                  disabled={authingService === sourceService.id}
                  className="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
                >
                  {authingService === sourceService.id ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      <span>Connecting...</span>
                    </>
                  ) : (
                    <>
                      <ExternalLink className="h-4 w-4" />
                      <span>Connect {sourceService.name}</span>
                    </>
                  )}
                </button>
              ) : (
                <div className="p-3 bg-blue-500/20 rounded-lg flex items-center space-x-2">
                  <CheckCircle className="h-5 w-5 text-blue-400" />
                  <span className="text-blue-300">Ready for file upload</span>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Destination Authentication */}
        <div className="card bg-white/10 backdrop-blur border-gray-700">
          <div className="flex items-center space-x-3 mb-4">
            {destinationService.icon}
            <div>
              <h3 className="text-lg font-semibold text-white">{destinationService.name}</h3>
              <p className="text-sm text-spotify-gray">Destination Platform</p>
            </div>
          </div>

          {authData.destinationAuth ? (
            <div className="flex items-center space-x-3 p-3 bg-green-500/20 rounded-lg">
              <CheckCircle className="h-5 w-5 text-green-400" />
              <div>
                <div className="text-white font-medium">{authData.destinationAuth.user.name}</div>
                <div className="text-xs text-green-300">Connected successfully</div>
              </div>
            </div>
          ) : (
            <button
              onClick={() => handleAuth(destinationService, 'destination')}
              disabled={authingService === destinationService.id}
              className="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
              {authingService === destinationService.id ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span>Connecting...</span>
                </>
              ) : (
                <>
                  <ExternalLink className="h-4 w-4" />
                  <span>Connect {destinationService.name}</span>
                </>
              )}
            </button>
          )}
        </div>
      </div>

      {/* Security Notice */}
      <div className="card bg-yellow-500/10 border-yellow-500/30 mb-8">
        <div className="flex items-start space-x-3">
          <AlertTriangle className="h-5 w-5 text-yellow-400 mt-0.5" />
          <div>
            <h4 className="text-yellow-300 font-medium mb-1">Secure Authentication</h4>
            <p className="text-yellow-200 text-sm">
              We use OAuth 2.0 for secure authentication. Your credentials are never stored on our servers.
              You can revoke access at any time from your account settings.
            </p>
          </div>
        </div>
      </div>

      {/* Live Sync Preview */}
      {canProceed && (
        <div className="card bg-gradient-to-r from-spotify-green/20 to-blue-500/20 border-spotify-green/30">
          <h3 className="text-lg font-semibold text-white mb-4">🚀 Ready for Live Migration!</h3>
          <p className="text-spotify-gray mb-4">
            You'll see your {destinationService.name} playlist grow in real-time as songs are matched and added.
          </p>
          
          <div className="flex justify-center">
            <button
              onClick={handleProceed}
              className="btn-primary flex items-center space-x-2"
            >
              <Music className="h-4 w-4" />
              <span>Start Live Migration</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
