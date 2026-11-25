import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useSessao } from "../sessao/useSessao";

export function Layout() {
  const { sessao, sair } = useSessao();
  const navegar = useNavigate();

  async function aoSair() {
    await sair();
    navegar("/entrar", { replace: true });
  }

  return (
    <div className="aplicacao">
      <header className="cabecalho">
        <strong>Motoriz</strong>
        <nav aria-label="Principal">
          <NavLink to="/" end>
            Início
          </NavLink>
          {sessao?.papel === "admin" && <NavLink to="/usuarios">Usuários</NavLink>}
          <NavLink to="/senha">Senha</NavLink>
        </nav>
        <button type="button" className="secundario" onClick={aoSair}>
          Sair
        </button>
      </header>
      <main className="conteudo">
        <Outlet />
      </main>
    </div>
  );
}
