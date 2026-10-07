# Template de Relatório Executivo de Entrega E2E (Mosaico Backend)

Utilize esta estrutura padronizada para compilar e apresentar os resultados consolidados de uma esteira E2E ao usuário final.

---

```markdown
# 📋 Relatório Executivo de Entrega E2E — Mosaico Backend

**Data de Conclusão:** {{DATA_ATUAL}}  
**Identificador da Demanda:** {{ISSUE_OU_DEMANDA}}  
**Branch de Trabalho:** `{{NOME_BRANCH}}`  
**Status do Ciclo:** 🟢 CONCLUÍDO COM SUCESSO  
**Pull Request:** [{{PR_TITULO}}]({{PR_URL}})

---

## 1. 🎯 Resumo da Entrega & Objetivo
{{DESCRICAO_OBJETIVA_DO_QUE_FOI_RESOLVIDO}}

- **Tipo da Tarefa:** `{{TIPO_TAREFA}}` (`[FEAT]`, `[FIX]`, `[REFACTOR]`, `[CHORE]`)
- **Domínio Afetado:** `{{DOMINIO}}` (ex: `auth`, `feira`, `order`, etc.)
- **Responsável Atribuído:** `@{{ASSIGNEE}}`

---

## 2. 📑 Especificação Técnica & Contratos
- **Arquivo da Spec:** [SPEC.md]({{CAMINHO_SPEC}})
- **Status da Spec:** `DONE`
- **Principais Contratos & Endpoints:**
  - `{{METODO_HTTP}} {{ROTA_CANONICA}}` — {{DESCRICAO_ROTA}}
- **DTOs Criados/Alterados:**
  - `{{NOME_DTO_RECORD}}` (`record` imutável com Bean Validation)

---

## 3. 📂 Inventário Técnico de Arquivos Impactados

| Ação | Caminho do Arquivo | Responsabilidade |
|---|---|---|
| `[NEW]` | `backend/src/main/java/.../{{ARQUIVO}}.java` | {{RESPONSABILIDADE}} |
| `[MODIFY]` | `backend/src/main/java/.../{{ARQUIVO_EXISTENTE}}.java` | {{ALTERACAO}} |
| `[NEW]` | `backend/src/test/java/.../{{ARQUIVO_TESTE}}.java` | Testes unitários da funcionalidade |

---

## 4. 🧪 Validação da Qualidade & Testes Automatizados

- **Compilação do Projeto:** `./mvnw clean compile` — 🟢 **100% OK** (Zero erros de compilação)
- **Suíte de Testes Executada:** `./mvnw test`
  - **Total de Testes Rodados:** `{{QTD_TESTES}}`
  - **Aprovados:** `{{QTD_APROVADOS}}`
  - **Falhas / Erros:** `0`
- **Critérios de Aceite (Definition of Done - DoD):**
  - [x] {{CRITERIO_1}}
  - [x] {{CRITERIO_2}}
  - [x] {{CRITERIO_3}}
  - [x] Regressão validada (nenhum teste anterior quebrado)

---

## 5. 🔍 Parecer de Code Review & Auditoria
**Auditor:** Subagente Especialista em Code Review  
**Resultado:** 🟢 **APROVADO SEM RESSALVAS CRÍTICAS**

- **Camadas & Separação:** Controller fino, regra 100% no Service com `@Transactional`, DTOs isolados.
- **Tamanho de Métodos:** Todos os métodos contêm ≤ 30 linhas de código.
- **Segurança & LGPD:** Zero secrets hardcoded, autorização `@Is...` aplicada, dados sensíveis protegidos.
- **Consistência:** Nomenclatura camelCase/PascalCase uniforme, zero FQCN soltos no código.

---

## 6. 🚀 Integração Git & Pull Request
- **Commit Semântico:** `{{HASH_COMMIT}}` — `{{MENSAGEM_COMMIT}}`
- **Branch Remota:** `origin/{{NOME_BRANCH}}`
- **Pull Request Oficial:**
  👉 **[{{PR_URL}}]({{PR_URL}})** (Vinculado para fechamento automático: `Closes #{{ISSUE_ID}}`)

---

## 7. 📌 Próximos Passos Sugeridos
1. Revisão por pares no GitHub PR (`@{{ASSIGNEE}}`).
2. Aprovação e merge para a branch `main`.
3. Execução do pipeline de CI no GitHub Actions (`backend-workflow.yaml`).
```
