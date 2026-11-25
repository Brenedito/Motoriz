# 0007. Fotos por URL assinada com SHA-256

Status: Aceita

## Contexto

Fotos de vistoria são prova em caso de avaria; precisam de integridade verificável e de acesso controlado por conta (spec §6.7).

## Decisão

Armazenamento compatível com S3 (MinIO em desenvolvimento). A API gera uma URL assinada de `PUT` de validade curta, com chave `conta/<conta_id>/<arquivo_id>`; o cliente envia e confirma; a API verifica tamanho e tipo, calcula o SHA-256 lendo o objeto e grava o metadado. O download é sempre por URL assinada gerada depois de checar conta e permissão (e auditar, se for dado pessoal). O bucket é privado.

## Consequências

- O hash sustenta o valor probatório do checklist.
- A API não trafega os bytes no envio.
- Depende de um serviço de armazenamento no ambiente.

## Alternativas

- Enviar o arquivo pela API: mais simples, mais carga e memória no servidor.
- Bucket público com nomes aleatórios: sem controle de acesso nem auditoria.
