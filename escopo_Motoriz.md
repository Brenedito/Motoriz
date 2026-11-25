# Escopo: Motoriz (MVP)

> Versão: 0.2 · Data: 08/11/2026 · Status: aprovado com ajustes

## 1. Visão
Locadoras e donos de frota hoje controlam veículos, contratos, vistorias e manutenções em papel, planilha e WhatsApp. Para eles, o Motoriz centraliza o ciclo operacional de cada carro: cadastro, locação, vistoria com foto e manutenção. A diferença em relação à planilha é que o sistema liga os eventos entre si. Locar muda o status do carro, devolver compara a vistoria de saída com a de chegada, e o km registrado alimenta o plano de manutenção.

## 2. Problema e contexto
- **Situação atual:** o contrato fica em papel ou PDF solto. O status do carro está na cabeça do dono. A vistoria é feita em papel ou em fotos de WhatsApp sem padrão. A manutenção é lembrada quando o carro quebra ou quando o cliente reclama.
- **Custo do problema:**
  - Avaria não comprovada vira prejuízo do dono, porque não há como provar que o dano surgiu na locação.
  - Manutenção preventiva atrasada vira corretiva, que é mais cara, e deixa o carro parado sem gerar receita.
  - Sem histórico consolidado, não dá para saber quem estava com o carro em uma data nem o que foi feito nele.
- **Por que um sistema e não planilha:** a vistoria comparativa com foto e o vencimento de manutenção por km e por tempo, cruzados com o status do carro, são inviáveis de manter em planilha com disciplina.

## 3. Objetivos e critérios de sucesso
| # | Objetivo | Como medir | Meta (premissa) |
|---|---|---|---|
| O1 | Toda locação ter registro completo | % de locações encerradas com contrato anexado + checklist de saída + checklist de devolução | ≥ 90% |
| O2 | Avarias comprováveis | % de avarias novas na devolução com foto de saída e de devolução da mesma peça | ≥ 90% |
| O3 | Manutenção preventiva em dia | % de manutenções programadas realizadas até o vencimento (tempo ou km) | ≥ 80% |
| O4 | Adoção real | Locadoras usando o sistema de forma contínua, em todas as locações, por 2 meses seguidos | ≥ 5 locadoras |

## 4. Atores e permissões
| Ator | Descrição | Pode | Não pode |
|---|---|---|---|
| Administrador da locadora | Dono ou gestor da frota (PJ ou pessoa física) | Tudo da sua conta: veículos, clientes, locações, checklists, manutenções, modelos de checklist, usuários | Ver dados de outras locadoras |
| Operador | Atendente ou vistoriador | Criar e encerrar locações, trocar veículo em locação, cadastrar clientes, preencher checklists e inspeções, registrar km e manutenções | Cadastrar, editar ou inativar veículos; criar ou alterar planos de manutenção; gerir usuários; alterar modelos de checklist; editar checklist concluído |
| Cliente locatário | Pessoa que aluga o carro | Não acessa o sistema na v1 | — |
| Suporte Motoriz | Equipe da plataforma | Criar e suspender contas de locadoras | Alterar dados operacionais das locadoras |

Cada locadora é uma conta isolada. Uma pessoa física com 3 carros e uma empresa com 150 usam o mesmo produto (premissa P1).

**Responsável por ação:** toda ação no sistema (criar, editar, concluir, cancelar, inativar, anexar, trocar veículo) registra o usuário que a executou e a data/hora (RF-20, RN-17). Exemplos: quem fez cada checklist, quem criou e quem encerrou cada locação.

## 5. Fluxos principais

### F-01 Cadastrar veículo
- **Ator:** Administrador
- **Gatilho:** carro entra na frota.
- **Passos:**
  1. Informa placa, modelo, marca, ano, cor, chassi/RENAVAM e km atual.
  2. Opcionalmente anexa documentos e fotos.
  3. Associa planos de manutenção (F-04).
- **Resultado:** veículo com status DISPONÍVEL.
- **Exceções:** placa já cadastrada na conta → bloqueia.

### F-02 Criar locação (entrega do veículo)
- **Ator:** Operador
- **Gatilho:** cliente vai retirar o carro.
- **Passos:**
  1. Seleciona um veículo DISPONÍVEL. Se houver manutenção vencida ou inspeção técnica vencida, o sistema exibe um alerta e permite seguir.
  2. Seleciona um cliente existente ou cadastra um novo. Se a CNH estiver vencida, o sistema alerta.
  3. Informa a data/hora de início e a data prevista de devolução.
  4. Anexa o contrato assinado (arquivo obrigatório).
  5. Preenche o checklist de saída (F-03).
  6. Conclui a locação.
- **Resultado:**
  - Locação ATIVA.
  - Veículo passa a LOCADO.
  - Km de saída registrado no veículo.
- **Exceções:**
  - Sem contrato ou sem checklist de saída concluído → a locação fica EM PREENCHIMENTO e o veículo não muda de status.
  - O operador abandona o preenchimento → o rascunho pode ser retomado ou descartado.

### F-03 Checklist de vistoria (saída e devolução)
- **Ator:** Operador
- **Gatilho:** etapa de F-02 ou de F-05.
- **Passos:**
  1. Registra km e nível de combustível.
  2. Para cada peça da carenagem do modelo de checklist, marca o estado: sem avaria, ou avaria com tipo (risco, amassado, quebrado, ausente) e descrição.
  3. Toda avaria exige ao menos uma foto.
  4. Registra os pneus por inspeção visual e os itens obrigatórios (estepe, macaco, chave de roda, triângulo, documento).
  5. Tira as fotos gerais obrigatórias: frente, traseira, laterais, painel com km.
  6. Conclui o checklist. Data, hora e usuário ficam gravados.
- **Resultado:** checklist imutável vinculado à locação.

### F-04 Planejar manutenção
- **Ator:** Administrador
- **Passos:**
  1. Cria um plano por veículo, por exemplo "troca de óleo a cada 10.000 km ou 6 meses".
  2. Define o gatilho: por km, por tempo, ou ambos (vence o que ocorrer primeiro).
  3. Define a antecedência do alerta, por exemplo 1.000 km ou 15 dias.
- **Resultado:** o sistema calcula o próximo vencimento a partir da última realização (ou do cadastro) e do km atual.

### F-05 Devolver veículo (encerrar locação)
- **Ator:** Operador
- **Passos:**
  1. Abre a locação ATIVA.
  2. Preenche o checklist de devolução (F-03).
  3. O sistema compara o checklist com o de saída e mostra, peça a peça:
     - avarias novas;
     - avarias pré-existentes;
     - itens obrigatórios faltantes;
     - diferença de km e de combustível.
  4. O operador confirma a comparação e escolhe o destino do veículo: DISPONÍVEL ou EM MANUTENÇÃO.
- **Resultado:**
  - Locação ENCERRADA com o relatório de diferenças salvo.
  - Km do veículo atualizado.
  - Status do veículo conforme o destino escolhido.

### F-06 Registrar manutenção
- **Ator:** Operador ou Administrador
- **Passos:**
  1. Abre uma manutenção, a partir de um plano vencido ou de forma avulsa (corretiva).
  2. Informa oficina, data e km. O orçamento pode ser anexado (opcional).
  3. Opcionalmente coloca o veículo EM MANUTENÇÃO.
  4. Ao concluir, informa os serviços executados e o valor gasto (obrigatório, apenas informativo).
- **Resultado:**
  - Manutenção CONCLUÍDA no histórico.
  - O plano recalcula o próximo vencimento.
  - O veículo volta a DISPONÍVEL se estava EM MANUTENÇÃO.

### F-07 Inspeção técnica periódica
- **Ator:** Operador ou Administrador
- **Passos:**
  1. Registra o estado das peças de desgaste: discos e pastilhas de freio, amortecedores, pneus (sulco), suspensão, correias, bateria. Cada item é marcado como bom, atenção ou trocar, com foto opcional.
  2. Itens marcados "trocar" geram sugestão de manutenção corretiva.
- **Resultado:** inspeção no histórico do veículo. A periodicidade segue um plano, como em F-04.

### F-08 Atualizar km avulso
- **Ator:** Operador
- **Gatilho:** carro em locação longa sem passar pelo pátio.
- **Passos:** registra o km com foto do painel.
- **Resultado:** os vencimentos de manutenção por km são recalculados.

### F-09 Consultar histórico
- **Ator:** Administrador ou Operador
- **Passos:**
  - Por veículo: linha do tempo com locações, checklists, avarias, manutenções, inspeções e km.
  - Por placa e data: quem estava com o carro naquele momento, considerando trocas de veículo (F-10).

### F-10 Trocar veículo durante a locação
- **Ator:** Operador
- **Gatilho:** o veículo locado quebra, sofre sinistro ou precisa de manutenção, e o cliente recebe outro carro.
- **Passos:**
  1. Na locação ATIVA, escolhe "trocar veículo" e informa o motivo.
  2. Seleciona o novo veículo, que precisa estar DISPONÍVEL (RN-01). Os alertas de RN-06 também valem.
  3. Preenche o checklist de saída do novo veículo (obrigatório).
  4. Preenche o checklist de devolução do veículo original. Se o original não estiver no pátio (guinchado, na oficina), o checklist fica **pendente** e é feito quando o carro chegar (RN-19).
  5. Define o destino do original: EM MANUTENÇÃO (padrão) ou DISPONÍVEL.
  6. Opcionalmente anexa um documento de troca (termo/aditivo assinado).
- **Resultado:**
  - A locação continua ATIVA, com o mesmo cliente e o mesmo contrato.
  - O novo veículo passa a LOCADO.
  - O original sai da locação. O vínculo dele (período, km de saída e de devolução, checklists e comparação) fica registrado na locação.
- **Exceções:**
  - Nenhum veículo disponível → a troca não é concluída.
  - Pode haver mais de uma troca na mesma locação; cada vínculo é registrado.

## 6. Requisitos funcionais
| ID | Requisito | Ator | Prioridade | Critério de aceite |
|---|---|---|---|---|
| RF-01 | Cadastrar, editar e inativar veículos | Admin | Essencial | Veículo inativo não aparece para locação, mas o histórico permanece |
| RF-02 | Exibir status atual de cada veículo (DISPONÍVEL, LOCADO, EM MANUTENÇÃO, INATIVO) | Todos | Essencial | Status muda automaticamente nos eventos de RN-02 a RN-05 |
| RF-03 | Cadastrar clientes locatários (PF e PJ) com CPF/CNPJ, contato, endereço, CNH (número, categoria, validade) e foto da CNH | Operador | Essencial | Não permite CPF/CNPJ duplicado na mesma conta |
| RF-04 | Criar locação com veículo, cliente, datas e contrato assinado anexado | Operador | Essencial | Não conclui sem contrato e sem checklist de saída |
| RF-05 | Checklist de saída e de devolução com peças da carenagem, itens obrigatórios, pneus visuais, km, combustível e fotos | Operador | Essencial | Avaria sem foto impede concluir o checklist |
| RF-06 | Comparar automaticamente o checklist de devolução com o de saída e gerar relatório de diferenças | Sistema | Essencial | Toda peça com estado diferente aparece com fotos de saída e devolução lado a lado |
| RF-07 | Encerrar locação pelo checklist de devolução, com escolha do destino do veículo | Operador | Essencial | Locação encerrada não pode ser reaberta |
| RF-08 | Modelos de checklist configuráveis pela locadora: incluir ou remover peças e itens; o modelo padrão vem pronto | Admin | Essencial | Alterar o modelo não altera checklists já concluídos |
| RF-09 | Planos de manutenção por km, por tempo ou ambos, com antecedência de alerta | Admin | Essencial | Vencimento recalculado a cada novo km e a cada manutenção concluída |
| RF-10 | Registrar manutenção (preventiva ou corretiva) com oficina, data, km, serviços, valor gasto e orçamento anexado (opcional) | Operador/Admin | Essencial | Não conclui sem valor; fica no histórico do veículo com o anexo, se houver |
| RF-11 | Inspeção técnica periódica de peças de desgaste | Operador/Admin | Essencial | Item "trocar" gera sugestão de manutenção |
| RF-12 | Registro de km avulso com foto do painel | Operador | Essencial | Km menor que o último registrado é bloqueado |
| RF-13 | Painel de alertas (ver seção 11) | Todos | Essencial | Cada alerta leva ao registro correspondente |
| RF-14 | Histórico do veículo em linha do tempo | Todos | Essencial | Mostra todos os eventos em ordem cronológica com anexos |
| RF-15 | Consulta "quem estava com o veículo" por placa e data/hora | Admin/Operador | Essencial | Retorna a locação e o cliente vigentes no momento informado, inclusive em locações com troca de veículo |
| RF-16 | Gestão de usuários da conta (Admin e Operador) | Admin | Essencial | Operador não acessa as funções restritas da seção 4 |
| RF-17 | Vencimentos de documentos do veículo (licenciamento, seguro) com alerta | Admin | Futuro | — |
| RF-18 | Exportar relatório da comparação de vistoria (para enviar ao cliente ou anexar a cobrança feita fora do sistema) | Operador | Essencial | Gera documento com dados da locação, diferenças, fotos e responsáveis pelos checklists |
| RF-19 | Checklist operável no celular, no pátio, com fotos tiradas pela câmera | Operador | Essencial | Checklist completo de um carro sem avarias feito em ≤ 5 minutos (meta a validar) |
| RF-20 | Registrar o responsável (usuário) e a data/hora de toda ação no sistema, com trilha consultável por registro | Sistema | Essencial | Todo veículo, locação, checklist, manutenção, inspeção, leitura de km e cliente mostra quem criou, quem alterou, o quê e quando |
| RF-21 | Trocar veículo em locação ativa, mantendo o registro do veículo original (F-10) | Operador | Essencial | A locação lista todos os veículos vinculados, com período e checklists de cada um |

## 7. Regras de negócio
| ID | Regra | Exceções |
|---|---|---|
| RN-01 | Só veículo DISPONÍVEL pode ser locado | — |
| RN-02 | Locação concluída (contrato + checklist de saída) → veículo LOCADO | — |
| RN-03 | Checklist de devolução concluído → locação ENCERRADA e veículo DISPONÍVEL ou EM MANUTENÇÃO, conforme escolha do operador | — |
| RN-04 | Veículo LOCADO não pode ir para EM MANUTENÇÃO nem INATIVO sem antes sair da locação, seja pelo encerramento ou pela troca (RN-18) | — |
| RN-05 | Manutenção concluída de veículo EM MANUTENÇÃO → DISPONÍVEL | Se houver outra manutenção aberta no mesmo veículo, continua EM MANUTENÇÃO |
| RN-06 | Manutenção vencida, inspeção vencida ou CNH vencida geram alerta na criação da locação, mas não bloqueiam | — |
| RN-07 | Plano por km e tempo vence no que ocorrer primeiro; o próximo ciclo conta a partir da data e do km da última realização | Sem realização anterior: conta a partir do cadastro do plano |
| RN-08 | O km registrado nunca pode ser menor que o último km do veículo | Correção de erro de digitação só pelo Admin, com justificativa registrada |
| RN-09 | Checklist concluído é imutável; correções entram como adendo com data, usuário e motivo | — |
| RN-10 | Toda avaria registrada em checklist exige no mínimo 1 foto | — |
| RN-11 | A comparação usa o checklist de saída do mesmo veículo na mesma locação; avaria presente na saída é pré-existente, nunca nova | Em locação com troca, cada veículo é comparado com o seu próprio checklist de saída |
| RN-12 | Um veículo só pode estar vinculado a uma locação ATIVA por vez; uma locação ATIVA tem exatamente um veículo vigente | — |
| RN-13 | Locação ATIVA com data prevista de devolução ultrapassada gera alerta de atraso | — |
| RN-14 | Veículo, cliente ou locação com histórico não podem ser excluídos, apenas inativados ou cancelados | Rascunho de locação pode ser descartado |
| RN-15 | Cancelar locação ATIVA (erro de cadastro) exige justificativa e devolve o veículo a DISPONÍVEL; a locação fica CANCELADA no histórico | Só Admin |
| RN-16 | Locação ATIVA sem registro de km há mais de X dias gera alerta de km desatualizado | X configurável pela locadora (padrão 7 dias, premissa P3) |
| RN-17 | Toda ação registra o usuário responsável e a data/hora; esse registro não pode ser editado nem excluído por ninguém | — |
| RN-18 | Troca de veículo: o novo veículo vira LOCADO e o original sai da locação para o destino escolhido; contrato e cliente continuam os mesmos | — |
| RN-19 | O checklist de devolução do veículo original numa troca pode ficar pendente; enquanto pendente, o original não pode voltar a DISPONÍVEL e o sistema mantém um alerta | — |

## 8. Entidades e dados (visão de negócio)

**Locadora (conta).** Nome, documento (CPF ou CNPJ), contato, usuários.
- Relações: contém todas as demais entidades.
- Estados: ativa ou suspensa.

**Usuário.** Nome, e-mail, papel (Admin ou Operador).
- Relações: pertence a uma locadora.
- Estados: ativo ou inativo.
- Não pode ser perdido: o autor de cada checklist e manutenção.

**Veículo.** Placa, marca, modelo, ano, cor, chassi, RENAVAM, km atual, fotos, documentos.
- Estados: DISPONÍVEL, LOCADO, EM MANUTENÇÃO, INATIVO.
- Não pode ser perdido: o histórico completo.

**Cliente locatário.** Tipo (PF ou PJ), nome, CPF/CNPJ, contato, endereço, CNH (número, categoria, validade, foto).
- Relações: tem N locações.
- Estados: ativo ou inativo.

**Locação.**
- Dados: cliente, datas de início e prevista de devolução, data real de devolução, contrato anexado, um ou mais vínculos de veículo.
- Estados: EM PREENCHIMENTO, ATIVA, ENCERRADA, CANCELADA.
- Não pode ser perdido: o contrato, os vínculos, os checklists e as fotos.

**Vínculo de veículo (na locação).** Veículo, período (início e fim), km de saída e de devolução, checklist de saída, checklist de devolução (ou pendente), relatório de comparação, motivo de saída (encerramento ou troca), documento de troca opcional. Uma locação sem troca tem um único vínculo.

**Modelo de checklist.** Lista de peças da carenagem, itens obrigatórios e fotos gerais exigidas. Um modelo padrão vem pronto.
- Lista padrão (premissa P4): capô; para-choque dianteiro e traseiro; para-lamas DE/DD/TE/TD; portas DE/DD/TE/TD; tampa traseira/porta-malas; teto; retrovisores E/D; faróis e lanternas; para-brisa e vidros; rodas.

**Checklist (vistoria).**
- Dados: tipo (saída ou devolução), locação, km, combustível, estado de cada peça, avarias com tipo, descrição e fotos, itens obrigatórios, pneus, fotos gerais, usuário, data/hora, adendos.
- Estados: em preenchimento, concluído (imutável).

**Plano de manutenção.**
- Dados: veículo, descrição, intervalo em km e/ou meses, antecedência do alerta, última realização, próximo vencimento calculado.
- Estados: ativo ou inativo.

**Manutenção.**
- Dados: veículo, tipo (preventiva, vinculada a um plano, ou corretiva), oficina, data, km, serviços executados, valor gasto (informativo), orçamento anexado (opcional).
- Estados: ABERTA, EM ANDAMENTO, CONCLUÍDA, CANCELADA.

**Inspeção técnica.**
- Dados: veículo, data, km, itens de desgaste com estado e foto opcional, usuário.

**Leitura de km.**
- Dados: veículo, valor, origem (checklist, manutenção ou avulsa), foto, usuário, data.
- É a base do cálculo de vencimento por km.

**Registro de ação (trilha de responsáveis).**
- Dados: usuário, data/hora, tipo de ação, registro afetado e, em alterações, o valor anterior e o novo.
- É imutável (RN-17) e não pode ser perdido.

## 9. Casos de borda e tratamento de erros
| Situação | Comportamento esperado |
|---|---|
| Km de devolução menor que o de saída | Bloqueia (RN-08) |
| Operador perde a conexão no meio do checklist com fotos | O preenchimento não pode ser perdido; retoma de onde parou |
| Cliente devolve com combustível menor ou item obrigatório faltando | Aparece na comparação como diferença; nenhuma ação financeira no sistema |
| Avaria nova encontrada dias depois da devolução | Adendo ao checklist de devolução (RN-09), marcado como registro posterior |
| Carro quebra durante a locação e é trocado por outro | Troca na mesma locação (F-10, RN-18) |
| Na troca, o carro original está guinchado e não chega ao pátio | Checklist de devolução do original fica pendente com alerta; original não volta a DISPONÍVEL até concluir (RN-19) |
| Usuário que fez um checklist ou uma locação é desativado | Continua aparecendo como responsável nos registros que fez (RN-17) |
| Locação longa, carro nunca volta ao pátio | Km avulso (F-08) e alerta de km desatualizado (RN-16) |
| Placa trocada (Mercosul) ou corrigida | Admin edita; histórico preservado, com registro da alteração |
| Cliente com CNH vencida | Alerta e permite seguir (RN-06) |
| Dois operadores tentam locar o mesmo carro ao mesmo tempo | Só um conclui; o outro recebe aviso de que o veículo não está mais disponível (RN-12) |
| Manutenção aberta enquanto o veículo está LOCADO (agendamento futuro) | Permitido como ABERTA, sem mudar o status do veículo |
| Arquivo de contrato ilegível ou errado | Admin substitui o anexo; a versão anterior fica preservada |

## 10. Integrações e dependências de negócio
Nenhuma integração externa na v1. Contrato, assinatura e cobrança acontecem fora do Motoriz, que só recebe o contrato assinado como anexo. Dependência operacional: o operador ter celular com câmera no momento da entrega e da devolução.

## 11. Notificações e comunicação
Na v1, os alertas aparecem dentro do sistema, em um painel e em indicadores por veículo. Tipos de alerta:
- Manutenção próxima do vencimento ou vencida (por km ou tempo).
- Inspeção técnica vencida.
- Devolução atrasada (RN-13).
- Km desatualizado em locação ativa (RN-16).
- CNH de cliente vencida ou a vencer, no momento da locação.
- Checklist de devolução pendente de veículo trocado (RN-19).

Notificação externa (e-mail, WhatsApp, push) fica para o futuro.

## 12. Relatórios e métricas
Indicadores e relatórios da v1:
- Frota por status, em tempo real.
- Taxa de ocupação por veículo e geral (dias locado ÷ dias ativos no período).
- Manutenções vencidas e próximas.
- Histórico por veículo.
- Avarias por cliente (Desejável): quantas avarias novas cada cliente já gerou.
- Dias parado em manutenção por veículo (Desejável).
- Gasto com manutenção por veículo e por período, somando os valores informados (Desejável).
- Ações por usuário: quem fez quais locações, checklists e manutenções no período (Desejável; a trilha em si é Essencial, RF-20).

Sem relatórios financeiros de receita ou cobrança (seção 14).

## 13. Restrições, conformidade e volume
- **LGPD.** O sistema guarda dados pessoais de terceiros: CPF, CNH com foto, endereço e contrato. A locadora é a controladora e o Motoriz é o operador. São necessários:
  - controle de acesso por conta;
  - registro de quem acessou ou alterou;
  - exclusão ou anonimização sob pedido do titular, respeitando a retenção sugerida abaixo.
- **Retenção sugerida (P8, validar com jurídico em PA-04).**
  - Contrato, checklists, fotos e dados do cliente ligados a uma locação: guardados por **5 anos após o encerramento**. Esse prazo cobre os prazos de cobrança e de reparação civil e de consumo mais comuns.
  - Depois disso, os dados pessoais do cliente são anonimizados. O histórico operacional do veículo (avarias, km, manutenções) continua guardado.
  - Cliente cadastrado sem nenhuma locação: excluído sob pedido, a qualquer momento.
  - Registros de ação (RN-17): mesmo prazo do registro a que se referem.
- **Valor probatório.** Checklist imutável, com data, hora, usuário e fotos, é o ativo central do produto. Qualquer edição posterior precisa ser rastreável.
- **Volume (premissa P2).**
  - Frotas de 1 a ~200 veículos por conta.
  - Cada checklist tem 10 a 40 fotos.
  - Locação diária pode gerar dezenas de checklists por dia em uma frota média; o volume de fotos é o principal fator de crescimento de dados.

## 14. Fora do escopo (v1)
- Cobrança, pagamentos, caução, valores de locação, inadimplência, financeiro em geral. A única exceção é o valor gasto em manutenção, que é apenas informativo.
- Vencimento de documentos do veículo (RF-17).
- Multas de trânsito (gestão, indicação de condutor, cobrança).
- Geração de contrato e assinatura eletrônica dentro do sistema.
- Reservas e agenda futura de locações.
- Portal ou app para o cliente locatário.
- Rastreamento/telemetria (GPS, km automático).
- Integrações (Detran, seguradoras, oficinas, nota fiscal).
- Notificações externas (e-mail, WhatsApp, push).
- Estoque de peças.

## 15. Roadmap sugerido
- **v1:** seções 5 e 6 com prioridade Essencial. Prova a hipótese de que locadoras adotam o registro digital completo com vistoria comparativa e manutenção programada.
- **v2:**
  - Financeiro básico: valor da locação, recebimentos, caução; cruzar com o gasto de manutenção já registrado na v1 para chegar ao resultado por veículo.
  - Vencimento de documentos do veículo (RF-17).
  - Notificações por WhatsApp.
  - Relatório de vistoria enviado ao cliente.
  - Itens Desejáveis da v1.
- **Futuro:**
  - Reservas.
  - Multas com indicação de condutor.
  - Assinatura eletrônica.
  - Portal do locatário.
  - Telemetria.
  - Indicadores de rentabilidade por carro.

## 16. Riscos
| Risco | Probabilidade | Impacto | Mitigação |
|---|---|---|---|
| Sem financeiro, o dono continua precisando da planilha de recebimentos e enxerga o Motoriz como trabalho extra | Alta | Alto | Validar a v1 com locadoras cuja dor principal é avaria e manutenção; financeiro como primeiro item da v2 |
| Operador não preenche checklist completo no pátio (pressa, cliente esperando) | Alta | Alto | RF-19 (checklist rápido no celular); peças sem avaria marcadas em lote; meta de tempo validada em campo |
| Atender locadora diária e locação por aplicativo dilui o produto | Média | Médio | Fluxo único na v1 (a diferença real é só a frequência de km); medir uso por segmento e decidir o foco na v2 |
| Km desatualizado em locações longas torna inútil a manutenção por km | Alta (segmento app) | Médio | F-08 + RN-16; considerar telemetria no futuro |
| Volume de fotos alto em frotas grandes | Média | Médio | Considerar no planejamento; fora deste escopo decidir como |
| Dados de clientes (CNH, CPF) vazados | Baixa | Alto | Requisitos de LGPD da seção 13 |

## 17. Premissas
| ID | Premissa | Se for falsa |
|---|---|---|
| P1 | Cada locadora é uma conta isolada, com papéis Admin e Operador | Se só houver um usuário por conta, a gestão de usuários (RF-16) sai da v1 |
| P2 | Frotas de 1 a ~200 veículos | Frotas maiores exigem filiais/pátios e mais papéis |
| P3 | Alerta de km desatualizado padrão em 7 dias | Ajuste de configuração apenas |
| P4 | Lista padrão de peças da carenagem conforme a seção 8 | Ajuste do modelo padrão |
| P5 | Concluir a locação exige contrato e checklist de saída | Se puder concluir sem checklist, a comparação de devolução fica sem base |
| P6 | O destino do veículo após a devolução (DISPONÍVEL ou EM MANUTENÇÃO) é escolhido pelo operador | Se for automático (ex.: avaria nova → manutenção), muda RN-03 |
| P7 | Os mesmos fluxos servem para locação diária e para locação a motorista de aplicativo | Se o segmento app exigir algo próprio, entra no escopo |
| P8 | Retenção de 5 anos após o encerramento da locação, com anonimização depois (seção 13) | Se o jurídico definir outro prazo, ajusta-se apenas a regra de retenção |
| P9 | Na troca de veículo, o contrato original continua válido; o documento de troca é opcional | Se a locadora precisar de aditivo assinado sempre, o anexo vira obrigatório em F-10 |

## 18. Perguntas em aberto
| ID | Pergunta | Impacto no escopo | Quem responde |
|---|---|---|---|
| PA-04 | O prazo de retenção sugerido (5 anos após o encerramento, depois anonimização) atende às obrigações legais da locadora? | LGPD e retenção (P8) | Jurídico |

**Resolvidas na v0.2:**
- **PA-01:** troca de veículo na mesma locação, mantendo o registro do original → F-10, RF-21, RN-18, RN-19.
- **PA-02:** só o Admin cadastra veículos e planos de manutenção → seção 4.
- **PA-03:** manutenção registra o valor gasto (obrigatório), com orçamento opcional → RF-10.
- **PA-05:** uso contínuo por 2 meses de pelo menos 5 locadoras → O4.

## 19. Preferências declaradas (não vinculantes)
Nenhuma tecnologia mencionada.

## 20. Glossário
- **Locadora:** conta cliente do Motoriz; empresa ou pessoa física com frota.
- **Locatário / cliente:** quem aluga o veículo da locadora.
- **Checklist de saída / devolução:** vistoria do veículo na entrega ao locatário e no retorno.
- **Carenagem:** peças externas da carroceria (capô, portas, para-choques etc.).
- **Avaria nova:** dano presente na devolução e ausente no checklist de saída da mesma locação.
- **Inspeção técnica:** verificação periódica de peças de desgaste (freios, amortecedores, pneus etc.), separada da vistoria de locação.
- **Plano de manutenção:** regra recorrente de manutenção preventiva por km e/ou tempo.
- **Adendo:** registro posterior anexado a um checklist concluído, sem alterá-lo.

---

## Anexo A: Escopo em uma página

**Visão:** o Motoriz centraliza o ciclo operacional da frota de locadoras e donos de carros: veículos, locações com contrato, vistoria comparativa com foto e manutenção programada.

**Problema:** avarias sem prova, manutenção preventiva esquecida, status e histórico dos carros espalhados em papel, planilha e WhatsApp.

**Atores:** Administrador da locadora, Operador, Suporte Motoriz. O locatário não acessa. Só o Admin cadastra veículos e planos de manutenção. Toda ação registra o usuário responsável.

**Essencial v1:**
- Veículos com status automático: DISPONÍVEL, LOCADO, EM MANUTENÇÃO, INATIVO.
- Clientes locatários com CNH.
- Locação com contrato assinado anexado e checklist de saída obrigatório; ao concluir, o veículo vira LOCADO.
- Checklist com peças da carenagem, itens obrigatórios, pneus, km, combustível; foto obrigatória por avaria; operável no celular.
- Modelos de checklist configuráveis pela locadora.
- Devolução com comparação automática de saída × devolução (avarias novas, faltas, km, combustível) que encerra a locação; relatório exportável.
- Troca de veículo na mesma locação, preservando o registro do original.
- Planos de manutenção por km e/ou tempo (o que vier primeiro); histórico com valor gasto e orçamento opcional.
- Consulta de quem estava com o veículo em uma data.
- Trilha de responsável e data/hora em toda ação.
- Inspeção técnica periódica de peças de desgaste, separada do checklist.
- Km avulso para locações longas.
- Painel de alertas: manutenção, devolução atrasada, km desatualizado, CNH vencida.
- Histórico do veículo em linha do tempo.

**Regras críticas:**
- Só locar veículo DISPONÍVEL.
- Uma locação ativa por veículo.
- Checklist concluído é imutável (só adendo).
- Km nunca diminui.
- Manutenção vencida alerta, mas não bloqueia.
- Registro de responsável não pode ser editado nem excluído.

**Fora da v1:** cobrança, caução e valores de locação (só o gasto de manutenção é registrado, como informação), vencimento de documentos do veículo, multas, reservas, assinatura eletrônica, portal do cliente, integrações, notificações externas, telemetria.

**Sucesso:** ≥ 5 locadoras usando de forma contínua por 2 meses; ≥ 90% das locações com contrato + checklists completos; ≥ 80% das preventivas feitas no prazo.

**Premissas-chave:**
- Contas isoladas com Admin e Operador.
- Frotas de até ~200 carros.
- Mesmo fluxo para locação diária e para app.
- Retenção de 5 anos após a locação.

**Pergunta em aberto:** validar o prazo de retenção com o jurídico.
