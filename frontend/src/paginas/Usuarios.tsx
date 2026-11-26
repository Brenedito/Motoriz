import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState, type FormEvent } from "react";
import { api, ErroDaApi } from "../api/cliente";
import type { components } from "../api/esquema";
import { useSessao } from "../sessao/useSessao";

type UsuarioSaida = components["schemas"]["UsuarioSaida"];
type Papel = UsuarioSaida["papel"];

const CHAVE_USUARIOS = ["usuarios"] as const;
const ROTULO_PAPEL: Record<Papel, string> = { admin: "Administrador", operador: "Operador" };

export function Usuarios() {
  const { sessao } = useSessao();
  if (sessao?.papel !== "admin") {
    return <p role="alert">Apenas administradores podem gerenciar usuários.</p>;
  }
  return <ListaDeUsuarios meuId={sessao.usuario_id} />;
}

function ListaDeUsuarios({ meuId }: { meuId: string }) {
  const queryClient = useQueryClient();
  const [criando, setCriando] = useState(false);

  const lista = useQuery({
    queryKey: CHAVE_USUARIOS,
    queryFn: async () => {
      const { data, error, response } = await api.GET("/api/usuarios");
      if (data === undefined) throw new ErroDaApi(response.status, error);
      return data;
    },
  });

  const alterarAtivo = useMutation({
    mutationFn: async (v: { id: string; acao: "desativar" | "reativar" }) => {
      const caminho =
        v.acao === "desativar" ? "/api/usuarios/{id}/desativar" : "/api/usuarios/{id}/reativar";
      const { error, response } = await api.POST(caminho, { params: { path: { id: v.id } } });
      if (!response.ok) throw new ErroDaApi(response.status, error);
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: CHAVE_USUARIOS }),
  });

  return (
    <section>
      <h1>Usuários</h1>
      {!criando && (
        <button type="button" onClick={() => setCriando(true)}>
          Novo usuário
        </button>
      )}
      {criando && <FormularioNovoUsuario aoConcluir={() => setCriando(false)} />}

      {alterarAtivo.isError && (
        <p role="alert" className="erro">
          {alterarAtivo.error.message}
        </p>
      )}
      {lista.isPending && <p className="aviso">Carregando…</p>}
      {lista.isError && (
        <p role="alert" className="erro">
          {lista.error.message}
        </p>
      )}
      <ul className="lista">
        {lista.data?.map((u) => (
          <li key={u.id} className={u.ativo ? undefined : "inativo"}>
            <div>
              <strong>{u.nome}</strong>
              <span>{u.email}</span>
              <span className="discreto">
                {ROTULO_PAPEL[u.papel]}
                {u.ativo ? "" : " · inativo"}
                {u.id === meuId ? " · você" : ""}
              </span>
            </div>
            {/* O próprio usuário não pode se desativar: o botão só levaria a um erro. */}
            {u.id !== meuId && (
              <button
                type="button"
                className="secundario"
                disabled={alterarAtivo.isPending}
                onClick={() =>
                  alterarAtivo.mutate({ id: u.id, acao: u.ativo ? "desativar" : "reativar" })
                }
              >
                {u.ativo ? "Desativar" : "Reativar"}
              </button>
            )}
          </li>
        ))}
      </ul>
    </section>
  );
}

function FormularioNovoUsuario({ aoConcluir }: { aoConcluir: () => void }) {
  const queryClient = useQueryClient();
  const [nome, setNome] = useState("");
  const [email, setEmail] = useState("");
  const [papel, setPapel] = useState<Papel>("operador");
  const [senhaInicial, setSenhaInicial] = useState("");

  const criar = useMutation({
    mutationFn: async () => {
      const { error, response } = await api.POST("/api/usuarios", {
        body: { nome, email, papel, senha_inicial: senhaInicial },
      });
      if (!response.ok) throw new ErroDaApi(response.status, error);
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: CHAVE_USUARIOS });
      aoConcluir();
    },
  });

  function aoEnviar(evento: FormEvent) {
    evento.preventDefault();
    criar.mutate();
  }

  return (
    <form onSubmit={aoEnviar} className="formulario">
      <label>
        Nome
        <input required value={nome} onChange={(e) => setNome(e.target.value)} />
      </label>
      <label>
        E-mail
        <input
          type="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
      </label>
      <label>
        Papel
        <select value={papel} onChange={(e) => setPapel(e.target.value as Papel)}>
          <option value="operador">Operador</option>
          <option value="admin">Administrador</option>
        </select>
      </label>
      <label>
        Senha inicial
        <input
          type="password"
          autoComplete="new-password"
          required
          minLength={10}
          maxLength={128}
          value={senhaInicial}
          onChange={(e) => setSenhaInicial(e.target.value)}
        />
      </label>
      {criar.isError && (
        <p role="alert" className="erro">
          {criar.error.message}
        </p>
      )}
      <div className="acoes">
        <button type="submit" disabled={criar.isPending}>
          Criar usuário
        </button>
        <button type="button" className="secundario" onClick={aoConcluir}>
          Cancelar
        </button>
      </div>
    </form>
  );
}
