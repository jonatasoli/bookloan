import { fileURLToPath, URL } from "node:url";
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  server: {
    port: 5173,
    open: true,
    // Se precisar integrar com Django rodando em localhost:8000
    // descomente o proxy abaixo:
    proxy: {
      "/api": "http://127.0.0.1:8000",
    },
  },
  build: {
    outDir: "../static/frontend", // saída dos arquivos estáticos pro Django servir
    emptyOutDir: true,
  },
});
