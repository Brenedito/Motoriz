# 0004. Auditoria imutável por gatilho e permissão

Status: Aceita

## Contexto

Toda ação relevante deve ser registrada (RN-17) e o registro, bem como o checklist concluído, não pode ser alterado (spec §6.5). Garantir isso só na aplicação não resiste a um defeito ou a acesso direto ao banco.

## Decisão

A tabela `registro_acao` guarda conta, usuário, data/hora do servidor, ação, entidade, id e valores anterior e novo em JSON. Cada caso de uso grava seus registros na mesma transação da mudança. A imutabilidade é do banco: o usuário MySQL da aplicação (`motoriz_app`) tem apenas `INSERT, SELECT` em `registro_acao`, e gatilhos `BEFORE UPDATE/DELETE` com `SIGNAL` bloqueiam alteração de `registro_acao` e de checklist (itens e fotos) concluído. As migrações rodam com outro usuário (`motoriz_migracao`), com privilégios de DDL. Anexos nunca são sobrescritos.

## Consequências

- A trilha tem valor probatório mesmo diante de erro da aplicação.
- Testes de integração precisam provar que UPDATE e DELETE falham.
- Corrigir um dado concluído exige um registro novo (adendo, correção), nunca edição.

## Alternativas

- Imutabilidade só na aplicação: frágil.
- Armazenamento externo de auditoria: complexidade desnecessária no MVP.
