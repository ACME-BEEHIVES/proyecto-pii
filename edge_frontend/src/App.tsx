import { Routes, Route } from 'react-router-dom';
import EdgeLayout from './components/EdgeLayout';
import Dashboard from './pages/Dashboard';
import ScanConfigPage from './pages/ScanConfig';
import FindingsPage from './pages/Findings';
import DsarLookupPage from './pages/DsarLookup';
import RedactionPage from './pages/Redaction';
import IdentityGraphPage from './pages/IdentityGraph';
import HelpCenterPage from './pages/HelpCenter';

function App() {
  return (
    <EdgeLayout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/findings" element={<FindingsPage />} />
        <Route path="/config" element={<ScanConfigPage />} />
        <Route path="/dsar" element={<DsarLookupPage />} />
        <Route path="/redaction" element={<RedactionPage />} />
        <Route path="/identity" element={<IdentityGraphPage />} />
        <Route path="/help" element={<HelpCenterPage />} />
      </Routes>
    </EdgeLayout>
  );
}

export default App;
