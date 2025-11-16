import { useState, useEffect } from 'react';
import { Routes, Route } from 'react-router-dom';
import { MainLayout } from './components/layout/MainLayout';
import { HomePage } from './pages/HomePage';
import { LivePage } from './pages/LivePage';
import { SettingsPage } from './pages/SettingsPage';
import { PlayerPage } from './pages/PlayerPage';
import { SplashScreen } from './pages/SplashScreen';
import { useAppStore } from './store/useAppStore';

function App() {
  const [showSplash, setShowSplash] = useState(true);
  const checkTrialStatus = useAppStore(state => state.checkTrialStatus);

  useEffect(() => {
    checkTrialStatus();
    const timer = setTimeout(() => setShowSplash(false), 2000); // Show splash for 2 seconds
    return () => clearTimeout(timer);
  }, [checkTrialStatus]);

  if (showSplash) {
    return <SplashScreen />;
  }

  return (
    <Routes>
      <Route path="/" element={<MainLayout />}>
        <Route index element={<HomePage />} />
        <Route path="live" element={<LivePage />} />
        <Route path="settings" element={<SettingsPage />} />
      </Route>
      <Route path="/player" element={<PlayerPage />} />
    </Routes>
  );
}

export default App;
