import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react-swc";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  return {
    plugins: [react()],
    define: {
      __APP_VERSION__: JSON.stringify("0.1.0"),
      __API_BASE_URL__: JSON.stringify(env.VITE_API_BASE_URL || "http://localhost:8000"),
    },
    server: {
      host: "0.0.0.0",
      port: 5173,
    },
  };
});
