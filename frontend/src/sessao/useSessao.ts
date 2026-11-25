import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api, ErroDaApi } from "../api/cliente";
import type { components } from "../api/esquema";

export type SessaoAtual = components["schemas"]["SessaoAtual"];

export const CHAVE_SESSAO = ["sessao"] as const;

export function useSessao(): {
  sessao: SessaoAtual | null;
  carregando: boolean;
  entrar(email: string, senha: string): Promise<void>;
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
    await queryClient.invalidateQueries({ queryKey: CHAVE_SESSAO });
  }

  async function sair(): Promise<void> {
    await api.DELETE("/api/sessao");
    queryClient.setQueryData(CHAVE_SESSAO, null);
    queryClient.removeQueries({ predicate: (q) => q.queryKey[0] !== CHAVE_SESSAO[0] });
  }

  return { sessao: consulta.data ?? null, carregando: consulta.isPending, entrar, sair };
}
