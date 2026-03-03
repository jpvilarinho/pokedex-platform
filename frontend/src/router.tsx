import { createBrowserRouter } from "react-router-dom";
import PageList from "./pages/page-list";
import PageDetail from "./pages/page-detail";

export const router = createBrowserRouter([
  { path: "/", element: <PageList /> },
  { path: "/pokemon/:id", element: <PageDetail /> }
]);
