import { setupServer } from "msw/node";

// Sem handlers padrão: cada teste declara as rotas de que precisa.
export const servidor = setupServer();
