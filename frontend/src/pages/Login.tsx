import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from 'primereact/card';
import { InputText } from 'primereact/inputtext';
import { Password } from 'primereact/password';
import { Button } from 'primereact/button';
import { Divider } from 'primereact/divider';
import { Message } from 'primereact/message';
import { Toast } from 'primereact/toast';
import { Microscope } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function Login() {
  const [isRegister, setIsRegister] = useState(false);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [fullName, setFullName] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login, register } = useAuth();
  const navigate = useNavigate();
  const toastRef = useRef<Toast>(null);

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
      // PublicRoute will auto-redirect to / since user is now set
    } catch (err: any) {
      const msg = err?.response?.data?.detail || 'Something went wrong';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-emerald-50 flex items-center justify-center p-4">
      <Toast ref={toastRef} />

      <div className="w-full max-w-md">
        {/* Brand */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-blue-600 text-white mb-4">
            <Microscope size={32} />
          </div>
          <h1 className="text-3xl font-bold text-gray-800">HematoScan</h1>
          <p className="text-sm text-gray-500 mt-1">Blood Cancer Detection System</p>
        </div>

        <Card className="shadow-xl border-0">
          <div className="p-2">
            <h2 className="text-xl font-semibold text-gray-800 mb-1">
              {isRegister ? 'Create Account' : 'Welcome Back'}
            </h2>
            <p className="text-sm text-gray-500 mb-6">
              {isRegister ? 'Register to start detecting' : 'Sign in to your account'}
            </p>

            {error && <Message severity="error" text={error} className="w-full mb-4" />}

            <div className="flex flex-col gap-4">
              <div className="flex flex-col gap-1">
                <label htmlFor="username" className="text-sm font-medium text-gray-700">Username</label>
                <InputText
                  id="username" value={username} onChange={(e) => setUsername(e.target.value)}
                  placeholder="demo" className="w-full" onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
                />
              </div>

              {isRegister && (
                <div className="flex flex-col gap-1">
                  <label htmlFor="email" className="text-sm font-medium text-gray-700">Email</label>
                  <InputText id="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="demo@hematoscan.com" className="w-full" />
                </div>
              )}

              {isRegister && (
                <div className="flex flex-col gap-1">
                  <label htmlFor="fullName" className="text-sm font-medium text-gray-700">Full Name</label>
                  <InputText id="fullName" value={fullName} onChange={(e) => setFullName(e.target.value)} placeholder="Demo User" className="w-full" />
                </div>
              )}

              <div className="flex flex-col gap-1">
                <label htmlFor="password" className="text-sm font-medium text-gray-700">Password</label>
                <Password
                  id="password" value={password} onChange={(e) => setPassword(e.target.value)}
                  placeholder="demo123" toggleMask feedback={false} className="w-full" inputClassName="w-full"
                  onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
                />
              </div>

              <Button
                label={loading ? 'Please wait...' : isRegister ? 'Create Account' : 'Sign In'}
                icon={loading ? 'pi pi-spin pi-spinner' : isRegister ? 'pi pi-user-plus' : 'pi pi-sign-in'}
                onClick={handleSubmit} disabled={loading}
                className="w-full mt-2" size="large"
              />
            </div>

            <Divider />

            <div className="text-center">
              <Button
                label={isRegister ? 'Already have an account? Sign In' : "Don't have an account? Register"}
                text className="p-0 text-sm text-blue-600 hover:text-blue-700"
                onClick={() => { setIsRegister(!isRegister); setError(''); }}
              />
            </div>

            <div className="mt-4 p-3 bg-blue-50 rounded-lg text-xs text-blue-700">
              <p className="font-semibold mb-1">💡 Demo Credentials</p>
              <p>Username: <strong>demo</strong> &nbsp;|&nbsp; Password: <strong>demo123</strong></p>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
