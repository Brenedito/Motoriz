import { useState, type FormEvent } from "react";
import { Navigate } from "react-router-dom";
import { mensagemDeErro } from "../api/cliente";
import { useSessao } from "../sessao/useSessao";

export function Entrar() {
  const { sessao, entrar } = useSessao();
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [erro, setErro] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  if (sessao) return <Navigate to="/" replace />;

  async function aoEnviar(evento: FormEvent) {
    evento.preventDefault();
    setErro(null);
    setEnviando(true);
    try {
      await entrar(email, senha);
    } catch (e) {
      setErro(e instanceof Error ? e.message : mensagemDeErro(e));
    } finally {
      setEnviando(false);
    }
  }

  return (
    <main className="conteudo estreito">
      <h1>Motoriz</h1>
      <form onSubmit={aoEnviar} className="formulario">
        <label>
          E-mail
          <input
            type="email"
            autoComplete="username"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </label>
        <label>
          Senha
          <input
            type="password"
            autoComplete="current-password"
            required
            value={senha}
            onChange={(e) => setSenha(e.target.value)}
          />
        </label>
        {erro && (
          <p role="alert" className="erro">
            {erro}
          </p>
        )}
        <button type="submit" disabled={enviando}>
          Entrar
        </button>
      </form>
    </main>
  );
}
