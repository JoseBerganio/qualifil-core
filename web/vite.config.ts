import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  // The repository keeps a single shared .env at the root.
  envDir: "..",
  server: {
    proxy: {
      "/api": "http://localhost:8000",
    },
  },
});
