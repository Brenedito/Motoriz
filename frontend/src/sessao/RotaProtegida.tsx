import { Navigate, Outlet } from "react-router-dom";
import { useSessao } from "./useSessao";

/** Exige sessão aberta; sem ela, manda para /entrar. */
export function RotaProtegida() {
  const { sessao, carregando } = useSessao();
  if (carregando) return <p className="aviso">Carregando…</p>;
  if (!sessao) return <Navigate to="/entrar" replace />;
  return <Outlet />;
}
