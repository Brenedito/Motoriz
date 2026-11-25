# 0003. Invariantes no banco com coluna gerada

Status: Aceita

## Contexto

Um veículo só pode estar em uma locação ativa por vez (RN-12). Dois operadores podem tentar locar o mesmo carro ao mesmo tempo (spec §6.4). O MySQL não tem índice único parcial.

## Decisão

A tabela `vinculo_veiculo` tem a coluna gerada `veiculo_vigente = IF(fim IS NULL, veiculo_id, NULL)` com índice único: como `NULL` não colide em índice único, só o vínculo em aberto conta. Quem perde a disputa recebe o erro "veículo não está mais disponível". O caso de uso também faz `SELECT ... FOR UPDATE` no veículo antes de mudar o status. Edições de cadastro (veículo, cliente) usam a coluna `versao` para controle otimista.

## Consequências

- A regra vale mesmo que a aplicação tenha um defeito ou haja concorrência.
- O erro de violação de unicidade precisa ser traduzido em erro de domínio.

## Alternativas

- Checar só na aplicação: sujeito a corrida entre requisições.
- Tabela auxiliar com unicidade manual: mais código para o mesmo efeito.
