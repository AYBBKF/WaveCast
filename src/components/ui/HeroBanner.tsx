import { Play } from 'lucide-react';
import { ContentItem } from '../../lib/mockData';

interface HeroBannerProps {
  item: ContentItem;
}

export function HeroBanner({ item }: HeroBannerProps) {
  return (
    <div className="relative h-[60vh] w-full flex items-end p-6 md:p-10">
      <div className="absolute inset-0">
        <img src={item.backdropUrl} alt={item.title} className="w-full h-full object-cover" />
        <div className="absolute inset-0 bg-gradient-to-t from-background via-background/70 to-transparent" />
        <div className="absolute inset-0 bg-gradient-to-r from-background via-transparent to-transparent" />
      </div>
      <div className="relative z-10 max-w-xl">
        <h1 className="text-4xl md:text-6xl font-black text-white mb-4" style={{ textShadow: '2px 2px 4px rgba(0,0,0,0.7)' }}>
          {item.title}
        </h1>
        <p className="text-gray-300 mb-6 text-sm md:text-base max-w-prose">{item.description}</p>
        <button className="flex items-center bg-white text-black font-bold py-3 px-8 rounded-md hover:bg-gray-200 transition-colors focus:outline-none focus-visible:ring-4 focus-visible:ring-blue-500">
          <Play className="mr-2 h-6 w-6" fill="black" />
          Lecture
        </button>
      </div>
    </div>
  );
}
