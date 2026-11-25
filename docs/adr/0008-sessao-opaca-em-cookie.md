# 0008. Sessão opaca em cookie

Status: Aceita

## Contexto

A autenticação usa e-mail e senha próprios. Desativar um usuário ou suspender uma locadora deve valer na hora (spec §6.8).

## Decisão

Senhas com hash Argon2id. A sessão é um identificador opaco guardado no banco e enviado em cookie `HttpOnly; Secure; SameSite=Strict`, com duração absoluta de 14 dias. Desativar o usuário invalida as sessões imediatamente. A proteção CSRF combina `SameSite=Strict` com um cabeçalho próprio (`X-Motoriz: 1`) exigido em requisições que alteram dados. Permissões por papel (Admin, Operador) são verificadas no caso de uso, não só na rota; Suporte Motoriz é um papel de plataforma sem acesso a dados operacionais.

## Consequências

- Revogação imediata e superfície simples.
- Cada requisição consulta a sessão no banco.

## Alternativas

- JWT: sem estado, mas difícil de revogar e mais complexo de fazer bem.
- Token em `localStorage`: exposto a XSS.
