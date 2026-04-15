import { useState, useRef, useCallback } from 'react';
import { Upload, File, X } from 'lucide-react';

export default function FileUploadZone({ onFileSelect, selectedFile, onClear }) {
  const [isDragging, setIsDragging] = useState(false);
  const inputRef = useRef(null);

  const handleDragEnter = useCallback((e) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback(
    (e) => {
      e.preventDefault();
      setIsDragging(false);
      const files = Array.from(e.dataTransfer.files);
      if (files[0]) {
        onFileSelect(files[0]);
      }
    },
    [onFileSelect]
  );

  const handleClick = () => {
    inputRef.current?.click();
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      onFileSelect(file);
    }
  };

  if (selectedFile) {
    return (
      <div className="border-2 border-[#1DB954]/40 rounded-lg p-6 bg-[#1DB954]/5 flex items-center gap-4 animate-fade-in">
        <div className="w-10 h-10 rounded-lg bg-[#1DB954]/20 flex items-center justify-center flex-shrink-0">
          <File className="w-5 h-5 text-[#1DB954]" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-white text-sm font-medium truncate">{selectedFile.name}</p>
          <p className="text-[#B3B3B3] text-xs mt-0.5">
            {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
          </p>
        </div>
        <button
          onClick={onClear}
          className="w-8 h-8 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center transition-colors"
          data-testid="button-clear-file"
        >
          <X className="w-4 h-4 text-[#B3B3B3]" />
        </button>
      </div>
    );
  }

  return (
    <div
      onDragEnter={handleDragEnter}
      onDragOver={handleDragEnter}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      onClick={handleClick}
      className={`
        border-2 border-dashed rounded-xl p-12 flex flex-col items-center justify-center cursor-pointer transition-all duration-200
        ${isDragging
          ? 'border-[#1DB954] bg-[#1DB954]/10'
          : 'border-white/20 hover:border-[#1DB954]/60 hover:bg-[#1DB954]/5'
        }
      `}
      data-testid="file-upload-zone"
    >
      <div className={`w-16 h-16 rounded-full flex items-center justify-center mb-4 transition-colors ${isDragging ? 'bg-[#1DB954]/20' : 'bg-white/5'}`}>
        <Upload className={`w-7 h-7 transition-colors ${isDragging ? 'text-[#1DB954]' : 'text-[#B3B3B3]'}`} />
      </div>
      <p className="text-white font-semibold text-sm mb-1">
        {isDragging ? 'Drop file here' : 'Drag and drop your file'}
      </p>
      <p className="text-[#B3B3B3] text-xs">
        or click to browse files
      </p>
      <p className="text-[#535353] text-xs mt-2">Supported: MP3, WAV, M4A, OGG</p>
      <input
        ref={inputRef}
        type="file"
        accept=".mp3,.wav,.m4a,.ogg,audio/*"
        onChange={handleFileChange}
        className="hidden"
        data-testid="input-file"
      />
    </div>
  );
}
