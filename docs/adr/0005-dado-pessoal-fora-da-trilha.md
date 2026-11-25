# 0005. Dado pessoal fora da trilha de auditoria

Status: Aceita

## Contexto

A trilha de auditoria é imutável (ADR 0004), mas a LGPD exige anonimizar o cliente quando cabível (spec §6.5 e §6.12). Se a trilha guardasse nome ou CPF, a anonimização esbarraria nela.

## Decisão

Para campos pessoais do cliente (nome, CPF/CNPJ, contato, endereço, CNH), o registro guarda só qual campo mudou, nunca os valores. Também se registra a leitura de dado pessoal sensível (detalhe de cliente, download de foto de CNH ou de contrato), atendendo ao "registro de quem acessou" da seção 13 do escopo.

## Consequências

- A anonimização não precisa alterar a trilha.
- A trilha não reconstrói o valor antigo de um dado pessoal; o histórico de valores pessoais não existe.

## Alternativas

- Cifrar os valores com chave por cliente e descartar a chave na anonimização: mais elegante, mais trabalho; fica como evolução.
- Guardar os valores na trilha: incompatível com a anonimização.
