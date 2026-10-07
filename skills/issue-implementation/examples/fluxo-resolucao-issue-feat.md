# Exemplo de Fluxo de Resolução de Issue [FEAT]

Exemplo prático de ponta a ponta demonstrando como a skill `issue-implementation` opera na resolução de uma issue real.

---

### 1. Comando do Usuário:
> "Implemente a issue #33 do backend"

### 2. Passo 1: Leitura da Issue
```bash
gh issue view 33 --repo Mosaico-br/Mosaico --json number,title,body,labels,assignees,state
```
- Retorno: Issue aberta por @wennerl77, labels `backend`, `feature`, tratando de API para Lojista.

### 3. Passo 2: Verificação de Dependências
- Na seção `### Dependências`, não há dependências de backend abertas.

### 4. Passo 3: Criação de Branch
```bash
git checkout main
git pull origin main
git checkout -b feat/33-api-lojista
```

### 5. Passo 4: Criação da Spec e Aguardo de Aprovação
O agente cria a spec em `backend/.agents/spec/feat-api-lojista/SPEC.md` com DTOs, entidades, controllers e critérios de aceite.

**Comunicação com o usuário (PONTO DE PARADA):**
> "Criei a especificação técnica da issue #33 em `backend/.agents/spec/feat-api-lojista/SPEC.md`. Ela detalha os endpoints REST, a entidade JPA Lojista e os critérios de aceite. Por favor, revise a spec. Posso prosseguir com a implementação?"

*Apenas após o usuário responder "aprovado", "prossiga" ou similar, o agente segue para o passo 6.*

### 6. Passo 5: Implementação no Escopo
- Criação dos arquivos estritamente delimitados na spec:
  - `backend/src/main/java/com/mosaico/core/user/entities/Lojista.java`
  - `backend/src/main/java/com/mosaico/core/user/controllers/LojistaController.java`
  - `backend/src/main/java/com/mosaico/core/user/services/LojistaService.java`
  - `backend/src/main/java/com/mosaico/core/user/dto/LojistaProfileResponse.java`

### 7. Passo 6: Validação de Testes e DoD
```bash
./mvnw clean compile
./mvnw test -Dtest=LojistaServiceTest
./mvnw test
```
- Validação de todos os critérios de aceite.
- Atualização do status da spec para `DONE`.

### 8. Passo 7: Commit, Push e Pull Request
```bash
git add backend/src/main/java/com/mosaico/core/user/...
git commit -m "feat(lojista): adicionar api rest para perfil e fornecedores do lojista (Closes #33)"
git push origin feat/33-api-lojista
gh pr create --title "[FEAT] - API REST para entidade Lojista" --body "Resolve #33. Todos os critérios de aceite atendidos e validados por testes. Closes #33"
```
