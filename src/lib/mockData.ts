import { faker } from '@faker-js/faker';

export interface ContentItem {
  id: string;
  title: string;
  description: string;
  posterUrl: string;
  backdropUrl: string;
  type: 'movie' | 'series';
}

const createMockContent = (type: 'movie' | 'series'): ContentItem => ({
  id: faker.string.uuid(),
  title: type === 'movie' ? faker.lorem.words(3) : faker.lorem.words(4),
  description: faker.lorem.paragraph(),
  posterUrl: `https://picsum.photos/seed/${faker.string.uuid()}/400/600`,
  backdropUrl: `https://picsum.photos/seed/${faker.string.uuid()}/1280/720`,
  type,
});

export const mockMovies: ContentItem[] = Array.from({ length: 20 }, () => createMockContent('movie'));
export const mockSeries: ContentItem[] = Array.from({ length: 20 }, () => createMockContent('series'));

export const mockHeroContent: ContentItem = {
    ...createMockContent('movie'),
    title: 'Mission: Cosmos',
    description: 'Une équipe d\'astronautes se lance dans une mission audacieuse pour trouver une nouvelle planète habitable alors que la Terre est au bord de l\'effondrement.'
};
