import { useEffect } from "react";
import { Link } from "react-router-dom";
import { exportXml, loadList, setCapturedOnly, toggleCapture } from "../features/pokedex/slice";
import { useAppDispatch, useAppSelector } from "../app/hooks";
import { PokemonListItem } from "../types/pokemon-list-item.type";

function downloadTextFile(filename: string, content: string, mime = "application/xml") {
  const blob = new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

export default function PageList() {
  const dispatch = useAppDispatch();
  const { items, total, offset, limit, loadingList, exportingXml, error, capturedOnly, togglingCaptureById } =
    useAppSelector((s) => s.pokedex);

  const pageSize = limit ?? 20;

  useEffect(() => {
    dispatch(loadList({ offset: 0, limit: pageSize, capturedOnly }));
  }, [dispatch, pageSize, capturedOnly]);

  const prev = () => dispatch(loadList({ offset: Math.max(0, offset - pageSize), limit: pageSize, capturedOnly }));

  const maxOffset = Math.max(0, total - pageSize);
  const next = () => dispatch(loadList({ offset: Math.min(maxOffset, offset + pageSize), limit: pageSize, capturedOnly }));

  const onExport = async () => {
    const xml = await dispatch(exportXml()).unwrap();
    downloadTextFile("pokedex.xml", xml);
  };

  const onToggleCapturedOnly = (checked: boolean) => {
    dispatch(setCapturedOnly(checked));
    dispatch(loadList({ offset: 0, limit: pageSize, capturedOnly: checked }));
  };

  const onToggleCaptureCard = (p: PokemonListItem) => {
    dispatch(toggleCapture({ id: p.id, nextCaptured: !p.captured }));
  };

  return (
    <div style={{ padding: 16, maxWidth: 1000, margin: "0 auto" }}>
      <h1>Pokédex</h1>

      <div style={{ display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
        <button onClick={prev} disabled={offset === 0 || loadingList}>Anterior</button>
        <button onClick={next} disabled={offset + pageSize >= total || loadingList}>Próximo</button>

        <span>
          {total === 0 ? "0-0" : `${offset + 1}-${Math.min(total, offset + pageSize)}`} de {total}
        </span>

        <label style={{ display: "flex", alignItems: "center", gap: 8, marginLeft: 12 }}>
          <input
            type="checkbox"
            checked={capturedOnly}
            onChange={(e) => onToggleCapturedOnly(e.target.checked)}
            disabled={loadingList}
          />
          <span>Mostrar apenas capturados</span>
        </label>

        <span style={{ flex: 1 }} />

        <button onClick={onExport} disabled={exportingXml || loadingList || total === 0}>
          {exportingXml ? "Exportando..." : "Exportar XML"}
        </button>
      </div>

      {error && (
        <p style={{ marginTop: 12, padding: 10, border: "1px solid #c00", borderRadius: 8 }}>
          <b>Erro:</b> {error}
        </p>
      )}

      {loadingList && <p>Carregando...</p>}

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))",
          gap: 12,
          marginTop: 16,
        }}
      >
        {items.map((p) => {
          const toggling = togglingCaptureById[p.id] ?? false;

          let cardButtonText = "Capturar";
          if (toggling) cardButtonText = "...";
          else if (p.captured) cardButtonText = "Soltar";

          return (
            <div
              key={p.id}
              style={{
                border: "1px solid #333",
                borderRadius: 12,
                padding: 12,
              }}
            >
              <Link
                to={`/pokemon/${p.id}`}
                style={{ textDecoration: "none", color: "inherit" }}
              >
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "baseline",
                  }}
                >
                  <strong style={{ textTransform: "capitalize" }}>
                    {p.name}
                  </strong>
                  <span>#{p.id}</span>
                </div>

                <div
                  style={{
                    display: "flex",
                    justifyContent: "center",
                    paddingTop: 10,
                  }}
                >
                  {p.sprite ? (
                    <img src={p.sprite} alt={p.name} />
                  ) : (
                    <div style={{ height: 96 }} />
                  )}
                </div>
              </Link>

              <div
                style={{
                  display: "flex",
                  gap: 8,
                  marginTop: 10,
                  alignItems: "center",
                }}
              >
                <span style={{ fontSize: 12 }}>
                  {p.captured ? "✅ Capturado" : "— Não capturado"}
                </span>
                <span style={{ flex: 1 }} />
                <button
                  onClick={() => onToggleCaptureCard(p)}
                  disabled={toggling || loadingList}
                >
                  {cardButtonText}
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}