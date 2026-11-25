import { QueryClientProvider } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { MemoryRouter } from "react-router-dom";
import { RotasDoApp } from "../App";
import { criarQueryClient } from "../queryClient";
import { servidor } from "./servidor";

export function renderizarComRotas(rota: string) {
  const cliente = criarQueryClient();
  return render(
    <QueryClientProvider client={cliente}>
      <MemoryRouter initialEntries={[rota]}>
        <RotasDoApp />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

export const ID_ANA = "00000000-0000-7000-8000-000000000001";
export const ID_BETO = "00000000-0000-7000-8000-000000000002";

/** Simula `GET /api/sessao` com um usuário logado com o papel dado. */
export function sessaoComo(papel: "admin" | "operador") {
  servidor.use(
    http.get("/api/sessao", () =>
      HttpResponse.json({
        usuario_id: ID_ANA,
        nome: "Ana Souza",
        email: "ana@locadora.com",
        papel,
        conta_id: "00000000-0000-7000-8000-0000000000aa",
        conta_nome: "Locadora Centro",
      }),
    ),
  );
}

/** Simula `GET /api/sessao` sem sessão aberta. */
export function semSessao() {
  servidor.use(
    http.get("/api/sessao", () => HttpResponse.json({ erro: "Sessão inválida." }, { status: 401 })),
  );
}
