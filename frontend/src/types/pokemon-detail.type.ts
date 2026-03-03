export type PokemonDetail = {
  id: number;
  name: string;
  sprite?: string | null;
  height?: number | null;
  weight?: number | null;
  types: string[];
  abilities: string[];
  stats: Record<string, number>;
  moves: string[];
  captured: boolean;
};