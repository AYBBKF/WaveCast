import { useAppStore } from '../store/useAppStore';
import { useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Tv } from 'lucide-react';

export function LivePage() {
  const playlist = useAppStore((state) => state.playlist);
  const navigate = useNavigate();

  const handleChannelClick = (url: string) => {
    navigate(`/player?url=${encodeURIComponent(url)}`);
  };

  if (playlist.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-center text-gray-400 p-10">
        <Tv size={64} className="mb-4" />
        <h2 className="text-2xl font-bold text-white mb-2">Aucune chaîne trouvée</h2>
        <p className="max-w-md">
          Pour commencer, veuillez ajouter l'URL de votre playlist M3U dans les{' '}
          <Link to="/settings" className="text-blue-400 hover:underline font-semibold">
            paramètres
          </Link>{' '}
          et la synchroniser.
        </p>
      </div>
    );
  }

  return (
    <div className="p-6 md:p-10 text-white">
      <h1 className="text-3xl font-bold mb-6">En Direct</h1>
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
        {playlist.map((channel, index) => (
          <motion.div
            key={channel.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.02 }}
            onClick={() => handleChannelClick(channel.url)}
            className="group aspect-video bg-card hover:bg-card-hover focus-within:bg-card-hover transition-all duration-200 rounded-lg flex flex-col items-center justify-center cursor-pointer relative overflow-hidden p-2 text-center focus:outline-none focus-visible:ring-4 focus-visible:ring-blue-500"
            tabIndex={0}
            onKeyDown={(e) => e.key === 'Enter' && handleChannelClick(channel.url)}
          >
            {channel.logo ? (
              <img 
                src={channel.logo} 
                alt={channel.name} 
                className="max-h-full max-w-full object-contain transition-transform duration-300 group-hover:scale-110" 
                onError={(e) => { e.currentTarget.style.display = 'none'; e.currentTarget.nextSibling?.classList.remove('hidden'); }}
              />
            ) : null}
            <span className={`font-semibold text-sm text-gray-200 ${channel.logo ? 'hidden' : ''} group-hover:opacity-80`}>
              {channel.name}
            </span>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
