import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

const BACKEND = "http://127.0.0.1:11140";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 11141,
    proxy: {
      "/api": { target: BACKEND, changeOrigin: true },
      "/mcp": { target: BACKEND, changeOrigin: true },
      "/docs": { target: BACKEND, changeOrigin: true },
      "/ws": { target: BACKEND, ws: true },
    },
  },
});