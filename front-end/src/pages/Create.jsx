import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { Sparkles } from 'lucide-react';
import Sidebar from '@/components/Sidebar';
import FileUploadZone from '@/components/FileUploadZone';
import LoadingSpinner from '@/components/LoadingSpinner';
import api from '@/api/axios';

export default function Create() {
  const navigate = useNavigate();
  const [selectedFile, setSelectedFile] = useState(null);
  const [summaryLength, setSummaryLength] = useState('150');
  const [mode, setMode] = useState('transcript');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!selectedFile) {
      toast.error('Please upload an audio file');
      return;
    }

    setIsLoading(true);
    try {
      const formData = new FormData();
      formData.append('audio', selectedFile);
      formData.append('mode', mode);
      if (mode !== 'transcript') {
        formData.append('target_words', summaryLength);
      }

      const response = await api.post('/api/summaries/create/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      toast.success('Summary created!');
      navigate(`/summaries/${response.data.id}`);
    } catch {
      toast.error('Error creating summary');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen bg-[#121212]">
      <Sidebar />
      <main className="flex-1 ml-60 p-8" data-testid="main-create">
        <div className="max-w-2xl mx-auto animate-fade-in-up">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-white text-3xl font-bold">Create a summary</h1>
            <p className="text-[#B3B3B3] text-sm mt-1">
              Upload an audio file to generate an intelligent summary
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* File Upload */}
            <div className="bg-[#1A1A1A] rounded-xl p-6 border border-white/5">
              <h2 className="text-white font-semibold text-sm mb-4 flex items-center gap-2">
                <span className="w-5 h-5 rounded-full bg-[#1DB954]/20 flex items-center justify-center text-[#1DB954] text-xs font-bold">1</span>
                Upload a file
              </h2>
              <FileUploadZone
                onFileSelect={setSelectedFile}
                selectedFile={selectedFile}
                onClear={() => setSelectedFile(null)}
              />
            </div>

            {/* Settings */}
            <div className="bg-[#1A1A1A] rounded-xl p-6 border border-white/5 space-y-6">
              <h2 className="text-white font-semibold text-sm flex items-center gap-2">
                <span className="w-5 h-5 rounded-full bg-[#1DB954]/20 flex items-center justify-center text-[#1DB954] text-xs font-bold">2</span>
                Summary Settings
              </h2>
              
              <div>
                <label className="block text-white text-sm font-medium mb-3">Processing Mode</label>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  {[
                    { value: 'transcript', label: 'Transcription Only' },
                    { value: 'resume', label: 'Text Summary' },
                    { value: 'resumeaudio', label: 'Audio Summary' }
                  ].map((option) => (
                    <button
                      key={option.value}
                      type="button"
                      onClick={() => setMode(option.value)}
                      className={`py-3 px-4 rounded-lg text-sm font-medium transition-colors border ${
                        mode === option.value
                          ? 'bg-[#1DB954]/10 border-[#1DB954] text-[#1DB954]'
                          : 'bg-[#282828] border-transparent text-[#B3B3B3] hover:text-white'
                      }`}
                    >
                      {option.label}
                    </button>
                  ))}
                </div>
              </div>

              {mode !== 'transcript' && (
                <div className="pt-4 border-t border-white/5">
                  <label className="block text-white text-sm font-medium mb-3">Summary Length</label>
                  <div className="grid grid-cols-3 gap-3">
                    {[
                      { value: '50', label: 'Short' },
                      { value: '150', label: 'Medium' },
                      { value: '300', label: 'Long' }
                    ].map((option) => (
                      <button
                        key={option.value}
                        type="button"
                        onClick={() => setSummaryLength(option.value)}
                        className={`py-2 px-4 rounded-lg text-sm font-medium transition-colors border ${
                          summaryLength === option.value
                            ? 'bg-[#1DB954]/10 border-[#1DB954] text-[#1DB954]'
                            : 'bg-[#282828] border-transparent text-[#B3B3B3] hover:text-white'
                        }`}
                      >
                        {option.label}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={isLoading || !selectedFile}
              className="w-full flex items-center justify-center gap-3 py-4 bg-[#1DB954] text-black font-bold text-sm rounded-full hover:bg-[#1aa34a] transition-all disabled:opacity-40 disabled:cursor-not-allowed hover:scale-[1.02] active:scale-[0.98]"
              data-testid="button-generate"
            >
              {isLoading ? (
                <>
                  <LoadingSpinner size="sm" />
                  Generating...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  Generate Summary
                </>
              )}
            </button>

            {isLoading && (
              <div className="bg-[#1A1A1A] rounded-xl p-6 border border-[#1DB954]/20 text-center animate-fade-in">
                <LoadingSpinner size="lg" className="mb-3" />
                <p className="text-white font-medium text-sm">Analyzing file...</p>
                <p className="text-[#B3B3B3] text-xs mt-1">
                  This may take a few moments depending on the file size
                </p>
              </div>
            )}
          </form>
        </div>
      </main>
    </div>
  );
}
