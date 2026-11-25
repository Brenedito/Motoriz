# 0010. Comparação congelada e adendos

Status: Aceita

## Contexto

A comparação entre vistoria de saída e de devolução é a base de uma cobrança por avaria; checklist concluído é imutável (ADR 0004). Fatos posteriores ainda precisam poder ser registrados (spec §6.5 e §6.10).

## Decisão

A comparação (RF-06, RN-11) é uma função pura do domínio de `vistoria`: recebe dois checklists e devolve o relatório de diferenças. O resultado é gravado junto ao vínculo no encerramento e não é recalculado, nem se o modelo de checklist mudar. Fatos posteriores entram como adendo (RN-09): registro novo ligado ao checklist, com a estrutura de avaria mais o motivo, nunca alteração. Relatório e PDF mostram os adendos numa seção à parte, "registros posteriores". O PDF é gerado na requisição com WeasyPrint.

## Consequências

- O relatório salvo é estável e defensável.
- Quem consulta precisa olhar o relatório e os adendos juntos.

## Alternativas

- Recalcular a comparação a cada consulta: muda com o tempo.
- Permitir editar o checklist concluído: quebra a imutabilidade.
