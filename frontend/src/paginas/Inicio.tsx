import { useSessao } from "../sessao/useSessao";

export function Inicio() {
  const { sessao } = useSessao();
  if (!sessao) return null;
  return (
    <section>
      <h1>Olá, {sessao.nome}</h1>
      <p>{sessao.conta_nome}</p>
      <p className="discreto">
        {sessao.papel === "admin" ? "Administrador" : "Operador"} · {sessao.email}
      </p>
    </section>
  );
}
