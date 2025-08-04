import React, { useState } from 'react';
import { Music, Upload, ArrowRight, Youtube, Headphones, FileText, Database } from 'lucide-react';

export interface ServiceOption {
  id: string;
  name: string;
  icon: React.ReactNode;
  description: string;
  authRequired: boolean;
  supportedFormats?: string[];
}

const services: ServiceOption[] = [
  {
    id: 'youtube-music',
    name: 'YouTube Music',
    icon: <Youtube className="h-8 w-8 text-red-500" />,
    description: 'Import playlists directly from your YouTube Music account',
    authRequired: true
  },
  {
    id: 'spotify',
    name: 'Spotify',
    icon: <Headphones className="h-8 w-8 text-spotify-green" />,
    description: 'Connect to your Spotify account',
    authRequired: true
  },
  {
    id: 'file-upload',
    name: 'File Upload',
    icon: <Upload className="h-8 w-8 text-blue-500" />,
    description: 'Upload exported playlist files',
    authRequired: false,
    supportedFormats: ['CSV', 'JSON', 'TXT', 'M3U']
  },
  {
    id: 'apple-music',
    name: 'Apple Music',
    icon: <Music className="h-8 w-8 text-pink-500" />,
    description: 'Import from Apple Music (coming soon)',
    authRequired: true
  }
];

interface ServiceSelectorProps {
  onSelectionComplete: (source: ServiceOption, destination: ServiceOption) => void;
}

export const ServiceSelector: React.FC<ServiceSelectorProps> = ({ onSelectionComplete }) => {
  const [sourceService, setSourceService] = useState<ServiceOption | null>(null);
  const [destinationService, setDestinationService] = useState<ServiceOption | null>(null);
  const [step, setStep] = useState<'source' | 'destination'>('source');

  const handleServiceSelect = (service: ServiceOption) => {
    if (step === 'source') {
      setSourceService(service);
      setStep('destination');
    } else {
      setDestinationService(service);
    }
  };

  const canProceed = sourceService && destinationService && sourceService.id !== destinationService.id;

  const handleProceed = () => {
    if (canProceed) {
      onSelectionComplete(sourceService!, destinationService!);
    }
  };

  const resetSelection = () => {
    setSourceService(null);
    setDestinationService(null);
    setStep('source');
  };

  return (
    <div className="max-w-6xl mx-auto">
      <div className="text-center mb-12">
        <h1 className="text-5xl font-bold text-white mb-6">
          🎵 YT2Spot Migration Studio
        </h1>
        <p className="text-xl text-spotify-gray mb-8">
          Transfer your music between platforms with live sync and real-time updates
        </p>
        
        {/* Progress Indicator */}
        <div className="flex items-center justify-center space-x-4 mb-8">
          <div className={`flex items-center space-x-2 px-4 py-2 rounded-full ${
            step === 'source' ? 'bg-spotify-green/20 text-spotify-green' : 
            sourceService ? 'bg-green-500/20 text-green-400' : 'bg-gray-700 text-gray-400'
          }`}>
            <Database className="h-4 w-4" />
            <span className="text-sm font-medium">Choose Source</span>
          </div>
          
          <ArrowRight className="h-5 w-5 text-spotify-gray" />
          
          <div className={`flex items-center space-x-2 px-4 py-2 rounded-full ${
            step === 'destination' ? 'bg-spotify-green/20 text-spotify-green' : 
            destinationService ? 'bg-green-500/20 text-green-400' : 'bg-gray-700 text-gray-400'
          }`}>
            <FileText className="h-4 w-4" />
            <span className="text-sm font-medium">Choose Destination</span>
          </div>
        </div>
      </div>

      {/* Selection Summary */}
      {(sourceService || destinationService) && (
        <div className="card bg-white/10 backdrop-blur border-gray-700 mb-8">
          <h3 className="text-lg font-semibold text-white mb-4">Migration Plan</h3>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              {sourceService ? (
                <div className="flex items-center space-x-3 px-4 py-3 bg-gray-800/50 rounded-lg">
                  {sourceService.icon}
                  <div>
                    <div className="text-white font-medium">{sourceService.name}</div>
                    <div className="text-xs text-spotify-gray">Source</div>
                  </div>
                </div>
              ) : (
                <div className="px-4 py-3 bg-gray-800/30 rounded-lg border-2 border-dashed border-gray-600">
                  <div className="text-gray-400">Select source...</div>
                </div>
              )}
            </div>

            <ArrowRight className="h-6 w-6 text-spotify-green" />

            <div className="flex items-center space-x-4">
              {destinationService ? (
                <div className="flex items-center space-x-3 px-4 py-3 bg-gray-800/50 rounded-lg">
                  {destinationService.icon}
                  <div>
                    <div className="text-white font-medium">{destinationService.name}</div>
                    <div className="text-xs text-spotify-gray">Destination</div>
                  </div>
                </div>
              ) : (
                <div className="px-4 py-3 bg-gray-800/30 rounded-lg border-2 border-dashed border-gray-600">
                  <div className="text-gray-400">Select destination...</div>
                </div>
              )}
            </div>
          </div>

          {canProceed && (
            <div className="mt-6 flex justify-center space-x-4">
              <button
                onClick={resetSelection}
                className="btn-secondary"
              >
                Reset Selection
              </button>
              <button
                onClick={handleProceed}
                className="btn-primary flex items-center space-x-2"
              >
                <span>Continue Migration</span>
                <ArrowRight className="h-4 w-4" />
              </button>
            </div>
          )}
        </div>
      )}

      {/* Service Grid */}
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-white mb-2">
          {step === 'source' ? 'Where are your playlists?' : 'Where do you want to migrate them?'}
        </h2>
        <p className="text-spotify-gray mb-6">
          {step === 'source' 
            ? 'Choose your source platform or upload exported files'
            : 'Select your destination platform'
          }
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {services.map((service) => {
            const isSelected = (step === 'source' ? sourceService?.id : destinationService?.id) === service.id;
            const isDisabled = (step === 'destination' && sourceService?.id === service.id) || 
                              (service.id === 'apple-music'); // Coming soon
            
            return (
              <div
                key={service.id}
                onClick={() => !isDisabled && handleServiceSelect(service)}
                className={`card cursor-pointer transition-all duration-200 ${
                  isSelected 
                    ? 'bg-spotify-green/20 border-spotify-green shadow-lg shadow-spotify-green/20' 
                    : isDisabled
                    ? 'bg-gray-800/30 border-gray-600 opacity-50 cursor-not-allowed'
                    : 'bg-white/10 border-gray-700 hover:bg-white/15 hover:border-gray-600'
                }`}
              >
                <div className="flex items-start space-x-4">
                  <div className={`p-3 rounded-lg ${
                    isSelected 
                      ? 'bg-spotify-green/20' 
                      : 'bg-gray-800/50'
                  }`}>
                    {service.icon}
                  </div>
                  
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <h3 className="text-lg font-semibold text-white">{service.name}</h3>
                      {service.authRequired && (
                        <span className="px-2 py-1 bg-blue-500/20 text-blue-300 text-xs rounded-full">
                          Auth Required
                        </span>
                      )}
                      {service.id === 'apple-music' && (
                        <span className="px-2 py-1 bg-yellow-500/20 text-yellow-300 text-xs rounded-full">
                          Coming Soon
                        </span>
                      )}
                    </div>
                    
                    <p className="text-spotify-gray text-sm mb-3">
                      {service.description}
                    </p>
                    
                    {service.supportedFormats && (
                      <div className="flex flex-wrap gap-1">
                        {service.supportedFormats.map((format) => (
                          <span 
                            key={format}
                            className="px-2 py-1 bg-gray-700 text-gray-300 text-xs rounded"
                          >
                            {format}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                  
                  {isSelected && (
                    <div className="text-spotify-green">
                      <ArrowRight className="h-5 w-5" />
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Features Preview */}
      <div className="card bg-white/10 backdrop-blur border-gray-700">
        <h3 className="text-lg font-semibold text-white mb-4">What You'll Experience</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div className="text-center">
            <div className="text-spotify-green font-semibold mb-2">Secure Authentication</div>
            <div className="text-spotify-gray">OAuth login for seamless access</div>
          </div>
          <div className="text-center">
            <div className="text-spotify-green font-semibold mb-2">Live Progress</div>
            <div className="text-spotify-gray">Watch your playlists grow in real-time</div>
          </div>
          <div className="text-center">
            <div className="text-spotify-green font-semibold mb-2">Smart Matching</div>
            <div className="text-spotify-gray">AI-powered song matching with manual review</div>
          </div>
        </div>
      </div>
    </div>
  );
};
