import { MutationCache, QueryCache, QueryClient } from "@tanstack/react-query";
import { ErroDaApi } from "./api/cliente";
import { CHAVE_SESSAO } from "./sessao/useSessao";

/**
 * Um 401 em qualquer chamada autenticada significa que a sessão acabou (expirou, usuário
 * desativado, locadora suspensa): limpa a sessão e `RotaProtegida` leva para /entrar.
 * Só o 401 faz isso; um 422 (ex.: senha atual incorreta) é erro de formulário.
 */
export function criarQueryClient(): QueryClient {
  const cliente: QueryClient = new QueryClient({
    queryCache: new QueryCache({ onError: (erro) => encerrarSeNaoAutorizado(cliente, erro) }),
    mutationCache: new MutationCache({
      onError: (erro) => encerrarSeNaoAutorizado(cliente, erro),
    }),
    defaultOptions: { queries: { retry: false, refetchOnWindowFocus: true } },
  });
  return cliente;
}

function encerrarSeNaoAutorizado(cliente: QueryClient, erro: unknown) {
  if (erro instanceof ErroDaApi && erro.status === 401) {
    cliente.setQueryData(CHAVE_SESSAO, null);
  }
}
