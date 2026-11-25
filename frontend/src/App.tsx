import { Navigate, Route, Routes } from "react-router-dom";
import { AlterarSenha } from "./paginas/AlterarSenha";
import { Entrar } from "./paginas/Entrar";
import { Inicio } from "./paginas/Inicio";
import { Layout } from "./paginas/Layout";
import { Usuarios } from "./paginas/Usuarios";
import { RotaProtegida } from "./sessao/RotaProtegida";

export function RotasDoApp() {
  return (
    <Routes>
      <Route path="/entrar" element={<Entrar />} />
      <Route element={<RotaProtegida />}>
        <Route element={<Layout />}>
          <Route path="/" element={<Inicio />} />
          <Route path="/usuarios" element={<Usuarios />} />
          <Route path="/senha" element={<AlterarSenha />} />
        </Route>
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
