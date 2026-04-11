import { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import { Mail, User as UserIcon, CalendarDays } from 'lucide-react';
import Sidebar from '@/components/Sidebar';
import LoadingSpinner from '@/components/LoadingSpinner';
import api from '@/api/axios';

function getInitials(username) {
  return username
    .split(/[_\s-]/)
    .map((w) => w[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);
}

export default function Profile() {
  const [profile, setProfile] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await api.get('/api/auth/profile/');
        setProfile(response.data);
      } catch {
        toast.error('Error loading profile');
      } finally {
        setIsLoading(false);
      }
    };

    fetchProfile();
  }, []);

  return (
    <div className="flex min-h-screen bg-[#121212]">
      <Sidebar />
      <main className="flex-1 ml-60 p-8" data-testid="main-profile">
        <div className="max-w-2xl mx-auto animate-fade-in-up">
          <h1 className="text-white text-3xl font-bold mb-8">Profile</h1>

          {isLoading ? (
            <div className="flex items-center justify-center h-64">
              <LoadingSpinner size="lg" />
            </div>
          ) : profile ? (
            <div className="space-y-5">
              {/* Avatar card */}
              <div className="bg-[#1A1A1A] rounded-2xl p-8 border border-white/5 flex items-center gap-6">
                <div
                  className="w-20 h-20 rounded-full bg-[#1DB954] flex items-center justify-center flex-shrink-0 shadow-lg shadow-[#1DB954]/20"
                  data-testid="avatar"
                >
                  <span className="text-black font-bold text-2xl">
                    {getInitials(profile.username)}
                  </span>
                </div>
                <div>
                  <h2 className="text-white text-2xl font-bold" data-testid="text-username">
                    {profile.username}
                  </h2>
                  <p className="text-[#B3B3B3] text-sm mt-1" data-testid="text-email">
                    {profile.email}
                  </p>
                </div>
              </div>

              {/* Details */}
              <div className="bg-[#1A1A1A] rounded-2xl border border-white/5 divide-y divide-white/5">
                <div className="flex items-center gap-4 p-5">
                  <div className="w-10 h-10 rounded-lg bg-white/5 flex items-center justify-center flex-shrink-0">
                    <UserIcon className="w-5 h-5 text-[#B3B3B3]" />
                  </div>
                  <div>
                    <p className="text-[#535353] text-xs uppercase tracking-wider mb-1">Username</p>
                    <p className="text-white font-medium text-sm" data-testid="detail-username">
                      {profile.username}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-4 p-5">
                  <div className="w-10 h-10 rounded-lg bg-white/5 flex items-center justify-center flex-shrink-0">
                    <Mail className="w-5 h-5 text-[#B3B3B3]" />
                  </div>
                  <div>
                    <p className="text-[#535353] text-xs uppercase tracking-wider mb-1">Email address</p>
                    <p className="text-white font-medium text-sm" data-testid="detail-email">
                      {profile.email}
                    </p>
                  </div>
                </div>
                {profile.date_joined && (
                  <div className="flex items-center gap-4 p-5">
                    <div className="w-10 h-10 rounded-lg bg-white/5 flex items-center justify-center flex-shrink-0">
                      <CalendarDays className="w-5 h-5 text-[#B3B3B3]" />
                    </div>
                    <div>
                      <p className="text-[#535353] text-xs uppercase tracking-wider mb-1">Member since</p>
                      <p className="text-white font-medium text-sm">
                        {new Date(profile.date_joined).toLocaleDateString('en-US', {
                          day: 'numeric',
                          month: 'long',
                          year: 'numeric',
                        })}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ) : null}
        </div>
      </main>
    </div>
  );
}
