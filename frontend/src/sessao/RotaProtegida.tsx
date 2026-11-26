import { Navigate, Outlet } from "react-router-dom";
import { useSessao } from "./useSessao";

/**
 * Exige sessão aberta; sem ela (401), manda para /entrar. Uma falha passageira (5xx, rede, a API
 * reiniciando) não é "sem sessão": mostra o erro e deixa tentar de novo.
 */
export function RotaProtegida() {
  const { sessao, carregando, falhou, tentarDeNovo } = useSessao();
  if (sessao) return <Outlet />; // mesmo se um refetch em segundo plano falhar
  if (falhou) {
    return (
      <div className="aviso">
        <p role="alert" className="erro">
          Não foi possível verificar a sua sessão.
        </p>
        <button type="button" onClick={tentarDeNovo}>
          Tentar de novo
        </button>
      </div>
    );
  }
  if (carregando) return <p className="aviso">Carregando…</p>;
  return <Navigate to="/entrar" replace />;
}
