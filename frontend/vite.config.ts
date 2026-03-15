import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import { tanstackRouter } from "@tanstack/router-plugin/vite";
import checker from "vite-plugin-checker";
import path from "path";

export default defineConfig({
    plugins: [
        tanstackRouter({
            routesDirectory: "./src/routes",
            generatedRouteTree: "./src/routeTree.gen",
        }),
        react(),
        tailwindcss(),
        checker({ typescript: true }),
    ],
    resolve: {
        alias: {
            "@": path.resolve(__dirname, "./src"),
        },
    },
    server: {
        host: "0.0.0.0",
        port: 5173,
        proxy: {
          "/api": {
            target: 'http://web:8000',
            changeOrigin: true
          }
        }
    },
});
