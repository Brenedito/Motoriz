import createClient from "openapi-fetch";
import type { paths } from "./esquema";

// Em produção a origem é a mesma da página (baseUrl "" na prática); usar a origem explícita
// também deixa o cliente utilizável fora do navegador real (testes em jsdom + msw).
export const api = createClient<paths>({
  baseUrl: globalThis.location?.origin ?? "",
  credentials: "include",
  // Resolve o fetch a cada chamada (o openapi-fetch o capturaria na criação do cliente),
  // para que o msw dos testes consiga interceptar.
  fetch: (requisicao) => globalThis.fetch(requisicao),
  // Exigido pela API nas requisições que alteram dados; inofensivo nos GETs.
  headers: { "X-Motoriz": "1" },
});

const MENSAGEM_PADRAO = "Não foi possível concluir a operação. Tente novamente.";

/** Extrai o texto de `{"erro": "..."}` (corpo de erro de toda a API). */
export function mensagemDeErro(erro: unknown): string {
  if (typeof erro === "object" && erro !== null && "erro" in erro) {
    const texto = (erro as { erro: unknown }).erro;
    if (typeof texto === "string" && texto) return texto;
  }
  return MENSAGEM_PADRAO;
}

/** Erro de uma chamada à API, com o status HTTP para quem precisar distinguir. */
export class ErroDaApi extends Error {
  readonly status: number;
  constructor(status: number, erro: unknown) {
    super(mensagemDeErro(erro));
    this.name = "ErroDaApi";
    this.status = status;
  }
}
