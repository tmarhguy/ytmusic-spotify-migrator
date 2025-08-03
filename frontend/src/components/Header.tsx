import React from 'react';
import { Music, Github } from 'lucide-react';

export const Header: React.FC = () => {
  return (
    <header className="bg-spotify-black border-b border-gray-800">
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="bg-spotify-green p-2 rounded-lg">
              <Music className="h-8 w-8 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">
                YT2Spot
              </h1>
              <p className="text-spotify-gray text-sm">
                YouTube Music → Spotify Migrator
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <a
              href="https://github.com/tmarhguy/ytmusic-spotify-migrator"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center space-x-2 text-spotify-gray hover:text-white transition-colors"
            >
              <Github className="h-5 w-5" />
              <span className="hidden sm:inline">GitHub</span>
            </a>
          </div>
        </div>
      </div>
    </header>
  );
};
