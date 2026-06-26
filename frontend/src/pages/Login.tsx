import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from 'primereact/card';
import { InputText } from 'primereact/inputtext';
import { Password } from 'primereact/password';
import { Button } from 'primereact/button';
import { Toast } from 'primereact/toast';
import { Microscope, User, Lock, Mail, UserPlus, ArrowRight } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const inputClass = '!w-full !pl-10 !bg-slate-900/60 !border !border-white/10 !rounded-xl !text-slate-100 !text-sm !py-2.5 placeholder:!text-slate-600 focus:!border-blue-400/50 focus:!shadow-[0_0_0_3px_rgba(59,130,246,0.15)] focus:!bg-slate-900/80 !transition-all !outline-none';

export default function Login() {
  const [isRegister, setIsRegister] = useState(false);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [fullName, setFullName] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [particles, setParticles] = useState<{ id: number; x: number; y: number; size: number; delay: number; duration: number }[]>([]);
  const { login, register } = useAuth();
  const navigate = useNavigate();
  const toastRef = useRef<Toast>(null);

  // Generate floating particles on mount
  useEffect(() => {
    const generated = Array.from({ length: 15 }, (_, i) => ({
      id: i,
      x: Math.random() * 100,
      y: Math.random() * 100,
      size: 2 + Math.random() * 4,
      delay: Math.random() * 8,
      duration: 12 + Math.random() * 18,
    }));
    setParticles(generated);
  }, []);

  const handleSubmit = async () => {
    setError('');
    if (!username.trim() || !password.trim()) {
      setError('Username and password are required');
      return;
    }
    if (isRegister && (!email.trim() || !fullName.trim())) {
      setError('All fields are required for registration');
      return;
    }

    setLoading(true);
    try {
      if (isRegister) {
        await register({ username: username.trim(), email: email.trim(), password, full_name: fullName.trim() });
        toastRef.current?.show({ severity: 'success', summary: 'Registered & Logged In', life: 3000 });
      } else {
        await login({ username: username.trim(), password });
        toastRef.current?.show({ severity: 'success', summary: 'Welcome back!', life: 3000 });
      }
    } catch (err: any) {
      const msg = err?.response?.data?.detail || 'Something went wrong';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen flex items-center justify-center p-6 overflow-hidden bg-[length:200%_200%]"
      style={{ background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%)' }}
    >
      {/* Animated floating particles */}
      <div className="absolute inset-0 pointer-events-none z-[1]" aria-hidden="true">
        {particles.map((p) => (
          <div
            key={p.id}
            className="login-particle"
            style={{
              left: `${p.x}%`,
              top: `${p.y}%`,
              width: p.size,
              height: p.size,
              animationDelay: `${p.delay}s`,
              animationDuration: `${p.duration}s`,
            }}
          />
        ))}
      </div>

      {/* Background gradient blobs */}
      <div className="absolute w-[600px] h-[600px] rounded-full blur-[120px] pointer-events-none z-0 login-blob-1"
        style={{ top: '-200px', right: '-150px', background: 'rgba(59, 130, 246, 0.15)' }}
      />
      <div className="absolute w-[500px] h-[500px] rounded-full blur-[120px] pointer-events-none z-0 login-blob-2"
        style={{ bottom: '-150px', left: '-150px', background: 'rgba(16, 185, 129, 0.1)' }}
      />
      <div className="absolute w-[400px] h-[400px] rounded-full blur-[120px] pointer-events-none z-0 login-blob-3"
        style={{ top: '50%', left: '50%', transform: 'translate(-50%, -50%)', background: 'rgba(139, 92, 246, 0.1)' }}
      />

      <Toast ref={toastRef} position="top-right" />

      <div className="relative z-[2] w-full max-w-sm flex flex-col items-center">
        {/* Brand Section */}
        <div className="text-center mb-8">
          <div className="relative inline-flex items-center justify-center mb-4">
            <div className="login-glow absolute w-20 h-20 rounded-full" />
            <div className="login-icon-float relative w-16 h-16 rounded-[18px] bg-gradient-to-br from-blue-500 to-blue-400 flex items-center justify-center text-white shadow-[0_8px_32px_rgba(37,99,235,0.35)]">
              <Microscope size={32} />
            </div>
          </div>
          <h1 className="text-[1.75rem] font-bold text-slate-100 tracking-tight m-0">HematoScan</h1>
          <p className="text-sm text-slate-400 mt-1">Blood Cancer Detection System</p>
        </div>

        {/* Card */}
        <Card className="w-full !border !border-white/10 !rounded-[1.25rem] !bg-slate-800/70 backdrop-blur-xl shadow-[0_25px_60px_rgba(0,0,0,0.4)] overflow-hidden animate-[login-card-enter_0.6s_ease-out]">
          <div className="p-7">
            {/* Header */}
            <div className="mb-6">
              <h2 className="text-[1.35rem] font-semibold text-slate-100 m-0 mb-1">
                {isRegister ? 'Create Account' : 'Welcome Back'}
              </h2>
              <p className="text-sm text-slate-400 m-0">
                {isRegister
                  ? 'Register to start using AI-powered detection'
                  : 'Sign in to your account to continue'}
              </p>
            </div>

            {/* Error Message */}
            {error && (
              <div className="flex items-center gap-2 p-2.5 rounded-xl bg-red-500/10 border border-red-500/20 text-red-300 text-sm mb-4 animate-[login-shake_0.4s_ease-out]">
                <div className="w-5 h-5 rounded-full bg-red-500/20 flex items-center justify-center text-[0.7rem] font-bold shrink-0">!</div>
                <span>{error}</span>
              </div>
            )}

            {/* Form Fields */}
            <div className="flex flex-col gap-4">
              {/* Username */}
              <div className="flex flex-col gap-1.5">
                <label htmlFor="username" className="text-[0.8rem] font-medium text-slate-300">Username</label>
                <div className="relative flex items-center">
                  <div className="absolute left-[0.85rem] top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none z-[1] flex items-center justify-center">
                    <User size={15} />
                  </div>
                  <InputText
                    id="username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="demo"
                    className={inputClass}
                    onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
                  />
                </div>
              </div>

              {/* Full Name (Register only) */}
              <div
                className={`flex flex-col gap-1.5 overflow-hidden transition-all duration-300 ease ${
                  isRegister ? 'max-h-[100px] opacity-100' : 'max-h-0 opacity-0 pointer-events-none'
                }`}
              >
                <label htmlFor="fullName" className="text-[0.8rem] font-medium text-slate-300">Full Name</label>
                <div className="relative flex items-center">
                  <div className="absolute left-[0.85rem] top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none z-[1] flex items-center justify-center">
                    <UserPlus size={15} />
                  </div>
                  <InputText
                    id="fullName"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="Demo User"
                    className={inputClass}
                    onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
                  />
                </div>
              </div>

              {/* Email (Register only) */}
              <div
                className={`flex flex-col gap-1.5 overflow-hidden transition-all duration-300 ease ${
                  isRegister ? 'max-h-[100px] opacity-100' : 'max-h-0 opacity-0 pointer-events-none'
                }`}
              >
                <label htmlFor="email" className="text-[0.8rem] font-medium text-slate-300">Email</label>
                <div className="relative flex items-center">
                  <div className="absolute left-[0.85rem] top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none z-[1] flex items-center justify-center">
                    <Mail size={15} />
                  </div>
                  <InputText
                    id="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="demo@hematoscan.com"
                    className={inputClass}
                    onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
                  />
                </div>
              </div>

              {/* Password */}
              <div className="flex flex-col gap-1.5">
                <label htmlFor="password" className="text-[0.8rem] font-medium text-slate-300">Password</label>
                <div className="relative flex items-center">
                  <div className="absolute left-[0.85rem] top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none z-[1] flex items-center justify-center">
                    <Lock size={15} />
                  </div>
                  <Password
                    id="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="demo123"
                    toggleMask
                    feedback={false}
                    className="!w-full"
                    inputClassName={inputClass}
                    onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
                  />
                </div>
              </div>

              {/* Submit Button */}
              <Button
                label={loading ? 'Please wait...' : isRegister ? 'Create Account' : 'Sign In'}
                icon={
                  loading
                    ? 'pi pi-spin pi-spinner'
                    : isRegister
                      ? 'pi pi-user-plus'
                      : 'pi pi-sign-in'
                }
                iconPos="right"
                onClick={handleSubmit}
                disabled={loading}
                className="!w-full !mt-2 !py-3 !rounded-xl !bg-gradient-to-r !from-blue-600 !to-blue-500 !border-0 !text-white !text-[0.95rem] !font-semibold !shadow-[0_4px_16px_rgba(37,99,235,0.3)] hover:!from-blue-700 hover:!to-blue-600 hover:!shadow-[0_6px_24px_rgba(37,99,235,0.45)] hover:-translate-y-px active:translate-y-0 active:!shadow-[0_2px_8px_rgba(37,99,235,0.3)] disabled:opacity-60 disabled:cursor-not-allowed !transition-all !cursor-pointer"
                size="large"
              />
            </div>

            {/* Toggle Register/Login */}
            <div className="flex items-center justify-center gap-1 mt-5">
              <span className="text-sm text-slate-400">
                {isRegister ? 'Already have an account?' : "Don't have an account?"}
              </span>
              <button
                className="inline-flex items-center gap-1.5 text-sm font-semibold text-blue-400 bg-transparent border-0 p-0 cursor-pointer transition-all hover:text-blue-300 hover:gap-2"
                onClick={() => {
                  setIsRegister(!isRegister);
                  setError('');
                }}
              >
                {isRegister ? 'Sign In' : 'Register'}
                <ArrowRight size={14} className="transition-transform duration-200" />
              </button>
            </div>

            {/* Demo Credentials */}
            <div className="flex items-center justify-center gap-2 mt-5 px-4 py-2 rounded-full bg-blue-500/10 border border-blue-500/20 text-[0.78rem] text-blue-300">
              <div className="w-[7px] h-[7px] rounded-full bg-blue-500 login-demo-pulse shrink-0" />
              <span>
                <strong>Demo</strong> — Username: <code className="text-slate-100 font-semibold font-mono">demo</code> / Password: <code className="text-slate-100 font-semibold font-mono">demo123</code>
              </span>
            </div>
          </div>
        </Card>

        {/* Footer */}
        <p className="mt-6 text-xs text-slate-600 text-center">
          &copy; {new Date().getFullYear()} HematoScan. All rights reserved.
        </p>
      </div>
    </div>
  );
}
