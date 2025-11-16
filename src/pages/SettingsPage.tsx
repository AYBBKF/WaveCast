import { useState } from 'react';
import { useAppStore } from '../store/useAppStore';
import parser from 'iptv-playlist-parser';
import { Channel } from '../types';

export function SettingsPage() {
  const { deviceId, isTrialActive, trialEndDate, isActivated, m3uUrl, setM3uUrl, setPlaylist } = useAppStore(
    (state) => ({
      deviceId: state.deviceId,
      isTrialActive: state.isTrialActive,
      trialEndDate: state.trialEndDate,
      isActivated: state.isActivated,
      m3uUrl: state.m3uUrl,
      setM3uUrl: state.setM3uUrl,
      setPlaylist: state.setPlaylist,
    })
  );

  const [urlInput, setUrlInput] = useState(m3uUrl);
  const [syncLoading, setSyncLoading] = useState(false);
  const [syncMessage, setSyncMessage] = useState('');
  const [urlSaveMessage, setUrlSaveMessage] = useState('');

  const handleSaveUrl = (e: React.FormEvent) => {
    e.preventDefault();
    setM3uUrl(urlInput);
    setUrlSaveMessage('URL enregistrée avec succès !');
    setTimeout(() => setUrlSaveMessage(''), 3000);
  };

  const handleSync = async () => {
    setSyncLoading(true);
    setSyncMessage('');
    setUrlSaveMessage('');

    if (!m3uUrl) {
      setSyncMessage("Veuillez d'abord enregistrer une URL M3U.");
      setSyncLoading(false);
      return;
    }

    try {
      // NOTE: This fetch can fail due to CORS policy on the server providing the M3U file.
      // For local development, a browser extension to disable CORS might be needed.
      const response = await fetch(m3uUrl);
      if (!response.ok) {
        throw new Error(`Erreur HTTP: ${response.status}`);
      }
      const m3uText = await response.text();
      const result = parser.parse(m3uText);

      const channels: Channel[] = result.items.map((item, index) => ({
        id: `${item.url}-${index}`,
        name: item.name || `Chaîne ${index + 1}`,
        logo: item.tvg.logo,
        url: item.url,
        group: item.group.title,
      }));

      setPlaylist(channels);
      setSyncMessage(`Playlist synchronisée ! ${channels.length} chaînes chargées.`);
    } catch (error) {
      console.error("Sync error:", error);
      setSyncMessage("Erreur de synchronisation. Vérifiez l'URL et la politique CORS du serveur distant.");
    } finally {
      setSyncLoading(false);
    }
  };

  const getTrialStatusText = () => {
    if (isActivated) return <span className="text-green-400">Votre licence est active.</span>;
    if (isTrialActive && trialEndDate) {
      const daysRemaining = Math.ceil((trialEndDate - Date.now()) / (1000 * 60 * 60 * 24));
      return <span className="text-yellow-400">{`Essai gratuit : ${daysRemaining} jour(s) restant(s).`}</span>;
    }
    return <span className="text-red-500">Votre période d'essai est terminée.</span>;
  };

  return (
    <div className="p-6 md:p-10 text-white max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">Paramètres</h1>
      
      <div className="space-y-6">
        <div className="bg-card p-6 rounded-lg">
          <h2 className="text-xl font-semibold mb-3">Statut de l'Activation</h2>
          <p className="text-gray-300">{getTrialStatusText()}</p>
          {!isActivated && !isTrialActive && (
            <button className="mt-4 bg-red-600 text-white font-bold py-2 px-6 rounded-md hover:bg-red-700 transition-colors">
              Activer pour 4.99€/an
            </button>
          )}
        </div>

        <div className="bg-card p-6 rounded-lg">
          <h2 className="text-xl font-semibold mb-2">Identifiant de l'appareil</h2>
          <p className="text-gray-400 mb-4">Utilisez cet identifiant pour connecter votre appareil sur notre site web.</p>
          <div className="flex items-center space-x-4 bg-background p-3 rounded-md">
            <code className="text-lg text-gray-300 flex-grow">{deviceId}</code>
            <button 
              onClick={() => navigator.clipboard.writeText(deviceId)}
              className="bg-gray-600 text-white py-2 px-4 rounded-md hover:bg-gray-500 transition-colors text-sm"
            >
              Copier
            </button>
          </div>
        </div>

        <div className="bg-card p-6 rounded-lg">
          <h2 className="text-xl font-semibold mb-4">Gestion de la Playlist</h2>
          
          <form onSubmit={handleSaveUrl} className="space-y-4">
            <div>
              <label htmlFor="m3u-url" className="block text-sm font-medium text-gray-300 mb-2">
                URL de la playlist M3U
              </label>
              <div className="flex flex-col sm:flex-row sm:space-x-2 space-y-2 sm:space-y-0">
                <input
                  id="m3u-url"
                  type="url"
                  value={urlInput}
                  onChange={(e) => setUrlInput(e.target.value)}
                  placeholder="https://exemple.com/playlist.m3u"
                  className="flex-grow bg-background p-3 rounded-md text-gray-200 focus:ring-2 focus:ring-blue-500 border border-gray-600 w-full"
                />
                <button 
                  type="submit"
                  className="bg-green-600 text-white font-bold py-2 px-4 rounded-md hover:bg-green-700 transition-colors flex-shrink-0"
                >
                  Sauvegarder
                </button>
              </div>
              {urlSaveMessage && <p className="mt-2 text-sm text-green-400">{urlSaveMessage}</p>}
            </div>
          </form>

          <div className="mt-6 border-t border-gray-700 pt-6">
            <p className="text-gray-400 mb-4">Une fois l'URL sauvegardée, synchronisez-la pour charger les chaînes.</p>
            <button 
              onClick={handleSync}
              disabled={syncLoading || !m3uUrl}
              className="bg-blue-600 text-white font-bold py-3 px-8 rounded-md hover:bg-blue-700 transition-colors disabled:bg-gray-500 disabled:cursor-not-allowed"
            >
              {syncLoading ? 'Synchronisation...' : 'Synchroniser la Playlist'}
            </button>
            {syncMessage && <p className={`mt-4 text-sm ${syncMessage.includes('Erreur') ? 'text-red-400' : 'text-green-400'}`}>{syncMessage}</p>}
          </div>
        </div>
      </div>
    </div>
  );
}
