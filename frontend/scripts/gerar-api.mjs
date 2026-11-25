// Gera src/api/openapi.json (a partir do backend, sem banco) e src/api/esquema.d.ts.
// Escrito em Node para funcionar igual no cmd do Windows e em shells POSIX.
import { spawnSync } from "node:child_process";
import { mkdirSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const raiz = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const saidaJson = resolve(raiz, "src/api/openapi.json");
const saidaTipos = resolve(raiz, "src/api/esquema.d.ts");
const comShell = process.platform === "win32";

const backend = spawnSync("uv", ["run", "python", "-m", "motoriz.exportar_openapi"], {
  cwd: resolve(raiz, "../backend"),
  encoding: "utf8",
  shell: comShell,
});
if (backend.status !== 0) {
  process.stderr.write(backend.stderr || String(backend.error));
  process.exit(backend.status ?? 1);
}
mkdirSync(dirname(saidaJson), { recursive: true });
writeFileSync(saidaJson, backend.stdout);

const tipos = spawnSync("npx", ["openapi-typescript", saidaJson, "-o", saidaTipos], {
  cwd: raiz,
  stdio: "inherit",
  shell: comShell,
});
process.exit(tipos.status ?? 1);
