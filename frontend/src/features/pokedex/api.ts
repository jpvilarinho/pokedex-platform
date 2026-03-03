import { PokemonDetail } from "../../types/pokemon-detail.type";
import { PokemonListItem } from "../../types/pokemon-list-item.type";
import { PokemonPokedexDetail } from "../../types/pokemon-pokedex-detail.type";

const API_BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";

export async function fetchPokemons(args: {
  offset?: number;
  limit?: number;
  capturedOnly?: boolean;
  name?: string;
}) {
  const { offset = 0, limit, capturedOnly, name } = args;

  const params = new URLSearchParams({ offset: String(offset) });
  if (limit !== undefined) params.set("limit", String(limit));
  if (capturedOnly) params.set("captured_only", "true");
  if (name) params.set("name", name);

  const res = await fetch(`${API_BASE}/pokemon?${params.toString()}`);
  if (!res.ok) throw new Error("Failed to fetch pokemons");
  return res.json() as Promise<{
    total: number;
    offset: number;
    limit: number | null;
    items: PokemonListItem[];
  }>;
}

export async function fetchPokemonDetail(id: number) {
  const res = await fetch(`${API_BASE}/pokemon/${id}`);
  if (!res.ok) throw new Error("Failed to fetch pokemon detail");
  return res.json() as Promise<PokemonDetail>;
}

export async function fetchPokemonPokedexDetail(id: number) {
  const res = await fetch(`${API_BASE}/pokemon/${id}/pokedex`);
  if (!res.ok) throw new Error("Failed to fetch pokemon pokedex detail");
  return res.json() as Promise<PokemonPokedexDetail>;
}

export async function fetchPokemonsXml(): Promise<string> {
  const res = await fetch(`${API_BASE}/pokemon/export/xml`);
  if (!res.ok) throw new Error("Failed to export pokemons to XML");
  return res.text();
}

export async function capturePokemon(id: number) {
  const res = await fetch(`${API_BASE}/pokemon/${id}/capture`, { method: "POST" });
  if (!res.ok) throw new Error("Failed to capture pokemon");
  return res.json() as Promise<{ id: number; captured: boolean }>;
}

export async function releasePokemon(id: number) {
  const res = await fetch(`${API_BASE}/pokemon/${id}/capture`, { method: "DELETE" });
  if (!res.ok) throw new Error("Failed to release pokemon");
  return res.json() as Promise<{ id: number; captured: boolean }>;
}