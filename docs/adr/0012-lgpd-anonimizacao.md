# 0012. LGPD: anonimização de cliente

Status: Aceita

## Contexto

O sistema guarda dado pessoal de clientes (CPF/CNPJ, contato, endereço, CNH) e precisa atender à LGPD sem perder o histórico operacional (spec §6.12 e seção 13 do escopo).

## Decisão

O caso de uso "anonimizar cliente" (Admin) substitui os dados pessoais por marcadores, apaga a foto da CNH do armazenamento e mantém o histórico operacional. Cliente sem locação pode ser excluído. Como a trilha de auditoria não guarda valores pessoais (ADR 0005), a anonimização não toca em registros imutáveis. A anonimização automática após 5 anos não entra na v1, pois nenhum dado terá essa idade; o caso de uso existe e pode ser agendado depois.

## Consequências

- Locações e vistorias continuam consultáveis, sem identificar a pessoa.
- A anonimização é irreversível.

## Alternativas

- Apagar o cliente e suas locações: destrói o histórico e a prova.
- Anonimização automática agendada já na v1: sem dado que a justifique.
