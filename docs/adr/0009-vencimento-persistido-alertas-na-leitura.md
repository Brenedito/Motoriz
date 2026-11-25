# 0009. Vencimento persistido e alertas na leitura

Status: Aceita

## Contexto

Manutenção vence por km e por tempo, e o painel de alertas precisa ser barato e correto (spec §6.9). O volume é de até cerca de 200 veículos por conta.

## Decisão

O vencimento de cada plano (próximo km e próxima data) é calculado no domínio de `manutencao` e persistido sempre que a base muda: nova leitura de km, manutenção concluída, plano alterado. `frota` avisa `manutencao` pela fachada ao registrar km. Os alertas são calculados na leitura, comparando os valores persistidos com a data de hoje e o km atual.

## Consequências

- Sem agendador nem tarefas em segundo plano.
- Consultas de alerta simples e rápidas nesse volume.
- É preciso recalcular o vencimento em todo evento que mude a base, inclusive a correção de km.

## Alternativas

- Calcular tudo na leitura: refaz a regra a cada consulta.
- Agendador que gera alertas: infraestrutura extra sem ganho nesse volume.
