import { useQuery, useQueryClient, type QueryClient } from "@tanstack/react-query";
import { api, ErroDaApi } from "../api/cliente";
import type { components } from "../api/esquema";

export type SessaoAtual = components["schemas"]["SessaoAtual"];

export const CHAVE_SESSAO = ["sessao"] as const;

/**
 * Tira do cache tudo o que não é a própria sessão. O cache é da aba, não da conta: sem isso,
 * o próximo usuário (talvez de outra locadora) veria os dados do anterior até o refetch.
 */
export function limparDadosDaConta(cliente: QueryClient): void {
  cliente.removeQueries({ predicate: (q) => q.queryKey[0] !== CHAVE_SESSAO[0] });
}

export function useSessao(): {
  sessao: SessaoAtual | null;
  carregando: boolean;
  /** A leitura da sessão falhou por outro motivo que não 401 (5xx, rede): não é "sem sessão". */
  falhou: boolean;
  tentarDeNovo(): void;
  entrar(email: string, senha: string): Promise<void>;
  /** Só limpa a sessão local depois de o servidor confirmar; senão, lança `ErroDaApi`. */
  sair(): Promise<void>;
} {
  const queryClient = useQueryClient();

  const consulta = useQuery({
    queryKey: CHAVE_SESSAO,
    queryFn: async (): Promise<SessaoAtual | null> => {
      const { data, error, response } = await api.GET("/api/sessao");
      // Só o 401 significa "sem sessão"; qualquer outra falha é erro de verdade.
      if (response.status === 401) return null;
      if (data === undefined) throw new ErroDaApi(response.status, error);
      return data;
    },
    staleTime: 60_000,
  });

  async function entrar(email: string, senha: string): Promise<void> {
    const { error, response } = await api.POST("/api/sessao", { body: { email, senha } });
    if (!response.ok) throw new ErroDaApi(response.status, error);
    limparDadosDaConta(queryClient);
    await queryClient.invalidateQueries({ queryKey: CHAVE_SESSAO });
  }

  async function sair(): Promise<void> {
    // Sair da tela com o cookie ainda válido faria a pessoa voltar logada sozinha. O 401 conta
    // como saída: a sessão já tinha acabado no servidor.
    const { error, response } = await api.DELETE("/api/sessao");
    if (!response.ok && response.status !== 401) throw new ErroDaApi(response.status, error);
    queryClient.setQueryData(CHAVE_SESSAO, null);
    limparDadosDaConta(queryClient);
  }

  return {
    sessao: consulta.data ?? null,
    carregando: consulta.isPending,
    falhou: consulta.isError,
    tentarDeNovo: () => void consulta.refetch(),
    entrar,
    sair,
  };
}
