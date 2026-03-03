import { useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { loadPokedexDetail, toggleCapture } from "../features/pokedex/slice";
import { useAppDispatch, useAppSelector } from "../app/hooks";

export default function PageDetail() {
  const { id } = useParams();
  const pokemonId = Number(id);

  const dispatch = useAppDispatch();

  const detail = useAppSelector((s) => s.pokedex.pokedexById[pokemonId]);
  const loading = useAppSelector((s) => s.pokedex.loadingDetail);
  const error = useAppSelector((s) => s.pokedex.error);
  const toggling = useAppSelector((s) => s.pokedex.togglingCaptureById[pokemonId] ?? false);

  const isValidId = Number.isFinite(pokemonId) && pokemonId > 0;

  useEffect(() => {
    if (!isValidId) return;
    if (!detail) dispatch(loadPokedexDetail(pokemonId));
  }, [dispatch, pokemonId, detail, isValidId]);

  if (!isValidId) return <p style={{ padding: 16 }}>ID inválido.</p>;
  if (loading && !detail) return <p style={{ padding: 16 }}>Carregando...</p>;
  if (!detail) return <p style={{ padding: 16 }}>Não encontrado.</p>;

  const onToggleCapture = () => {
    dispatch(toggleCapture({ id: pokemonId, nextCaptured: !detail.captured }));
  };
  
  let captureButtonText: string = "Capturar";
  if (toggling) captureButtonText = "Salvando...";
  else if (detail.captured) captureButtonText = "Soltar";

  return (
    <div style={{ padding: 16, maxWidth: 900, margin: "0 auto" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
        <Link to="/">← Voltar</Link>
        <span style={{ flex: 1 }} />
        <button onClick={onToggleCapture} disabled={toggling}>
          {captureButtonText}
        </button>
      </div>

      {error && (
        <p style={{ marginTop: 12, padding: 10, border: "1px solid #c00", borderRadius: 8 }}>
          <b>Erro:</b> {String(error)}
        </p>
      )}

      <h1 style={{ textTransform: "capitalize" }}>
        {detail.name} <small>#{detail.id}</small>
        {detail.captured && <small style={{ marginLeft: 10 }}>✅ Capturado</small>}
      </h1>

      {detail.sprite && <img src={detail.sprite} alt={detail.name} />}

      {/* Pokédex-like fields */}
      {(detail.genus || detail.description) && (
        <div style={{ marginTop: 12, padding: 12, border: "1px solid #333", borderRadius: 12 }}>
          {detail.genus && <p style={{ margin: 0 }}><b>Gênero:</b> {detail.genus}</p>}
          {detail.description && <p style={{ marginTop: 8 }}><b>Descrição:</b> {detail.description}</p>}
        </div>
      )}

      <p><b>Tipos:</b> {detail.types.join(", ")}</p>
      <p><b>Habilidades:</b> {detail.abilities.join(", ")}</p>
      <p><b>Altura:</b> {detail.height} | <b>Peso:</b> {detail.weight}</p>

      {detail.weaknesses?.length > 0 && (
        <>
          <h3>Fraquezas</h3>
          <p>{detail.weaknesses.join(", ")}</p>
        </>
      )}

      {detail.evolution_chain?.length > 0 && (
        <>
          <h3>Cadeia de evolução</h3>
          <p style={{ textTransform: "capitalize" }}>{detail.evolution_chain.join(" → ")}</p>
        </>
      )}

      <h3>Status</h3>
      <ul>
        {Object.keys(detail.stats).map((k) => (
          <li key={k}>
            {k}: {detail.stats[k]}
          </li>
        ))}
      </ul>

      <h3>Moves (até 200)</h3>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
        {detail.moves.map((m: string) => (
          <span key={m} style={{ border: "1px solid #333", borderRadius: 999, padding: "4px 10px" }}>
            {m}
          </span>
        ))}
      </div>
    </div>
  );
}