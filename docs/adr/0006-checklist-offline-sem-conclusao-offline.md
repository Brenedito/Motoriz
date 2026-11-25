# 0006. Checklist offline sem conclusão offline

Status: Aceita

## Contexto

O vistoriador preenche o checklist no pátio, onde a conexão pode falhar (spec §6.6). Conflitos como dois operadores locando o mesmo carro precisam aparecer na hora.

## Decisão

O frontend é uma PWA. O modo offline cobre só o preenchimento do checklist e o km avulso. Rascunho e fotos (como `Blob`) ficam no IndexedDB (Dexie). O cliente gera os UUIDs de checklist, avarias e fotos, e todo comando é idempotente por UUID. Cada foto sobe quando houver conexão (URL assinada, `PUT`, confirmação); o rascunho sincroniza por `PUT /checklists/{id}`. Concluir exige conexão (decisão do autor): concluir checklist, ativar locação, confirmar a devolução e trocar veículo são comandos online, aceitos só com todas as fotos exigidas confirmadas. A hora oficial é a do servidor; a hora da foto vai à parte em `capturada_em`.

## Consequências

- Nenhum dado de checklist se perde sem rede.
- O servidor decide conflitos na hora; sem conexão a tela mostra o que falta.

## Alternativas

- Concluir offline e reconciliar depois: conflitos tardios e hora não confiável.
- Sem modo offline: perde trabalho em pátios sem sinal.
