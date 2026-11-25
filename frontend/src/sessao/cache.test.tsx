import { act, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { describe, expect, test } from "vitest";
import { criarQueryClient } from "../queryClient";
import { servidor } from "../testes/servidor";
import {
  chavesForaDaSessao,
  ID_ANA,
  ID_BETO,
  renderizarComRotas,
  sessaoComo,
} from "../testes/ferramentas";

// O cache do React Query é da aba, não da conta: ao trocar de usuário (sair, sessão expirada,
// outro login), nada da conta anterior pode sobrar nele para ser mostrado ao próximo.

const ana = { id: ID_ANA, nome: "Ana Souza", email: "ana@locadora.com", papel: "admin", ativo: true };
const beto = { id: ID_BETO, nome: "Beto Lima", email: "beto@locadora.com", papel: "operador", ativo: true };
const carla = {
  id: "00000000-0000-7000-8000-000000000003",
  nome: "Carla Dias",
  email: "carla@outra.com",
  papel: "admin",
  ativo: true,
};

const sessaoDaCarla = {
  usuario_id: carla.id,
  nome: carla.nome,
  email: carla.email,
  papel: "admin",
  conta_id: "00000000-0000-7000-8000-0000000000bb",
  conta_nome: "Outra Locadora",
};

describe("cache entre sessões", () => {
  test("sair limpa o cache", async () => {
    sessaoComo("admin");
    servidor.use(
      http.get("/api/usuarios", () => HttpResponse.json([ana, beto])),
      http.delete("/api/sessao", () => new HttpResponse(null, { status: 204 })),
    );
    const { cliente } = renderizarComRotas("/usuarios");
    expect(await screen.findByText("beto@locadora.com")).toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: "Sair" }));

    expect(await screen.findByRole("button", { name: "Entrar" })).toBeInTheDocument();
    expect(chavesForaDaSessao(cliente)).toEqual([]);
  });

  test("um 401 leva ao login e limpa o cache", async () => {
    sessaoComo("admin");
    let expirou = false;
    servidor.use(
      http.get("/api/usuarios", () =>
        expirou
          ? HttpResponse.json({ erro: "Sessão inválida." }, { status: 401 })
          : HttpResponse.json([ana, beto]),
      ),
    );
    const { cliente } = renderizarComRotas("/usuarios");
    expect(await screen.findByText("beto@locadora.com")).toBeInTheDocument();

    expirou = true;
    await act(() => cliente.invalidateQueries({ queryKey: ["usuarios"] }));

    expect(await screen.findByRole("button", { name: "Entrar" })).toBeInTheDocument();
    expect(cliente.getQueryData(["sessao"])).toBeNull();
    expect(chavesForaDaSessao(cliente)).toEqual([]);
  });

  test("depois do login de outro usuário, a lista antiga não aparece", async () => {
    let logado = false;
    let liberarLista: () => void = () => {};
    const listaPronta = new Promise<void>((resolver) => {
      liberarLista = resolver;
    });
    servidor.use(
      http.get("/api/sessao", () =>
        logado
          ? HttpResponse.json(sessaoDaCarla)
          : HttpResponse.json({ erro: "Sessão inválida." }, { status: 401 }),
      ),
      http.post("/api/sessao", () => {
        logado = true;
        return new HttpResponse(null, { status: 204 });
      }),
      http.get("/api/usuarios", async () => {
        await listaPronta; // segura a resposta: o que aparecer antes dela veio do cache
        return HttpResponse.json([carla]);
      }),
    );
    // Sobra de uma sessão anterior na mesma aba (outra conta).
    const cliente = criarQueryClient();
    cliente.setQueryData(["usuarios"], [ana, beto]);
    renderizarComRotas("/entrar", cliente);

    await userEvent.type(await screen.findByLabelText("E-mail"), carla.email);
    await userEvent.type(screen.getByLabelText("Senha"), "senha-da-carla-1");
    await userEvent.click(screen.getByRole("button", { name: "Entrar" }));
    await userEvent.click(await screen.findByRole("link", { name: "Usuários" }));

    expect(screen.queryByText("beto@locadora.com")).not.toBeInTheDocument();
    expect(screen.queryByText("ana@locadora.com")).not.toBeInTheDocument();
    liberarLista();
    expect(await screen.findByText("carla@outra.com")).toBeInTheDocument();
  });
});
