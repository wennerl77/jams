---
name: github-issues
description: >-
  Use esta skill sempre que o usuário solicitar a criação, planejamento, divisão
  ou registro de uma ou mais issues no GitHub para o projeto Mosaico. Define
  padronização de títulos, responsabilidade única, decomposição em sub-issues,
  atribuição obrigatória (backend: @wennerl77, frontend: @AntonnyCaldeiraSilva),
  labels de tipo, área, prioridade e domínio, milestones automáticas para épicos (>3 issues),
  escopo de arquivos/domínios afetados, contratos reais e critérios de aceite sem emojis.
---

# Skill: Criação e Gestão de Issues no GitHub (Mosaico)

Esta skill estabelece o processo canônico e as diretrizes obrigatórias para planejar, estruturar e criar issues no repositório GitHub do projeto **Mosaico** (`Mosaico-br/Mosaico`).

---

## 1. Princípios Fundamentais e Regras Inegociáveis

### 1.1. Responsabilidade Única (Single Responsibility Principle)
- Toda issue **deve possuir apenas uma única responsabilidade clara e indivisível**.
- **Nunca infle uma issue** agrupando múltiplos objetivos ou fluxos em um só ticket.
- *Exemplo de Violação:* Uma issue de "Autenticação" contendo cadastro, login, logout, recuperação de senha e rotação de token JWT.
- *Forma Correta:* Quebrar em issues atômicas e desacopladas:
  1. Login e geração de token JWT
  2. Registro de novo usuário (Logon)
  3. Logout e invalidação/blacklist de sessão
  4. Fluxo de recuperação de senha via e-mail

### 1.2. Desacoplamento & Decomposição
- Mantenha cada issue o mais independente possível de outras tarefas.
- Sempre que houver dúvida entre criar 1 issue ampla ou 3 issues menores, **prefira sempre quebrar em issues menores**.
- Separe estritamente tarefas de **Backend** e tarefas de **Frontend** em issues distintas. Não misture implementação de API e telas na mesma issue.

### 1.3. Regra dos 3+ e Milestones Obrigatórias
- Se um tópico, épico ou funcionalidade demandar **mais de 3 issues**:
  1. **Crie obrigatoriamente uma Milestone no GitHub** para agrupar o conjunto.
  2. Defina na descrição da Milestone (e nas issues) a **ordem cronológica de execução** e o grafo de dependências entre elas.
  3. Associe todas as issues relacionadas a essa Milestone.

### 1.4. Atribuição Obrigatória (Assignees) & Menções
Toda issue deve ser atribuída à pessoa responsável pelo domínio e marcada no corpo da issue:
- **Issues de Backend (Spring Boot API):**
  - **Assignee:** `wennerl77` (Wenner Lucas)
  - **Menção obrigatória no corpo:** `@wennerl77`
- **Issues de Frontend (Vue 3 / Capacitor):**
  - **Assignee:** `AntonnyCaldeiraSilva` (Antonny Silva)
  - **Menção obrigatória no corpo:** `@AntonnyCaldeiraSilva`
- Se o autor explicitamente indicar outro colaborador ou se a tarefa for delegada a uma pessoa específica, atribua a ela respeitando a convenção.

### 1.5. Proibição Estrita de Emojis
- **Não utilize emojis** no título ou na descrição da issue.
- Essa restrição alinha-se às diretrizes visuais do Mosaico (evitar poluição, inconsistência entre plataformas e manter a sobriedade técnica). Use marcadores Markdown limpos (`-`, `*`, `1.`, `[ ]`).

---

## 2. Padrão de Nomenclatura do Título

O título da issue deve ser conciso, direto e seguir rigorosamente a convenção de prefixo por tipo:

```text
[TIPO] - <título objetivo e curto, sem detalhamento>
```

### Prefixos Válidos:
- `[FEAT]` - Nova funcionalidade ou endpoint
- `[FIX]` - Correção de defeito ou bug
- `[CHORE]` - Tarefas de manutenção, refatoração de build ou ajustes gerais
- `[DOCS]` - Atualização ou criação de documentação
- `[REFACTOR]` - Refatoração de código sem alteração comportamental
- `[TEST]` - Adição ou ajuste de testes automatizados
- `[SECURITY]` - Correção ou melhoria de segurança e autenticação
- `[CI]` / `[CD]` - Ajustes de integração ou entrega contínua

> **Importante:** O título deve ser **curto e objetivo** (máximo 70 caracteres após o prefixo). Todo detalhamento, motivação e impacto técnico devem ficar exclusivamente no corpo da issue.

---

## 3. Estrutura Obrigatória da Descrição (Body)

Toda issue criada deve seguir a estrutura de seções abaixo:

```markdown
### Contexto e Problema
<Primeiro parágrafo: Descrição concisa e direta do problema atual, gargalo ou necessidade de negócio. O que motivou a abertura desta issue e qual o cenário atual.>

### Proposta de Solução
<Detalhamento técnico do que será implementado nesta issue específica. Mantenha o foco estrito na responsabilidade única desta tarefa.>

### Dependências
- Depende de: #<numero_issue> (ou "Nenhuma dependência direta. Pode ser executada de forma paralela.")
- Bloqueia: #<numero_issue> (quando aplicável)

### Escopo e Domínios/Arquivos Afetados
Delimitação explícita de arquivos, pacotes e componentes modificados ou criados, para prevenir conflitos e concorrência entre agentes/desenvolvedores:
- Dominio principal: <ex: auth | feira | catalog | shipment | order | cart>
- Modulos / Pacotes: <ex: com.mosaico.core.auth.services>
- Arquivos afetados:
  - `caminho/para/Arquivo1.java`
  - `caminho/para/Arquivo2.vue`

### Contratos e DTOs (quando aplicável)
<Caso a issue defina rotas, payloads de entrada ou DTOs, SEMPRE utilize como base as entidades e tipos já existentes no codebase. NUNCA invente parâmetros arbitrários ou incompatíveis com o modelo atual do projeto.>

### Criterios de Aceite (Definition of Done)
- [ ] <Critério verificável 1>
- [ ] <Critério verificável 2>
- [ ] <Critério verificável 3>
- [ ] Testes unitários/integração escritos e validados (`./mvnw test` ou `npm run test`)
- [ ] Build e validação estática passando sem regressões

### Responsaveis
- Responsavel: @<usuario_atribuido> (ex: @wennerl77 para backend ou @AntonnyCaldeiraSilva para frontend)
```

---

## 4. Matriz de Labels Obrigatórias

Toda issue deve receber **no mínimo 4 labels** no momento da criação, permitindo identificação visual imediata na lista de issues e boards:

| Categoria | Labels Disponíveis | Regra |
|---|---|---|
| **1. Área** | `backend`, `frontend` | Obrigatório informar ao menos uma. |
| **2. Tipo** | `feature`, `bug`, `documentation`, `enhancement`, `security` | Corresponde ao prefixo do título. |
| **3. Prioridade** | `priority: high`, `priority: medium`, `priority: low` | Obrigatório definir o peso da issue. |
| **4. Domínio** | `domain: auth`, `domain: feira`, `domain: catalog`, `domain: mapa-feira`, `domain: cliente`, `domain: feirante`, `domain: comunidade`, `domain: reservas`, `domain: push-notifications`, `domain: ratings`, `domain: product-stock`, `domain: b2b`, `domain: admin-auth` | Delimita a fronteira de negócio. |

*Labels secundárias (quando aplicável):* `accessibility`, `good first issue`, `help wanted`.

---

## 5. Procedimento Operacional: Como Criar as Issues

Ao interagir com o usuário para criar issues, siga estas etapas:

### Passo 1: Analisar e Decompor a Demanda
1. Identifique o escopo completo solicitado pelo usuário.
2. Separe backend de frontend se o pedido for fullstack.
3. Quebre em tarefas com **responsabilidade única**.
4. Conte a quantidade de issues resultantes. Se **> 3 issues**, planeje a criação da **Milestone**.

### Passo 2: Investigar o Codebase (Zero Invenção)
1. Antes de redigir payloads ou citar classes, verifique o código real via `grep_search` ou `view_file`.
2. Garanta que nomes de rotas, campos de DTO e propriedades do banco correspondem à arquitetura atual do Mosaico (vide `AGENTS.md`).

### Passo 3: Criar a Milestone (se houver > 3 issues)
Utilize a GitHub CLI (`gh`):

```bash
gh api repos/Mosaico-br/Mosaico/milestones -f title="Nome da Milestone" -f description="Descrição do objetivo da milestone e ordem de execução: 1. Issue X -> 2. Issue Y -> 3. Issue Z"
```

### Passo 4: Criar a Issue via GitHub CLI
Crie a issue com as flags `--title`, `--body`, `--assignee`, `--label` e, se aplicável, `--milestone`:

```bash
gh issue create \
  --repo Mosaico-br/Mosaico \
  --title "[FEAT] - Adicionar endpoint de listagem de feiras por regiao" \
  --assignee "wennerl77" \
  --label "backend,feature,priority: high,domain: feira" \
  --body "### Contexto e Problema
O frontend necessita filtrar feiras ativas por codigo de regiao administrativa, mas atualmente o endpoint so retorna todas as feiras sem paginacao ou filtro geografico.

### Proposta de Solucao
Implementar parametro opcional regiaoId no endpoint GET /api/feiras com consulta paginada via Spring Data JPA.

### Dependencias
- Nenhuma dependencia previa.

### Escopo e Dominios/Arquivos Afetados
- Dominio principal: feira
- Modulos: com.mosaico.core.feira
- Arquivos afetados:
  - backend/src/main/java/com/mosaico/core/feira/controllers/FeiraController.java
  - backend/src/main/java/com/mosaico/core/feira/services/FeiraService.java
  - backend/src/main/java/com/mosaico/core/feira/repositories/FeiraRepository.java

### Contratos e DTOs
Parametros de consulta:
- regiaoId (Long, opcional)
- page (int, default 0)
- size (int, default 20)

### Criterios de Aceite (Definition of Done)
- [ ] Endpoint GET /api/feiras responde com status 200 e lista paginada filtrada por regiao
- [ ] Quando regiaoId for nulo, retorna todas as feiras mantendo compatibilidade
- [ ] Testes unitarios em FeiraServiceTest cobrindo o novo filtro
- [ ] ./mvnw test executa com 100% de sucesso

### Responsaveis
- Responsavel: @wennerl77"
```

### Passo 5: Confirmar e Apresentar ao Usuário
Retorne ao usuário com o link gerado pelo GitHub, o número da issue (`#ID`), o título, a atribuição e as labels vinculadas.

---

## 6. Recursos e Exemplos Adicionais
- [Template Canônico de Issue](./resources/issue-template.md)
- [Catálogo de Labels do Mosaico](./resources/labels-reference.md)
- [Exemplo de Issue de Backend](./examples/exemplo-issue-backend.md)
- [Exemplo de Issue de Frontend](./examples/exemplo-issue-frontend.md)
