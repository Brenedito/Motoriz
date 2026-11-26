import { useState } from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useSessao } from "../sessao/useSessao";

export function Layout() {
  const { sessao, sair } = useSessao();
  const navegar = useNavigate();
  const [saindo, setSaindo] = useState(false);
  const [falhaAoSair, setFalhaAoSair] = useState(false);

  async function aoSair() {
    setSaindo(true);
    setFalhaAoSair(false);
    try {
      await sair();
    } catch {
      // Sem a confirmação do servidor o cookie pode seguir válido: a pessoa fica e é avisada.
      setFalhaAoSair(true);
      setSaindo(false);
      return;
    }
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
        <button type="button" className="secundario" onClick={aoSair} disabled={saindo}>
          Sair
        </button>
      </header>
      {falhaAoSair && (
        <p role="alert" className="erro">
          Não foi possível sair. Tente novamente.
        </p>
      )}
      <main className="conteudo">
        <Outlet />
      </main>
    </div>
  );
}
