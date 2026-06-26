import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import UploadImage from './pages/UploadImage';
import BloodTest from './pages/BloodTest';
import Results from './pages/Results';
import History from './pages/History';
import './App.css';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/upload-image" element={<UploadImage />} />
          <Route path="/blood-test" element={<BloodTest />} />
          <Route path="/results" element={<Results />} />
          <Route path="/history" element={<History />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
