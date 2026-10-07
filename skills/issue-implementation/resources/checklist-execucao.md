# Checklist Operacional de Implementação de Issue

Utilize esta checklist para garantir que nenhuma etapa obrigatória foi pulada durante a resolução de uma issue no Mosaico.

---

### Fase 1: Pré-Implementação & Análise
- [ ] Issue lida no GitHub via `gh issue view <ID>`
- [ ] Tipo identificado (`[FEAT]`, `[FIX]`, `[CHORE]`, etc.)
- [ ] Verificação de dependências: todas as issues bloqueantes estão `CLOSED`
- [ ] Branch criada no padrão `<tipo>/<id>-<slug>` a partir da `main` atualizada
- [ ] **Se [FEAT]:** Spec técnica criada em `.agents/spec/feat-<nome>/SPEC.md`
- [ ] **Se [FEAT]:** **APROVAÇÃO FORMAL DO USUÁRIO RECEBIDA** antes de tocar em código produtivo
- [ ] **Se [FIX]:** Causa raiz diagnosticada e documentações impactadas mapeadas

---

### Fase 2: Implementação & Código
- [ ] Modificações estritamente restritas aos arquivos e domínios do escopo da issue/spec
- [ ] Nenhum arquivo fora do escopo foi alterado
- [ ] Padrões de arquitetura do `AGENTS.md` respeitados (DTOs como records, @Transactional em Services, Controllers enxutos)
- [ ] **Se [FIX]:** Documentação técnica relacionada (docs, Swagger, README) atualizada

---

### Fase 3: Validação & Qualidade
- [ ] Compilação com sucesso: `./mvnw clean compile`
- [ ] Testes da funcionalidade executados e passando: `./mvnw test -Dtest=...`
- [ ] Suíte completa de testes executada sem regressões: `./mvnw test`
- [ ] Todos os critérios de aceite (DoD) verificados e atendidos
- [ ] **Se [FEAT]:** Status da spec atualizado para `DONE`

---

### Fase 4: Entrega & Fechamento
- [ ] Git status verificado (sem arquivos indesejados ou untracked fora de contexto)
- [ ] Commit semântico realizado referenciando a issue: `feat(...): ... (Closes #ID)`
- [ ] Push da branch para `origin`
- [ ] Pull Request criado via `gh pr create` contendo `Closes #ID`
