import { useMutation } from "@tanstack/react-query";
import { useState, type FormEvent } from "react";
import { api, ErroDaApi } from "../api/cliente";

export function AlterarSenha() {
  const [senhaAtual, setSenhaAtual] = useState("");
  const [senhaNova, setSenhaNova] = useState("");

  const alterar = useMutation({
    mutationFn: async () => {
      const { error, response } = await api.POST("/api/sessao/senha", {
        body: { senha_atual: senhaAtual, senha_nova: senhaNova },
      });
      if (!response.ok) throw new ErroDaApi(response.status, error);
    },
    onSuccess: () => {
      setSenhaAtual("");
      setSenhaNova("");
    },
  });

  function aoEnviar(evento: FormEvent) {
    evento.preventDefault();
    alterar.mutate();
  }

  return (
    <section>
      <h1>Alterar senha</h1>
      <form onSubmit={aoEnviar} className="formulario">
        <label>
          Senha atual
          <input
            type="password"
            autoComplete="current-password"
            required
            value={senhaAtual}
            onChange={(e) => setSenhaAtual(e.target.value)}
          />
        </label>
        <label>
          Nova senha
          <input
            type="password"
            autoComplete="new-password"
            required
            minLength={10}
            maxLength={128}
            value={senhaNova}
            onChange={(e) => setSenhaNova(e.target.value)}
          />
        </label>
        <p className="discreto">De 10 a 128 caracteres.</p>
        {alterar.isError && (
          <p role="alert" className="erro">
            {alterar.error.message}
          </p>
        )}
        {alterar.isSuccess && <p role="status">Senha alterada.</p>}
        <button type="submit" disabled={alterar.isPending}>
          Alterar senha
        </button>
      </form>
    </section>
  );
}
