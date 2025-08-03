import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, AlertCircle, CheckCircle } from 'lucide-react';
import { MigrationSession, UploadResponse, MigrationConfig } from '../types';
import { api } from '../utils/api';

interface FileUploadProps {
  onSuccess: (session: MigrationSession) => void;
}

export const FileUpload: React.FC<FileUploadProps> = ({ onSuccess }) => {
  const [uploadedFile, setUploadedFile] = useState<UploadResponse | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isStarting, setIsStarting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [config, setConfig] = useState<MigrationConfig>({
    hard_threshold: 0.87,
    reject_threshold: 0.60,
    max_candidates: 5,
    dry_run: false
  });

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    setIsUploading(true);
    setError(null);

    try {
      const response = await api.uploadFile(file);
      setUploadedFile(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setIsUploading(false);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/plain': ['.txt'],
      'text/csv': ['.csv'],
      'application/json': ['.json']
    },
    maxFiles: 1,
    disabled: isUploading
  });

  const handleStartMigration = async () => {
    if (!uploadedFile) return;

    setIsStarting(true);
    setError(null);

    try {
      // We need to re-upload the file for the migration endpoint
      // In a real app, you'd store the file or pass a file ID
      const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
      const file = fileInput?.files?.[0];

      if (!file) {
        throw new Error('Please re-select your file');
      }

      const startResponse = await api.startMigration(file, config);

      // Poll for initial status
      const status = await api.getMigrationStatus(startResponse.session_id);

      onSuccess(status);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start migration');
    } finally {
      setIsStarting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-white mb-4">
          Migrate Your Music Library
        </h2>
        <p className="text-spotify-gray text-lg">
          Upload your YouTube Music export and we'll find matching songs on Spotify
        </p>
      </div>

      {!uploadedFile ? (
        <div className="card bg-white/10 backdrop-blur border-gray-700">
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-colors
              ${isDragActive
                ? 'border-spotify-green bg-spotify-green/10'
                : 'border-gray-600 hover:border-gray-500'
              }
              ${isUploading ? 'opacity-50 cursor-not-allowed' : ''}
            `}
          >
            <input {...getInputProps()} />

            <div className="flex flex-col items-center space-y-4">
              <div className="bg-spotify-green/20 p-4 rounded-full">
                <Upload className="h-12 w-12 text-spotify-green" />
              </div>

              <div>
                <h3 className="text-xl font-semibold text-white mb-2">
                  {isDragActive ? 'Drop your file here' : 'Upload your music file'}
                </h3>
                <p className="text-spotify-gray">
                  Drag & drop or click to select your YouTube Music export
                </p>
                <p className="text-sm text-spotify-gray mt-2">
                  Supports: .txt, .csv, .json files
                </p>
              </div>
            </div>
          </div>

          {error && (
            <div className="mt-4 p-4 bg-red-500/20 border border-red-500/50 rounded-lg flex items-center space-x-2">
              <AlertCircle className="h-5 w-5 text-red-400" />
              <span className="text-red-200">{error}</span>
            </div>
          )}
        </div>
      ) : (
        <div className="space-y-6">
          {/* File Info */}
          <div className="card bg-white/10 backdrop-blur border-gray-700">
            <div className="flex items-center space-x-4 mb-4">
              <div className="bg-spotify-green/20 p-2 rounded-lg">
                <CheckCircle className="h-6 w-6 text-spotify-green" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white">
                  File Uploaded Successfully
                </h3>
                <p className="text-spotify-gray">{uploadedFile.filename}</p>
              </div>
            </div>

            <div className="bg-gray-800/50 rounded-lg p-4">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-spotify-gray">Total Songs:</span>
                  <span className="text-white ml-2 font-medium">
                    {uploadedFile.total_songs}
                  </span>
                </div>
                <div>
                  <span className="text-spotify-gray">File Type:</span>
                  <span className="text-white ml-2 font-medium">
                    {uploadedFile.filename.split('.').pop()?.toUpperCase()}
                  </span>
                </div>
              </div>
            </div>

            {uploadedFile.songs.length > 0 && (
              <div className="mt-4">
                <h4 className="text-white font-medium mb-2">Preview (first 10 songs):</h4>
                <div className="bg-gray-800/50 rounded-lg p-3 max-h-40 overflow-y-auto">
                  {uploadedFile.songs.map((song, index) => (
                    <div key={index} className="flex items-center space-x-2 py-1">
                      <FileText className="h-4 w-4 text-spotify-gray" />
                      <span className="text-sm text-white">
                        {song.title} - {song.artist}
                      </span>
                    </div>
                  ))}
                  {uploadedFile.preview_truncated && (
                    <p className="text-xs text-spotify-gray mt-2">
                      ... and {uploadedFile.total_songs - uploadedFile.songs.length} more songs
                    </p>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Configuration */}
          <div className="card bg-white/10 backdrop-blur border-gray-700">
            <h3 className="text-lg font-semibold text-white mb-4">Migration Settings</h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-spotify-gray mb-2">
                  Auto-Accept Threshold
                </label>
                <input
                  type="range"
                  min="0.5"
                  max="1"
                  step="0.01"
                  value={config.hard_threshold}
                  onChange={(e) => setConfig(prev => ({ ...prev, hard_threshold: parseFloat(e.target.value) }))}
                  className="w-full"
                />
                <span className="text-xs text-spotify-gray">{(config.hard_threshold * 100).toFixed(0)}% match</span>
              </div>

              <div>
                <label className="block text-sm font-medium text-spotify-gray mb-2">
                  Auto-Reject Threshold
                </label>
                <input
                  type="range"
                  min="0.3"
                  max="0.8"
                  step="0.01"
                  value={config.reject_threshold}
                  onChange={(e) => setConfig(prev => ({ ...prev, reject_threshold: parseFloat(e.target.value) }))}
                  className="w-full"
                />
                <span className="text-xs text-spotify-gray">{(config.reject_threshold * 100).toFixed(0)}% match</span>
              </div>
            </div>

            <div className="mt-4 flex items-center space-x-3">
              <input
                type="checkbox"
                id="dry-run"
                checked={config.dry_run}
                onChange={(e) => setConfig(prev => ({ ...prev, dry_run: e.target.checked }))}
                className="rounded"
              />
              <label htmlFor="dry-run" className="text-sm text-spotify-gray">
                Dry run (don't actually like songs on Spotify)
              </label>
            </div>
          </div>

          {/* Start Migration */}
          <div className="flex justify-center space-x-4">
            <button
              onClick={() => setUploadedFile(null)}
              className="btn-secondary"
            >
              Upload Different File
            </button>
            <button
              onClick={handleStartMigration}
              disabled={isStarting}
              className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isStarting ? 'Starting Migration...' : 'Start Migration'}
            </button>
          </div>

          {error && (
            <div className="p-4 bg-red-500/20 border border-red-500/50 rounded-lg flex items-center space-x-2">
              <AlertCircle className="h-5 w-5 text-red-400" />
              <span className="text-red-200">{error}</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
