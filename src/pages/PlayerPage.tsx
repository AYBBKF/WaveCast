import ReactPlayer from 'react-player';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';

export function PlayerPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const videoUrl = searchParams.get('url');

  if (!videoUrl) {
    return (
      <div className="w-screen h-screen bg-black flex flex-col items-center justify-center text-white">
        <h2 className="text-2xl font-bold mb-4">Erreur de lecture</h2>
        <p className="text-gray-400 mb-6">Aucune URL de vidéo n'a été fournie.</p>
        <button 
            onClick={() => navigate(-1)} 
            className="flex items-center bg-gray-700 text-white py-2 px-4 rounded-md hover:bg-gray-600 transition-colors"
        >
            <ArrowLeft size={20} className="mr-2" />
            Retour
        </button>
      </div>
    );
  }

  return (
    <div className="w-screen h-screen bg-black flex items-center justify-center relative">
      <ReactPlayer
        url={videoUrl}
        playing
        controls
        width="100%"
        height="100%"
        config={{
          file: {
            attributes: {
              controlsList: 'nodownload',
            },
          },
        }}
        onError={(e) => console.error('Player Error', e)}
      />
      <button 
          onClick={() => navigate(-1)} 
          className="absolute top-5 left-5 z-50 bg-black/50 p-3 rounded-full text-white hover:bg-black/75 transition-colors"
          aria-label="Retour"
      >
          <ArrowLeft size={24} />
      </button>
    </div>
  );
}
