import { useState } from 'react';
import { Header } from './components/Header';
import { ServiceSelector } from './components/ServiceSelector';
import { Authentication, AuthenticationData } from './components/Authentication';
import { LiveMigration } from './components/LiveMigration';
import { FileUpload } from './components/FileUpload';
import { MigrationProgress } from './components/MigrationProgress';
import { Results } from './components/Results';
import { InteractiveDecision } from './components/InteractiveDecision';
import { MigrationSession } from './types';

type AppState = 'service-selection' | 'authentication' | 'live-migration' | 'file-upload' | 'progress' | 'decision' | 'results';

function App() {
  const [currentState, setCurrentState] = useState<AppState>('service-selection');
  const [selectedServices, setSelectedServices] = useState<{
    source: any;
    destination: any;
  } | null>(null);
  const [authData, setAuthData] = useState<AuthenticationData | null>(null);
  const [session, setSession] = useState<MigrationSession | null>(null);

  const handleServiceSelection = (source: any, destination: any) => {
    setSelectedServices({ source, destination });
    
    // If source is file upload, go directly to file upload flow
    if (source.id === 'file-upload') {
      setCurrentState('file-upload');
    } else {
      setCurrentState('authentication');
    }
  };

  const handleAuthComplete = (authenticationData: AuthenticationData) => {
    setAuthData(authenticationData);
    setCurrentState('live-migration');
  };

  const handleFileUploadSuccess = (sessionData: MigrationSession) => {
    setSession(sessionData);
    setCurrentState('progress');
  };

  const handleDecisionComplete = () => {
    setCurrentState('progress');
  };

  const handleMigrationComplete = () => {
    setCurrentState('results');
  };

  const resetToStart = () => {
    setCurrentState('service-selection');
    setSelectedServices(null);
    setAuthData(null);
    setSession(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-spotify-black via-gray-900 to-spotify-dark">
      <Header />
      
      <main className="container mx-auto px-4 py-8">
        {currentState === 'service-selection' && (
          <ServiceSelector onSelectionComplete={handleServiceSelection} />
        )}
        
        {currentState === 'authentication' && selectedServices && (
          <Authentication
            sourceService={selectedServices.source}
            destinationService={selectedServices.destination}
            onAuthComplete={handleAuthComplete}
          />
        )}
        
        {currentState === 'live-migration' && authData && (
          <LiveMigration authData={authData} />
        )}
        
        {currentState === 'file-upload' && (
          <FileUpload onSuccess={handleFileUploadSuccess} />
        )}

        {currentState === 'progress' && session && (
          <MigrationProgress
            session={session}
            onInteractionNeeded={() => setCurrentState('decision')}
            onComplete={handleMigrationComplete}
          />
        )}

        {currentState === 'decision' && session && (
          <InteractiveDecision
            session={session}
            onDecisionMade={handleDecisionComplete}
            onComplete={handleMigrationComplete}
          />
        )}

        {currentState === 'results' && session && (
          <Results
            session={session}
            onStartNew={resetToStart}
          />
        )}
      </main>

      {/* Back Button for Non-Initial States */}
      {currentState !== 'service-selection' && (
        <div className="fixed top-20 left-4 z-50">
          <button
            onClick={resetToStart}
            className="bg-white/10 backdrop-blur text-white px-4 py-2 rounded-lg hover:bg-white/20 transition-colors"
          >
            ← Start Over
          </button>
        </div>
      )}

      <footer className="bg-spotify-black text-spotify-gray py-8 mt-16">
        <div className="container mx-auto px-4 text-center">
          <p className="mb-2">🎵 YT2Spot - YouTube Music to Spotify Migrator</p>
          <p className="text-sm">
            Made with love for music lovers |
            <a href="https://github.com/tmarhguy/ytmusic-spotify-migrator"
              className="text-spotify-green hover:underline ml-1">
              View on GitHub
            </a>
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
