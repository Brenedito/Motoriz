import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { describe, expect, test } from "vitest";
import { servidor } from "../testes/servidor";
import { renderizarComRotas, sessaoComo } from "../testes/ferramentas";

describe("AlterarSenha", () => {
  test("senha atual incorreta (422) aparece como erro do formulário, sem derrubar a sessão", async () => {
    sessaoComo("admin");
    servidor.use(
      http.post("/api/sessao/senha", () =>
        HttpResponse.json({ erro: "Senha atual incorreta." }, { status: 422 }),
      ),
    );
    renderizarComRotas("/senha");
    await userEvent.type(await screen.findByLabelText("Senha atual"), "errada-errada");
    await userEvent.type(screen.getByLabelText("Nova senha"), "nova-senha-123");
    await userEvent.click(screen.getByRole("button", { name: "Alterar senha" }));
    expect(await screen.findByText("Senha atual incorreta.")).toBeInTheDocument();
    expect(screen.getByLabelText("Senha atual")).toBeInTheDocument();
  });

  test("troca a senha e confirma", async () => {
    sessaoComo("admin");
    let corpo: unknown = null;
    servidor.use(
      http.post("/api/sessao/senha", async ({ request }) => {
        corpo = await request.json();
        return new HttpResponse(null, { status: 204 });
      }),
    );
    renderizarComRotas("/senha");
    await userEvent.type(await screen.findByLabelText("Senha atual"), "senha-antiga-1");
    await userEvent.type(screen.getByLabelText("Nova senha"), "nova-senha-123");
    await userEvent.click(screen.getByRole("button", { name: "Alterar senha" }));
    expect(await screen.findByText("Senha alterada.")).toBeInTheDocument();
    expect(corpo).toEqual({ senha_atual: "senha-antiga-1", senha_nova: "nova-senha-123" });
  });
});
