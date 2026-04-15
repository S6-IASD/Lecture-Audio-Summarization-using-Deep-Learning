import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Download, Calendar, FileText } from 'lucide-react';
import toast from 'react-hot-toast';
import Sidebar from '@/components/Sidebar';
import LoadingSpinner from '@/components/LoadingSpinner';
import api from '@/api/axios';

function formatDate(dateStr) {
  try {
    return new Date(dateStr).toLocaleDateString('en-US', {
      weekday: 'long',
      day: 'numeric',
      month: 'long',
      year: 'numeric',
    });
  } catch {
    return dateStr;
  }
}

const downloadFormats = [
  { format: 'summary', ext: 'txt', label: 'TXT', color: 'bg-red-600 hover:bg-red-700' },
  { format: 'transcript', ext: 'txt', label: 'TRANSCRIPT', color: 'bg-blue-600 hover:bg-blue-700' },
  { format: 'audio', ext: 'wav', label: 'AUDIO', color: 'bg-[#1DB954] hover:bg-[#1aa34a]' },
];

export default function SummaryDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [summary, setSummary] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [audioUrl, setAudioUrl] = useState(null);

  useEffect(() => {
    let activeUrl = null;
    const fetchAudio = async () => {
      if (!summary?.audio_file) return;
      const token = localStorage.getItem('access_token');
      const url = `http://localhost:8000/api/summaries/${summary.id}/download/audio/`;
      try {
        const response = await fetch(url, { headers: { Authorization: `Bearer ${token}` } });
        if (response.ok) {
          const blob = await response.blob();
          activeUrl = URL.createObjectURL(blob);
          setAudioUrl(activeUrl);
        }
      } catch (err) {
        console.error("Failed to load audio for player", err);
      }
    };
    
    if (summary?.audio_file) {
      fetchAudio();
    }

    return () => {
      if (activeUrl) {
        URL.revokeObjectURL(activeUrl);
      }
    };
  }, [summary]);

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const response = await api.get(`/api/summaries/${id}/`);
        setSummary(response.data);
      } catch {
        toast.error('Summary not found');
        navigate('/dashboard');
      } finally {
        setIsLoading(false);
      }
    };

    fetchSummary();
  }, [id, navigate]);

  const handleDownload = async (formatDef) => {
    const token = localStorage.getItem('access_token');
    const url = `http://localhost:8000/api/summaries/${id}/download/${formatDef.format}/`;

    try {
      const response = await fetch(url, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!response.ok) {
        if (response.status === 404 && formatDef.format === 'audio') {
          throw new Error("This summary does not include audio");
        }
        throw new Error('Download error');
      }

      const blob = await response.blob();
      const objectUrl = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = objectUrl;
      link.download = `resume-${id}-${formatDef.format}.${formatDef.ext}`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(objectUrl);
      toast.success(`Downloading ${formatDef.label} started`);
    } catch (err) {
      if (err.message === "This summary does not include audio") {
        toast.error(err.message);
      } else {
        toast.error(`Error downloading ${formatDef.label}`);
      }
    }
  };

  if (isLoading) {
    return (
      <div className="flex min-h-screen bg-[#121212]">
        <Sidebar />
        <main className="flex-1 ml-60 p-8 flex items-center justify-center">
          <LoadingSpinner size="lg" />
        </main>
      </div>
    );
  }

  if (!summary) return null;

  return (
    <div className="flex min-h-screen bg-[#121212]">
      <Sidebar />
      <main className="flex-1 ml-60 p-8" data-testid="main-detail">
        <div className="max-w-3xl mx-auto animate-fade-in-up">
          {/* Back */}
          <button
            onClick={() => navigate('/dashboard')}
            className="flex items-center gap-2 text-[#B3B3B3] hover:text-white transition-colors mb-6 group"
            data-testid="button-back"
          >
            <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
            <span className="text-sm">Back to dashboard</span>
          </button>

          {/* Header */}
          <div className="bg-[#1A1A1A] rounded-xl p-8 border border-white/5 mb-6">
            <div className="flex items-start gap-4 mb-5">
              <div className="w-12 h-12 rounded-xl bg-[#1DB954]/10 flex items-center justify-center flex-shrink-0">
                <FileText className="w-6 h-6 text-[#1DB954]" />
              </div>
              <div>
                <h1 className="text-white text-2xl font-bold" data-testid="text-title">
                  {summary.original_filename}
                </h1>
                <div className="flex items-center gap-2 mt-2">
                  <Calendar className="w-4 h-4 text-[#535353]" />
                  <span className="text-[#B3B3B3] text-sm" data-testid="text-date">
                    {formatDate(summary.created_at)}
                  </span>
                </div>
              </div>
            </div>

            {/* Downloads */}
            <div className="border-t border-white/5 pt-5">
              <p className="text-[#B3B3B3] text-xs font-medium mb-3 uppercase tracking-wider">
                Download summary
              </p>
              <div className="flex gap-3">
                {downloadFormats.map((formatDef) => {
                  if (formatDef.format === 'summary' && !summary.summary_file) return null;
                  if (formatDef.format === 'transcript' && !summary.transcript_file) return null;
                  if (formatDef.format === 'audio' && !summary.audio_file) return null;

                  return (
                    <button
                      key={formatDef.format}
                      onClick={() => handleDownload(formatDef)}
                      className={`flex items-center gap-2 px-4 py-2 rounded-full text-white text-xs font-bold transition-all hover:scale-105 active:scale-95 ${formatDef.color}`}
                      data-testid={`button-download-${formatDef.format}`}
                    >
                      <Download className="w-3.5 h-3.5" />
                      {formatDef.label}
                    </button>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Content */}
          <div className="space-y-6">
            
            {/* AUDIO PLAYER */}
            {summary.audio_file && (
              <div className="bg-[#1A1A1A] rounded-xl p-8 border border-white/5">
                <h2 className="text-[#1DB954] font-semibold text-sm mb-5 uppercase tracking-wider">
                  Audio Summary
                </h2>
                {audioUrl ? (
                  <audio controls className="w-full h-12" src={audioUrl}>
                    Your browser does not support the audio element.
                  </audio>
                ) : (
                  <div className="flex items-center gap-3 text-[#B3B3B3] text-sm">
                    <LoadingSpinner size="sm" />
                    Loading audio playback...
                  </div>
                )}
              </div>
            )}

            {/* SUMMARY TEXT */}
            {summary.summary_text && (
              <div className="bg-[#1A1A1A] rounded-xl p-8 border border-white/5">
                <h2 className="text-[#B3B3B3] font-semibold text-sm mb-5 uppercase tracking-wider">
                  Summary
                </h2>
                <div className="text-white text-base leading-relaxed whitespace-pre-wrap font-medium">
                  {summary.summary_text}
                </div>
              </div>
            )}

            {/* TRANSCRIPT */}
            {summary.transcript && (
              <div className="bg-[#1A1A1A] rounded-xl p-8 border border-white/5">
                <h2 className="text-[#B3B3B3] font-semibold text-sm mb-5 uppercase tracking-wider">
                  {summary.summary_text ? "Full Transcription" : "Transcription Content"}
                </h2>
                <div className="text-[#B3B3B3] text-sm leading-relaxed whitespace-pre-wrap">
                  {summary.transcript}
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
