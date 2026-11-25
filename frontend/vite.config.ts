/// <reference types="vitest/config" />
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";
import { VitePWA } from "vite-plugin-pwa";

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: "autoUpdate",
      manifest: {
        name: "Motoriz",
        short_name: "Motoriz",
        lang: "pt-BR",
        display: "standalone",
        start_url: "/",
        background_color: "#f9fafb",
        theme_color: "#1f2937",
        icons: [{ src: "icone.svg", sizes: "any", type: "image/svg+xml", purpose: "any" }],
      },
      workbox: {
        // A API nunca deve ser respondida pelo cache nem pela página de navegação offline.
        navigateFallbackDenylist: [/^\/api\//],
      },
    }),
  ],
  server: {
    proxy: { "/api": "http://localhost:8000" },
  },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./src/testes/configuracao.ts"],
    css: false,
  },
});
