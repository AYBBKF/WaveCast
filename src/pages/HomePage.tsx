import { HeroBanner } from '../components/ui/HeroBanner';
import { Carousel } from '../components/ui/Carousel';
import { mockHeroContent, mockMovies, mockSeries } from '../lib/mockData';

export function HomePage() {
  return (
    <div className="w-full">
      <HeroBanner item={mockHeroContent} />
      <Carousel title="Films Populaires" items={mockMovies} />
      <Carousel title="Séries du Moment" items={mockSeries} />
    </div>
  );
}
