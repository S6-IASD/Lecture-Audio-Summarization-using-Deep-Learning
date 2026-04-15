import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { PlusCircle, FileText } from 'lucide-react';
import toast from 'react-hot-toast';
import Sidebar from '@/components/Sidebar';
import SummaryCard from '@/components/SummaryCard';
import LoadingSpinner from '@/components/LoadingSpinner';
import api from '@/api/axios';

export default function Dashboard() {
  const [summaries, setSummaries] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchSummaries = async () => {
      try {
        const response = await api.get('/api/summaries/');
        setSummaries(response.data?.results || response.data || []);
      } catch {
        toast.error('Error loading summaries');
      } finally {
        setIsLoading(false);
      }
    };

    fetchSummaries();
  }, []);

  return (
    <div className="flex min-h-screen bg-[#121212]">
      <Sidebar />
      <main className="flex-1 ml-60 p-8" data-testid="main-dashboard">
        <div className="max-w-5xl mx-auto">
          {/* Header */}
          <div className="flex items-center justify-between mb-8 animate-fade-in-up">
            <div>
              <h1 className="text-white text-3xl font-bold">Dashboard</h1>
              <p className="text-[#B3B3B3] text-sm mt-1">
                {summaries.length} total summary{summaries.length !== 1 ? 's' : ''}
              </p>
            </div>
            <Link
              to="/create"
              className="flex items-center gap-2 px-5 py-2.5 bg-[#1DB954] text-black font-bold text-sm rounded-full hover:bg-[#1aa34a] transition-all hover:scale-105 active:scale-95"
              data-testid="button-create"
            >
              <PlusCircle className="w-4 h-4" />
              New Summary
            </Link>
          </div>

          {/* Content */}
          {isLoading ? (
            <div className="flex items-center justify-center h-64">
              <LoadingSpinner size="lg" />
            </div>
          ) : summaries.length === 0 ? (
            /* Empty state */
            <div className="flex flex-col items-center justify-center h-64 text-center animate-fade-in-up" data-testid="empty-state">
              <div className="w-20 h-20 rounded-full bg-[#1A1A1A] flex items-center justify-center mb-5">
                <FileText className="w-9 h-9 text-[#535353]" />
              </div>
              <h2 className="text-white text-xl font-bold mb-2">No summaries yet</h2>
              <p className="text-[#B3B3B3] text-sm mb-6 max-w-sm">
                Start by creating your first summary. Upload an audio recording.
              </p>
              <Link
                to="/create"
                className="flex items-center gap-2 px-6 py-3 bg-[#1DB954] text-black font-bold text-sm rounded-full hover:bg-[#1aa34a] transition-all hover:scale-105"
                data-testid="button-create-first"
              >
                <PlusCircle className="w-4 h-4" />
                Create my first summary
              </Link>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4" data-testid="summaries-grid">
              {summaries.map((summary, index) => (
                <div key={summary.id} style={{ animationDelay: `${index * 50}ms` }}>
                  <SummaryCard
                    id={summary.id}
                    title={summary.original_filename}
                    created_at={summary.created_at}
                    content={summary.summary_text}
                  />
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
