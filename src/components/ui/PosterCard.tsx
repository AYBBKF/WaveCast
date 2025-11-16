import { motion } from 'framer-motion';
import { ContentItem } from '../../lib/mockData';

interface PosterCardProps {
  item: ContentItem;
}

export function PosterCard({ item }: PosterCardProps) {
  return (
    <motion.div
      className="group relative flex-shrink-0 w-40 md:w-48 rounded-lg overflow-hidden cursor-pointer focus:outline-none"
      whileHover={{ scale: 1.05, zIndex: 10 }}
      transition={{ duration: 0.2 }}
    >
      <img src={item.posterUrl} alt={item.title} className="w-full h-full object-cover" />
      <div className="absolute inset-0 bg-black bg-opacity-50 opacity-0 group-hover:opacity-100 group-focus-visible:opacity-100 transition-opacity duration-300 flex items-end p-3">
        <h3 className="text-white text-sm font-bold">{item.title}</h3>
      </div>
    </motion.div>
  );
}
