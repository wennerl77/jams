# Exemplo Prático: Fluxo E2E Baseado em Pedido Direto Explícito

Este exemplo documenta a orquestração do **E2E Dev Manager** ao receber uma demanda direta e explícita do desenvolvedor:  
`"Adicione um endpoint no backend para filtrar feiras ativas por horário de funcionamento"`

---

## 1. Entrada do Usuário
> **Usuário:** "Faça o desenvolvimento E2E para adicionar um filtro no endpoint de feiras que permita buscar feiras ativas por faixa de horário de funcionamento."

---

## 2. Passo 1 — Gerente Invoca Subagente 1 (Context & Issue Analyst)

Mesmo sem uma issue cadastrada previamente, o Subagente 1 atua para delimitar o escopo e preparar o ambiente:
- **TypeName:** `"self"`
- **Role:** `"Issue Context Analyst"`
- **Prompt:**
  ```markdown
  Demanda direta: "Filtrar feiras ativas por faixa de horário de funcionamento".
  Sincronize a base local com origin/main e crie uma branch com slug descritivo.
  Exemplo: feat/filtro-feiras-horario-funcionamento.
  ```

### Resposta do Subagente 1:
- Base `main` sincronizada com `origin/main`.
- Branch `feat/filtro-feiras-horario-funcionamento` criada e ativa.
- Tipo detectado: `[FEAT]`. Domínio: `feira`.

---

## 3. Passo 2 — Gerente Invoca Subagente 2 (Spec Architect)

O Gerente delega a modelagem da spec:
- **TypeName:** `"self"`
- **Role:** `"Spec Technical Architect"`
- **Prompt:**
  ```markdown
  Elabore a especificação técnica formal para a feature de filtro de feiras por horário em:
  backend/.agents/spec/feat-filtro-feiras-horario/SPEC.md
  Siga a skill: backend/.agents/skills/spec-creation/SKILL.md
  Pesquise FeiraRepository e FeiraController para reaproveitar estruturas existentes.
  ```

### Resposta do Subagente 2:
- Spec criada em `backend/.agents/spec/feat-filtro-feiras-horario/SPEC.md` (`status: READY`).
- Parâmetros definidos: `LocalTime horaInicio` e `LocalTime horaFim` opcionais no `GET /api/feiras`.
- Inventário de arquivos mapeado (`FeiraRepository.java`, `FeiraService.java`, `FeiraController.java`, `FeiraServiceTest.java`).

### Quality Gate / Ponto de Parada:
O Gerente interrompe e solicita aprovação formal:
> *"Spec técnica criada em `backend/.agents/spec/feat-filtro-feiras-horario/SPEC.md`. Por favor, revise os contratos e parâmetros. Posso prosseguir com a implementação?"*
>
> **Usuário responde:** *"Pode implementar!"*

---

## 4. Passo 3 — Gerente Invoca Subagente 3 (Backend Implementer)

O Gerente delega a codificação:
- **TypeName:** `"self"`
- **Role:** `"Backend Domain Implementer"`
- **Prompt:**
  ```markdown
  Implemente o código conforme a spec aprovada backend/.agents/spec/feat-filtro-feiras-horario/SPEC.md.
  Respeite as regras de backend/.agents/rules/code-standards.md.
  ```

### Resposta do Subagente 3:
- Adicionada query derivada/JPQL em `FeiraRepository`.
- Lógica de consulta paginada em `FeiraService` com `@Transactional(readOnly = true)`.
- Atualizado `FeiraController` com parâmetros `@RequestParam(required = false)`.

---

## 5. Passo 4 — Gerente Invoca Subagente 4 (QA & Test Engineer)

O Gerente delega a validação de testes automatizados:
- **TypeName:** `"self"`
- **Role:** `"Backend QA & Test Engineer"`
- **Prompt:**
  ```markdown
  Escreva testes unitários para o filtro de horário em FeiraServiceTest e valide ./mvnw test.
  Siga backend/.agents/rules/testing.md.
  ```

### Resposta do Subagente 4:
- Testes unitários cobrindo horário matutino, vespertino e sem filtro.
- `./mvnw clean compile` e `./mvnw test`: 100% de sucesso.

---

## 6. Passo 5 — Gerente Invoca Subagente 5 (Code Reviewer)

O Gerente aciona a auditoria de qualidade:
- **TypeName:** `"self"`
- **Role:** `"Senior Code Reviewer"`
- **Prompt:**
  ```markdown
  Audite o diff da branch feat/filtro-feiras-horario-funcionamento em relação a main.
  Siga backend/.agents/agents/code-review.md.
  ```

### Resposta do Subagente 5:
- Parecer: `[APROVADO]`. Nenhuma quebra de contrato, queries otimizadas, separação de camadas preservada.

---

## 7. Passo 6 — Gerente Invoca Subagente 6 (Git & Release Manager)

O Gerente delega a publicação:
- **TypeName:** `"self"`
- **Role:** `"Git & Release Manager"`
- **Prompt:**
  ```markdown
  Finalize o ciclo: atualize a spec para status: DONE, faça o commit semântico, push e abra o PR.
  ```

### Resposta do Subagente 6:
- Commit semântico: `feat(feira): adiciona filtro de horario de funcionamento no endpoint de feiras`.
- Push para `origin/feat/filtro-feiras-horario-funcionamento`.
- PR aberto no repositório: `https://github.com/Mosaico-br/Mosaico/pull/46`.

---

## 8. Relatório Final

O Gerente entrega o relatório executivo completo estruturado ao usuário.
