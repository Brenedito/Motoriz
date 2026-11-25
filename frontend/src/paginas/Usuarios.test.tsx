import { screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { describe, expect, test } from "vitest";
import { servidor } from "../testes/servidor";
import { ID_ANA, ID_BETO, renderizarComRotas, sessaoComo } from "../testes/ferramentas";

const ana = { id: ID_ANA, nome: "Ana Souza", email: "ana@locadora.com", papel: "admin", ativo: true };
const beto = { id: ID_BETO, nome: "Beto Lima", email: "beto@locadora.com", papel: "operador", ativo: true };

describe("Usuarios", () => {
  test("operador vê aviso em vez da lista", async () => {
    sessaoComo("operador");
    renderizarComRotas("/usuarios");
    expect(
      await screen.findByText("Apenas administradores podem gerenciar usuários."),
    ).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Novo usuário" })).not.toBeInTheDocument();
  });

  test("admin vê a lista e cria um usuário", async () => {
    sessaoComo("admin");
    const lista = [ana];
    let cabecalho: string | null = null;
    let corpo: unknown = null;
    servidor.use(
      http.get("/api/usuarios", () => HttpResponse.json(lista)),
      http.post("/api/usuarios", async ({ request }) => {
        cabecalho = request.headers.get("X-Motoriz");
        corpo = await request.json();
        lista.push(beto);
        return HttpResponse.json(beto, { status: 201 });
      }),
    );
    renderizarComRotas("/usuarios");
    expect(await screen.findByText("ana@locadora.com")).toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: "Novo usuário" }));
    await userEvent.type(screen.getByLabelText("Nome"), "Beto Lima");
    await userEvent.type(screen.getByLabelText("E-mail"), "beto@locadora.com");
    await userEvent.selectOptions(screen.getByLabelText("Papel"), "operador");
    await userEvent.type(screen.getByLabelText("Senha inicial"), "senha-inicial-1");
    await userEvent.click(screen.getByRole("button", { name: "Criar usuário" }));

    expect(await screen.findByText("beto@locadora.com")).toBeInTheDocument();
    expect(cabecalho).toBe("1");
    expect(corpo).toEqual({
      nome: "Beto Lima",
      email: "beto@locadora.com",
      papel: "operador",
      senha_inicial: "senha-inicial-1",
    });
  });

  test("desativar e reativar atualiza a lista", async () => {
    sessaoComo("admin");
    const lista = [ana, { ...beto }];
    servidor.use(
      http.get("/api/usuarios", () => HttpResponse.json(lista)),
      http.post(`/api/usuarios/${ID_BETO}/desativar`, () => {
        lista[1] = { ...beto, ativo: false };
        return new HttpResponse(null, { status: 204 });
      }),
      http.post(`/api/usuarios/${ID_BETO}/reativar`, () => {
        lista[1] = { ...beto, ativo: true };
        return new HttpResponse(null, { status: 204 });
      }),
    );
    renderizarComRotas("/usuarios");
    const linha = (await screen.findByText("beto@locadora.com")).closest("li") as HTMLElement;
    await userEvent.click(within(linha).getByRole("button", { name: "Desativar" }));
    await userEvent.click(await within(linha).findByRole("button", { name: "Reativar" }));
    expect(await within(linha).findByRole("button", { name: "Desativar" })).toBeInTheDocument();
  });

  test("erro da API ao desativar aparece na tela", async () => {
    sessaoComo("admin");
    servidor.use(
      http.get("/api/usuarios", () => HttpResponse.json([ana])),
      http.post(`/api/usuarios/${ID_ANA}/desativar`, () =>
        HttpResponse.json({ erro: "Você não pode desativar o seu próprio usuário" }, { status: 422 }),
      ),
    );
    renderizarComRotas("/usuarios");
    await userEvent.click(await screen.findByRole("button", { name: "Desativar" }));
    expect(
      await screen.findByText("Você não pode desativar o seu próprio usuário"),
    ).toBeInTheDocument();
    // um 422 de regra de negócio não derruba a sessão
    expect(screen.getByText("ana@locadora.com")).toBeInTheDocument();
  });
});
