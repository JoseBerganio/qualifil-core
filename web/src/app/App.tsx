import { Route, BrowserRouter, Routes } from "react-router-dom";
import { AppStatusPage } from "../pages/AppStatusPage";

export function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<AppStatusPage />} />
        <Route path="/status" element={<AppStatusPage />} />
      </Routes>
    </BrowserRouter>
  );
}
