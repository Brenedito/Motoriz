import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { describe, expect, test } from "vitest";
import { servidor } from "../testes/servidor";
import { renderizarComRotas, sessaoComo } from "../testes/ferramentas";

describe("sair", () => {
  test("se o servidor falha, a pessoa continua no app e vê o erro", async () => {
    // Sair da tela com o cookie ainda válido faria a pessoa voltar logada sozinha (tablet
    // compartilhado): o app só sai depois de o servidor confirmar.
    sessaoComo("admin");
    servidor.use(
      http.delete("/api/sessao", () => HttpResponse.json({ erro: "Falha" }, { status: 500 })),
    );
    const { cliente } = renderizarComRotas("/");
    await userEvent.click(await screen.findByRole("button", { name: "Sair" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Não foi possível sair. Tente novamente.",
    );
    expect(screen.getByRole("heading", { name: "Olá, Ana Souza" })).toBeInTheDocument();
    expect(cliente.getQueryData(["sessao"])).not.toBeNull();
  });

  test("sem rede, a pessoa continua no app e vê o erro", async () => {
    sessaoComo("admin");
    servidor.use(http.delete("/api/sessao", () => HttpResponse.error()));
    renderizarComRotas("/");
    await userEvent.click(await screen.findByRole("button", { name: "Sair" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Não foi possível sair. Tente novamente.",
    );
    expect(screen.queryByRole("button", { name: "Entrar" })).not.toBeInTheDocument();
  });

  test("sessão que já tinha expirado (401) conta como saída", async () => {
    sessaoComo("admin");
    servidor.use(
      http.delete("/api/sessao", () =>
        HttpResponse.json({ erro: "Sessão inválida." }, { status: 401 }),
      ),
    );
    renderizarComRotas("/");
    await userEvent.click(await screen.findByRole("button", { name: "Sair" }));
    expect(await screen.findByRole("button", { name: "Entrar" })).toBeInTheDocument();
  });
});

describe("rota protegida", () => {
  test("falha passageira ao ler a sessão oferece tentar de novo, sem mandar para o login", async () => {
    let disponivel = false;
    servidor.use(
      http.get("/api/sessao", () =>
        disponivel
          ? HttpResponse.json({
              usuario_id: "00000000-0000-7000-8000-000000000001",
              nome: "Ana Souza",
              email: "ana@locadora.com",
              papel: "admin",
              conta_id: "00000000-0000-7000-8000-0000000000aa",
              conta_nome: "Locadora Centro",
            })
          : new HttpResponse(null, { status: 502 }),
      ),
    );
    renderizarComRotas("/");

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Não foi possível verificar a sua sessão.",
    );
    expect(screen.queryByRole("button", { name: "Entrar" })).not.toBeInTheDocument();

    disponivel = true;
    await userEvent.click(screen.getByRole("button", { name: "Tentar de novo" }));
    expect(await screen.findByRole("heading", { name: "Olá, Ana Souza" })).toBeInTheDocument();
  });
});
