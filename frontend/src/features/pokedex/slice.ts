import { createAsyncThunk, createSlice, PayloadAction } from "@reduxjs/toolkit";
import { fetchPokemons, fetchPokemonDetail, fetchPokemonPokedexDetail, fetchPokemonsXml, capturePokemon, releasePokemon } from "./api";
import { State } from "../../types/state";

export const loadList = createAsyncThunk(
  "pokedex/loadList",
  async (args: { offset: number; limit?: number; capturedOnly?: boolean }) =>
    fetchPokemons({ offset: args.offset, limit: args.limit, capturedOnly: args.capturedOnly })
);

export const loadDetail = createAsyncThunk(
  "pokedex/loadDetail",
  async (id: number) => fetchPokemonDetail(id)
);

export const loadPokedexDetail = createAsyncThunk(
  "pokedex/loadPokedexDetail",
  async (id: number) => fetchPokemonPokedexDetail(id)
);

export const exportXml = createAsyncThunk(
  "pokedex/exportXml",
  async () => fetchPokemonsXml()
);

export const toggleCapture = createAsyncThunk(
  "pokedex/toggleCapture",
  async (args: { id: number; nextCaptured: boolean }) => {
    const { id, nextCaptured } = args;
    return nextCaptured ? capturePokemon(id) : releasePokemon(id);
  }
);

const initialState: State = {
  total: 0,
  offset: 0,
  limit: 20,
  items: [],
  loadingList: false,

  detailById: {},
  pokedexById: {},
  loadingDetail: false,

  capturedOnly: false,
  togglingCaptureById: {},

  exportingXml: false,
  error: undefined,
};

const slice = createSlice({
  name: "pokedex",
  initialState,
  reducers: {
    setLimit(state, action: PayloadAction<number>) {
      state.limit = action.payload;
    },
    setCapturedOnly(state, action: PayloadAction<boolean>) {
      state.capturedOnly = action.payload;
      state.offset = 0;
    },
  },
  extraReducers: (b) => {
    b.addCase(loadList.pending, (s) => {
      s.loadingList = true;
      s.error = undefined;
    });
    b.addCase(loadList.fulfilled, (s, a) => {
      s.loadingList = false;
      s.total = a.payload.total;
      s.offset = a.payload.offset;
      s.items = a.payload.items;
    });
    b.addCase(loadList.rejected, (s, a) => {
      s.loadingList = false;
      s.error = a.error.message ?? "Erro ao carregar lista";
    });

    b.addCase(loadDetail.pending, (s) => {
      s.loadingDetail = true;
      s.error = undefined;
    });
    b.addCase(loadDetail.fulfilled, (s, a) => {
      s.loadingDetail = false;
      s.detailById[a.payload.id] = a.payload;
    });
    b.addCase(loadDetail.rejected, (s, a) => {
      s.loadingDetail = false;
      s.error = a.error.message ?? "Erro ao carregar detalhe";
    });

    b.addCase(loadPokedexDetail.pending, (s) => {
      s.loadingDetail = true;
      s.error = undefined;
    });
    b.addCase(loadPokedexDetail.fulfilled, (s, a) => {
      s.loadingDetail = false;
      s.pokedexById[a.payload.id] = a.payload;

      s.detailById[a.payload.id] = a.payload;
    });
    b.addCase(loadPokedexDetail.rejected, (s, a) => {
      s.loadingDetail = false;
      s.error = a.error.message ?? "Erro ao carregar Pokédex detail";
    });

    b.addCase(exportXml.pending, (s) => {
      s.exportingXml = true;
      s.error = undefined;
    });
    b.addCase(exportXml.fulfilled, (s) => {
      s.exportingXml = false;
    });
    b.addCase(exportXml.rejected, (s, a) => {
      s.exportingXml = false;
      s.error = a.error.message ?? "Erro ao exportar XML";
    });

    b.addCase(toggleCapture.pending, (s, a) => {
      const { id } = a.meta.arg;
      s.togglingCaptureById[id] = true;
      s.error = undefined;
    });
    b.addCase(toggleCapture.fulfilled, (s, a) => {
      const { id, captured } = a.payload;
      s.togglingCaptureById[id] = false;

      const item = s.items.find((x) => x.id === id);
      if (item) item.captured = captured;

      const d = s.detailById[id];
      if (d) d.captured = captured;

      const pd = s.pokedexById[id];
      if (pd) pd.captured = captured;

      if (s.capturedOnly && !captured) {
        s.items = s.items.filter((x) => x.id !== id);
        s.total = Math.max(0, s.total - 1);
      }
    });
    b.addCase(toggleCapture.rejected, (s, a) => {
      const { id } = a.meta.arg;
      s.togglingCaptureById[id] = false;
      s.error = a.error.message ?? "Erro ao atualizar captura";
    });
  },
});

export const { setLimit, setCapturedOnly } = slice.actions;
export default slice.reducer;