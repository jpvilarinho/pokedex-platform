import { PokemonDetail } from "./pokemon-detail.type";

export type PokemonPokedexDetail = PokemonDetail & {
  description?: string | null;
  genus?: string | null;
  egg_groups: string[];
  gender_rate?: number | null;
  evolution_chain: string[];
  weaknesses: string[];
};