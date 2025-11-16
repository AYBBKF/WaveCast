import { ContentItem } from '../../lib/mockData';
import { PosterCard } from './PosterCard';

interface CarouselProps {
  title: string;
  items: ContentItem[];
}

export function Carousel({ title, items }: CarouselProps) {
  return (
    <div className="py-8 px-6 md:px-10">
      <h2 className="text-2xl font-bold mb-4 text-white">{title}</h2>
      <div className="flex space-x-4 overflow-x-auto pb-4 -mb-4">
        {items.map((item) => (
          <PosterCard key={item.id} item={item} />
        ))}
      </div>
    </div>
  );
}
