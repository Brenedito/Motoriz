import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { describe, expect, test } from "vitest";
import { servidor } from "../testes/servidor";
import { ID_ANA, renderizarComRotas, semSessao } from "../testes/ferramentas";

describe("Entrar", () => {
  test("mostra a mensagem da API quando o login falha", async () => {
    semSessao();
    servidor.use(
      http.post("/api/sessao", () =>
        HttpResponse.json({ erro: "E-mail ou senha incorretos." }, { status: 401 }),
      ),
    );
    renderizarComRotas("/entrar");
    await userEvent.type(await screen.findByLabelText("E-mail"), "ana@x.com");
    await userEvent.type(screen.getByLabelText("Senha"), "errada-errada");
    await userEvent.click(screen.getByRole("button", { name: "Entrar" }));
    expect(await screen.findByText("E-mail ou senha incorretos.")).toBeInTheDocument();
  });

  test("envia o cabeçalho X-Motoriz e vai para o início após o login", async () => {
    let logado = false;
    let cabecalho: string | null = null;
    let corpo: unknown = null;
    servidor.use(
      http.get("/api/sessao", () =>
        logado
          ? HttpResponse.json({
              usuario_id: ID_ANA,
              nome: "Ana Souza",
              email: "ana@locadora.com",
              papel: "admin",
              conta_id: "00000000-0000-7000-8000-0000000000aa",
              conta_nome: "Locadora Centro",
            })
          : HttpResponse.json({ erro: "Sessão inválida." }, { status: 401 }),
      ),
      http.post("/api/sessao", async ({ request }) => {
        cabecalho = request.headers.get("X-Motoriz");
        corpo = await request.json();
        logado = true;
        return new HttpResponse(null, { status: 204 });
      }),
    );
    renderizarComRotas("/entrar");
    await userEvent.type(await screen.findByLabelText("E-mail"), "ana@locadora.com");
    await userEvent.type(screen.getByLabelText("Senha"), "senha-correta-1");
    await userEvent.click(screen.getByRole("button", { name: "Entrar" }));

    expect(await screen.findByText(/Ana Souza/)).toBeInTheDocument();
    expect(screen.getByText(/Locadora Centro/)).toBeInTheDocument();
    expect(cabecalho).toBe("1");
    expect(corpo).toEqual({ email: "ana@locadora.com", senha: "senha-correta-1" });
  });

  test("sem sessão, uma rota protegida redireciona para o login", async () => {
    semSessao();
    renderizarComRotas("/");
    expect(await screen.findByRole("button", { name: "Entrar" })).toBeInTheDocument();
  });
});
