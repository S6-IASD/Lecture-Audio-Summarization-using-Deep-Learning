import { Link } from 'react-router-dom';
import { FileText, Download, Calendar, ChevronRight } from 'lucide-react';

function formatDate(dateStr) {
  try {
    return new Date(dateStr).toLocaleDateString('en-US', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
    });
  } catch {
    return dateStr;
  }
}

function getExcerpt(content, length = 120) {
  if (!content) return '';
  if (content.length <= length) return content;
  return content.slice(0, length).trim() + '...';
}

export default function SummaryCard({ id, title, created_at, content = '', excerpt }) {
  const displayExcerpt = excerpt || getExcerpt(content);

  const handleDownload = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    const token = localStorage.getItem('access_token');
    try {
      const response = await fetch(`http://localhost:8000/api/summaries/${id}/download/summary/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!response.ok) throw new Error('Download failed');
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `resume-${id}.txt`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
    } catch {
      // silently fail
    }
  };

  return (
    <Link
      to={`/summaries/${id}`}
      className="block bg-[#1A1A1A] rounded-xl p-5 border border-white/5 hover:bg-[#282828] transition-all duration-200 hover:scale-[1.02] hover:border-white/10 group cursor-pointer animate-fade-in-up"
      data-testid={`card-summary-${id}`}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3 flex-1 min-w-0">
          <div className="w-10 h-10 rounded-lg bg-[#1DB954]/10 flex items-center justify-center flex-shrink-0 mt-0.5">
            <FileText className="w-5 h-5 text-[#1DB954]" />
          </div>
          <div className="flex-1 min-w-0">
            <h3
              className="text-white font-semibold text-sm leading-tight truncate group-hover:text-[#1DB954] transition-colors"
              data-testid={`text-title-${id}`}
            >
              {title}
            </h3>
            <div className="flex items-center gap-1.5 mt-1">
              <Calendar className="w-3 h-3 text-[#535353]" />
              <span className="text-[#535353] text-xs" data-testid={`text-date-${id}`}>
                {formatDate(created_at)}
              </span>
            </div>
            {displayExcerpt && (
              <p
                className="text-[#B3B3B3] text-xs mt-2 leading-relaxed line-clamp-2"
                data-testid={`text-excerpt-${id}`}
              >
                {displayExcerpt}
              </p>
            )}
          </div>
        </div>
        <ChevronRight className="w-4 h-4 text-[#535353] group-hover:text-[#1DB954] transition-colors flex-shrink-0 mt-1" />
      </div>

      <div className="flex items-center gap-2 mt-4 pt-4 border-t border-white/5">
        <span className="flex-1 text-center text-xs font-medium text-[#B3B3B3] group-hover:text-white transition-colors">
          View Summary
        </span>
        <button
          onClick={handleDownload}
          className="flex items-center gap-1 px-3 py-1.5 rounded-full bg-[#1DB954] text-black text-xs font-bold hover:bg-[#1aa34a] transition-colors"
          data-testid={`button-download-${id}`}
        >
          <Download className="w-3 h-3" />
          TXT
        </button>
      </div>
    </Link>
  );
}
