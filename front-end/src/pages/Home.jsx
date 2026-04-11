import { Link } from 'react-router-dom';
import {
  Sparkles,
  FileText,
  Zap,
  Shield,
  Download,
  ChevronRight,
  CheckCircle2,
  ArrowRight,
} from 'lucide-react';

const team = [
  { name: 'Kamal Bousebbat', role: 'IASD student' },
  { name: 'Salma El Angui', role: 'IASD student' },
  { name: 'Othmane Boulaarab', role: 'IASD student' },
  { name: 'Khadija El Boudhiri', role: 'IASD student' },
];

const steps = [
  { number: '01', title: 'Create an account', description: 'Free sign up in seconds.' },
  { number: '02', title: 'Upload your audio', description: 'Drag and drop your audio file (MP3, WAV...).' },
  { number: '03', title: 'Get transcript and summary', description: "The AI transcribes and generates the summary instantly." },
];

const perks = [
  'Unlimited audio summaries',
  'Full transcription',
  'Voice generation (TTS)',
  'Secure processing',
  'Complete history',
  'Text format export',
];

export default function Home() {
  return (
    <div className="min-h-screen bg-[#121212] text-white overflow-x-hidden">
      {/* Navbar */}
      <nav className="fixed top-0 left-0 right-0 z-50 px-8 py-4 flex items-center justify-between bg-[#121212]/80 backdrop-blur-md border-b border-white/5">
        <Link to="/" className="flex items-center gap-2.5 group">
          <div className="w-8 h-8 bg-[#1DB954] rounded-full flex items-center justify-center group-hover:shadow-lg group-hover:shadow-[#1DB954]/30 transition-shadow">
            <Sparkles className="w-4 h-4 text-black" />
          </div>
          <span className="text-white font-bold text-lg tracking-tight">SummarizR</span>
        </Link>
        <div className="flex items-center gap-3">
          <Link
            to="/login"
            className="text-[#B3B3B3] hover:text-white text-sm font-medium transition-colors px-4 py-2"
            data-testid="link-login-nav"
          >
            Sign in
          </Link>
          <Link
            to="/register"
            className="bg-[#1DB954] text-black text-sm font-bold px-5 py-2.5 rounded-full hover:bg-[#1aa34a] transition-all hover:scale-105 active:scale-95"
            data-testid="link-register-nav"
          >
            Start for free
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative pt-40 pb-28 px-6 text-center overflow-hidden">
        {/* Glow background */}
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[700px] bg-[#1DB954]/[0.08] rounded-full blur-3xl" />
          <div className="absolute top-1/3 left-1/3 w-[400px] h-[400px] bg-[#1DB954]/5 rounded-full blur-3xl" />
        </div>

        <div className="relative max-w-4xl mx-auto animate-fade-in-up">
          {/* Badge */}
          

          <h1 className="text-5xl sm:text-6xl lg:text-7xl font-black tracking-tight leading-none mb-6">
            Summarize your
            <br />
            <span className="text-[#1DB954]">audio files</span> in
            <br />
            seconds
          </h1>

          <p className="text-[#B3B3B3] text-lg sm:text-xl max-w-2xl mx-auto leading-relaxed mb-10">
            Upload any audio recording and automatically get the transcription, a clear summary, and even a voice synthesis.
          </p>

          <div className="flex items-center justify-center gap-4 flex-wrap">
            <Link
              to="/register"
              className="flex items-center gap-2 bg-[#1DB954] text-black font-bold text-base px-8 py-4 rounded-full hover:bg-[#1aa34a] transition-all hover:scale-105 active:scale-95 shadow-lg shadow-[#1DB954]/20"
              data-testid="button-hero-cta"
            >
              Start for free
              <ArrowRight className="w-5 h-5" />
            </Link>
            <Link
              to="/login"
              className="flex items-center gap-2 bg-white/10 text-white font-semibold text-base px-8 py-4 rounded-full hover:bg-white/15 transition-all border border-white/10"
              data-testid="button-hero-login"
            >
              I already have an account
            </Link>
          </div>

          {/* Social proof */}
          <div className="mt-10 flex items-center justify-center gap-6 text-sm text-[#535353]">
            {perks.slice(0, 3).map((perk) => (
              <div key={perk} className="flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-[#1DB954]" />
                <span>{perk}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="py-24 px-6 bg-[#0a0a0a]">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-16">
            <p className="text-[#1DB954] text-sm font-semibold uppercase tracking-widest mb-3">How it works</p>
            <h2 className="text-4xl font-black">Simple as that</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {steps.map((step, i) => (
              <div key={step.number} className="relative">
                {i < steps.length - 1 && (
                  <div
                    className="hidden md:block absolute top-8 left-full h-px bg-gradient-to-r from-[#1DB954]/40 to-transparent -translate-y-1/2 z-0"
                    style={{ width: 'calc(100% - 2rem)' }}
                  />
                )}
                <div className="relative bg-[#1A1A1A] rounded-2xl p-8 border border-white/5 hover:border-[#1DB954]/20 transition-all hover:-translate-y-1 duration-300">
                  <div className="text-[#1DB954] font-black text-4xl mb-4 opacity-40">{step.number}</div>
                  <h3 className="text-white font-bold text-lg mb-2">{step.title}</h3>
                  <p className="text-[#B3B3B3] text-sm leading-relaxed">{step.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Team */}
      <section className="py-24 px-6 relative">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-16">
            <p className="text-[#1DB954] text-sm font-semibold uppercase tracking-widest mb-3">Our Team</p>
            <h2 className="text-4xl font-black">Project Creators</h2>
            <p className="text-[#B3B3B3] text-base mt-3 max-w-xl mx-auto">
              This project was built by a team passionate about artificial intelligence and audio.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {team.map((member) => (
              <div
                key={member.name}
                className="bg-[#1A1A1A] rounded-2xl p-8 border border-white/5 hover:border-[#1DB954]/20 hover:bg-[#1A1A1A]/80 transition-all group hover:-translate-y-1 duration-300 flex flex-col items-center text-center"
              >
                <div className="w-20 h-20 rounded-full bg-[#1DB954]/10 flex items-center justify-center mb-5 shadow-lg shadow-[#1DB954]/5 group-hover:shadow-[#1DB954]/20 transition-all">
                  <span className="text-[#1DB954] text-2xl font-bold">
                    {member.name.charAt(0)}
                  </span>
                </div>
                <h3 className="text-white font-bold text-lg mb-1">{member.name}</h3>
                <p className="text-[#B3B3B3] text-xs uppercase tracking-wider">{member.role}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Perks list */}
      <section className="py-24 px-6 bg-[#0a0a0a]">
        <div className="max-w-5xl mx-auto">
          <div className="bg-[#1A1A1A] rounded-3xl p-10 border border-white/5 relative overflow-hidden">
            {/* Decorative glow */}
            <div className="absolute -top-20 -right-20 w-64 h-64 bg-[#1DB954]/10 rounded-full blur-3xl pointer-events-none" />
            <div className="relative grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
              <div>
                <p className="text-[#1DB954] text-sm font-semibold uppercase tracking-widest mb-3">All inclusive</p>
                <h2 className="text-4xl font-black mb-4 leading-tight">
                  A complete experience,<br /> from day one
                </h2>
                <p className="text-[#B3B3B3] text-base leading-relaxed mb-8">
                  No hidden features, no surprises. Everything you need is available from sign up.
                </p>
                <Link
                  to="/register"
                  className="inline-flex items-center gap-2 bg-[#1DB954] text-black font-bold px-7 py-3.5 rounded-full hover:bg-[#1aa34a] transition-all hover:scale-105 active:scale-95"
                  data-testid="button-perks-cta"
                >
                  Create my account
                  <ChevronRight className="w-4 h-4" />
                </Link>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {perks.map((perk) => (
                  <div key={perk} className="flex items-center gap-3 py-2">
                    <CheckCircle2 className="w-5 h-5 text-[#1DB954] flex-shrink-0" />
                    <span className="text-white text-sm font-medium">{perk}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Banner */}
      <section className="py-24 px-6">
        <div className="max-w-3xl mx-auto text-center">
          <div className="w-16 h-16 bg-[#1DB954] rounded-full flex items-center justify-center mx-auto mb-6 animate-pulse-glow">
            <Sparkles className="w-8 h-8 text-black" />
          </div>
          <h2 className="text-4xl sm:text-5xl font-black mb-4 leading-tight">
            Ready to save time?
          </h2>
          <p className="text-[#B3B3B3] text-lg mb-8">
            Join users who transcribe their audios in seconds.
          </p>
          <Link
            to="/register"
            className="inline-flex items-center gap-2 bg-[#1DB954] text-black font-bold text-lg px-10 py-4 rounded-full hover:bg-[#1aa34a] transition-all hover:scale-105 active:scale-95 shadow-lg shadow-[#1DB954]/20"
            data-testid="button-final-cta"
          >
            Start for free
            <ArrowRight className="w-5 h-5" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-6 border-t border-white/5">
        <div className="max-w-5xl mx-auto flex items-center justify-between flex-wrap gap-4">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-[#1DB954] rounded-full flex items-center justify-center">
              <Sparkles className="w-3 h-3 text-black" />
            </div>
            <span className="text-[#B3B3B3] text-sm font-semibold">SummarizR</span>
          </div>
          <p className="text-[#535353] text-xs">
            © {new Date().getFullYear()} SummarizR. All rights reserved.
          </p>
          <div className="flex items-center gap-5 text-[#535353] text-xs">
            <Link to="/login" className="hover:text-white transition-colors">Sign In</Link>
            <Link to="/register" className="hover:text-white transition-colors">Sign Up</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
