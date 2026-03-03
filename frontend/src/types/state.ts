import { PokemonDetail } from "./pokemon-detail.type";
import { PokemonListItem } from "./pokemon-list-item.type";
import { PokemonPokedexDetail } from "./pokemon-pokedex-detail.type";

export type State = {
  total: number;
  offset: number;
  limit: number;
  items: PokemonListItem[];
  detailById: Record<number, PokemonDetail>;
  pokedexById: Record<number, PokemonPokedexDetail>;
  loadingList: boolean;
  loadingDetail: boolean;
  exportingXml: boolean;
  capturedOnly: boolean;
  togglingCaptureById: Record<number, boolean>;
  error?: string;
};