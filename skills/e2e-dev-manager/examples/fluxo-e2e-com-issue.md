# Exemplo Prático: Fluxo E2E Vinculado a uma Issue do GitHub

Este exemplo documenta a orquestração do **E2E Dev Manager** ao receber o comando:  
`"Implemente a issue #33 do GitHub"`

---

## 1. Entrada do Usuário
> **Usuário:** "Por favor, orquestre a implementação ponta a ponta da issue #33 do GitHub."

---

## 2. Passo 1 — Gerente Invoca Subagente 1 (Context & Issue Analyst)

O Gerente executa a ferramenta `invoke_subagent`:
- **TypeName:** `"self"`
- **Role:** `"Issue Context Analyst"`
- **Prompt:**
  ```markdown
  Inspecione a issue #33 no repositório Mosaico-br/Mosaico via GitHub CLI.
  Verifique dependências abertas, atualize a main e crie a branch de trabalho.
  Siga a skill: backend/.agents/skills/github-issues/SKILL.md
  ```

### Resposta do Subagente 1:
- Issue #33 localizada: `[FEAT] - Adicionar endpoint de listagem de feirantes por barraca`.
- Assignee: `wennerl77`. Labels: `backend`, `feature`, `priority: medium`, `domain: barraca`.
- Dependências: Nenhuma bloqueante aberta.
- Branch criada: `feat/33-feirantes-por-barraca` a partir de `main` atualizada.

---

## 3. Passo 2 — Gerente Invoca Subagente 2 (Spec Architect)

O Gerente executa a ferramenta `invoke_subagent`:
- **TypeName:** `"self"`
- **Role:** `"Spec Technical Architect"`
- **Prompt:**
  ```markdown
  Elabore a especificação técnica formal para a issue #33 em:
  backend/.agents/spec/feat-feirantes-por-barraca/SPEC.md
  Siga a skill: backend/.agents/skills/spec-creation/SKILL.md
  Pesquise o codebase factual e monte os DTOs records, inventário de arquivos e DoD.
  ```

### Resposta do Subagente 2:
- Spec criada em `backend/.agents/spec/feat-feirantes-por-barraca/SPEC.md` (`status: READY`).
- Inventário delimitado:
  - `[NEW]` `FeiranteResponse.java` (DTO record).
  - `[MODIFY]` `BarracaService.java` (método `findFeirantesByBarracaId`).
  - `[MODIFY]` `BarracaController.java` (endpoint `GET /api/barracas/{id}/feirantes` com `@IsBarracaOwner`).
  - `[NEW]` `BarracaServiceTest.java` (testes unitários).

### Quality Gate / Ponto de Parada:
O Gerente interrompe temporariamente a execução e apresenta a spec ao usuário:
> *"A especificação técnica foi elaborada em `backend/.agents/spec/feat-feirantes-por-barraca/SPEC.md`. Por favor, revise os contratos e o inventário delimitado. Posso prosseguir com a implementação?"*
>
> **Usuário responde:** *"Aprovado, pode prosseguir."*

---

## 4. Passo 3 — Gerente Invoca Subagente 3 (Backend Implementer)

O Gerente aciona o implementador técnico:
- **TypeName:** `"self"`
- **Role:** `"Backend Domain Implementer"`
- **Prompt:**
  ```markdown
  Desenvolva a implementação da spec backend/.agents/spec/feat-feirantes-por-barraca/SPEC.md.
  Siga as diretrizes de backend/.agents/rules/code-standards.md.
  Restrinja-se exclusivamente aos arquivos do inventário delimitado.
  ```

### Resposta do Subagente 3:
- Arquivos criados e alterados conforme a spec.
- Regra de negócio implementada em `BarracaService` com `@Transactional(readOnly = true)`.
- Status da spec alterado para `IMPLEMENTING`.

---

## 5. Passo 4 — Gerente Invoca Subagente 4 (QA & Test Engineer)

O Gerente aciona a validação de testes:
- **TypeName:** `"self"`
- **Role:** `"Backend QA & Test Engineer"`
- **Prompt:**
  ```markdown
  Compile e crie testes unitários para o endpoint de feirantes por barraca.
  Siga backend/.agents/rules/testing.md.
  Execute ./mvnw clean compile e ./mvnw test.
  ```

### Resposta do Subagente 4:
- `./mvnw clean compile`: SUCESSO (0 erros).
- Testes unitários implementados em `BarracaServiceTest` (cenários de sucesso e barraca inexistente).
- Suíte completa `./mvnw test` executada: 142 testes executados, 142 passaram, 0 falhas.

---

## 6. Passo 5 — Gerente Invoca Subagente 5 (Code Reviewer)

O Gerente aciona a auditoria de código:
- **TypeName:** `"self"`
- **Role:** `"Senior Code Reviewer"`
- **Prompt:**
  ```markdown
  Realize o code review do diff da branch feat/33-feirantes-por-barraca contra a main.
  Siga backend/.agents/agents/code-review.md.
  ```

### Resposta do Subagente 5:
- Parecer: `[APROVADO]`.
- Métodos com menos de 25 linhas, imports limpos sem FQCN, anotação `@IsBarracaOwner` devidamente aplicada, zero secrets expostos.

---

## 7. Passo 6 — Gerente Invoca Subagente 6 (Git & Release Manager)

O Gerente aciona o encerramento do versionamento:
- **TypeName:** `"self"`
- **Role:** `"Git & Release Manager"`
- **Prompt:**
  ```markdown
  Finalize o ciclo da issue #33:
  Atualize a spec para status: DONE, faça commit semântico com Closes #33,
  push para origin e abra o PR via gh pr create.
  ```

### Resposta do Subagente 6:
- Commit `a1b2c3d` realizado: `feat(barraca): adiciona listagem de feirantes por barraca (Closes #33)`.
- Push para `origin/feat/33-feirantes-por-barraca`.
- Pull Request aberto: `https://github.com/Mosaico-br/Mosaico/pull/45`.

---

## 8. Relatório Final Entregue pelo Gerente ao Usuário

O Gerente compila todas as informações utilizando o `template-relatorio-final.md` e devolve a resposta executiva final com links clicáveis e resumo de testes.
