---
name: spec-creation
description: >-
  Define o processo canônico e rigoroso para elaborar especificações técnicas (SPEC.md)
  no backend do Mosaico antes de qualquer desenvolvimento. Elimina inferências e achismos
  através de pesquisa factual obrigatória no codebase, inventário técnico de arquivos
  [NEW|MODIFY|DELETE], modelagem precisa de DTOs/entidades/endpoints, plano sequencial
  em 7 camadas e critérios de aceite verificáveis (DoD).
---

# Skill: Criação e Modelagem de Especificações Técnicas (SPEC.md)

Esta skill estabelece o processo obrigatório, determinístico e livre de suposições para elaborar especificações técnicas de engenharia no projeto **Mosaico Backend**.

A spec funciona como um **contrato técnico formal** entre o planejamento, a implementação e a revisão de código. Nenhuma linha de código produtivo de nova funcionalidade (`feat`) deve ser escrita sem uma spec previamente aprovada pelo usuário.

---

## 1. Princípio Fundamental: Zero Inferência e Pesquisa Prévia Obrigatória

**É terminantemente proibido redigir uma spec com base em suposições ou inferências ("eu acho").**

Antes de escrever qualquer linha da spec, o agente **DEVE executar uma fase de investigação factual no codebase**:
1. **Localizar arquivos e entidades existentes:** Use `grep_search` e `find_by_name` para identificar classes correlatas, enums e tabelas.
2. **Checar DTOs e entidades vigentes:** Abra os arquivos via `view_file` para verificar tipos reais (`UUID`, `Long`, `String`), nomes exatos de atributos em camelCase e colunas em snake_case.
3. **Mapear anotações e padrões:** Verifique se as classes usam Lombok (`@Getter`, `@Setter`, `@Builder`), Bean Validation (`@NotNull`, `@NotBlank`) e convenções de segurança (`@IsBarracaOwner`, `@IsAdmin`, etc.).
4. **Validar endpoints e rotas existentes:** Consulte os controllers do domínio para manter consistência semântica nas URIs REST (`/api/...`).

---

## 2. Localização, Nomenclatura e Ciclo de Vida da Spec

### 2.1. Caminho Padrão
Toda especificação técnica deve ser criada em seu próprio diretório dedicado:

```text
backend/.agents/spec/<tipo>-<nome-kebab-case>/SPEC.md
```

- **Prefixos válidos:** `feat`, `fix`, `refactor`, `chore`, `docs`, `security`.
- **Exemplos:**
  - `backend/.agents/spec/feat-calendario-feira/SPEC.md`
  - `backend/.agents/spec/feat-api-lojista/SPEC.md`
  - `backend/.agents/spec/fix-calculo-taxa-entrega/SPEC.md`

### 2.2. Cabeçalho YAML Obrigatório

O início do arquivo `SPEC.md` deve conter rigorosamente o bloco frontmatter:

```yaml
---
name: [Nome Curto e Claro da Funcionalidade]
description: [Resumo objetivo em 1 ou 2 frases do que a spec define]
type: feat | fix | refactor | chore | docs | security
status: DRAFT | READY | IMPLEMENTING | REVIEW | DONE
issue: "#<ID>"  # Incluir obrigatoriamente quando associada a uma GitHub Issue
created_at: YYYY-MM-DD
implemented_at: YYYY-MM-DD  # Preenchido apenas ao finalizar
---
```

### 2.3. Máquina de Estados (Ciclo de Status)
- `DRAFT`: Spec em fase de pesquisa e redação pelo agente.
- `READY`: Spec concluída pelo agente e **aguardando leitura e aprovação explícita do usuário** (Ponto de Parada).
- `IMPLEMENTING`: Usuário aprovou formalmente a spec; desenvolvimento de código liberado.
- `REVIEW`: Código implementado e testes automatizados passando; aguarda revisão final.
- `DONE`: Implementação validada, critérios de aceite atendidos e alteração concluída.

---

## 3. Estrutura Anatômica Obrigatória da SPEC.md

Toda spec deve conter as 9 seções detalhadas abaixo, sem omitir etapas:

```markdown
# [Nome da Funcionalidade / Alteração]

## 1. Descrição
### 1.1. Problema Atual
### 1.2. Objetivo da Alteração
### 1.3. Motivo da Mudança

## 2. Contexto Arquitetural
### 2.1. Módulos Afetados
### 2.2. Entidades Envolvidas
### 2.3. Dependências e Bibliotecas
### 2.4. Integrações Impactadas

## 3. Inventário Técnico de Arquivos
(Tabela ou lista estrita com [NEW], [MODIFY], [DELETE] e caminhos reais)

## 4. Modelagem de Dados e Contratos Reais
### 4.1. Entidades JPA e Banco de Dados
### 4.2. DTOs de Entrada e Saída (Records)
### 4.3. Endpoints REST e Assinaturas Web
### 4.4. Mappers (MapStruct)

## 5. Plano de Implementação Sequencial Ordenado
(Passos numerados rigorosamente seguindo a cadeia de 7 camadas)

## 6. Restrições Técnicas & Decisões Arquiteturais
### 6.1. Restrições e Padrões Obrigatórios
### 6.2. Decisões Técnicas Justificadas

## 7. Análise de Riscos e Mitigações

## 8. Critérios de Aceite (Definition of Done - DoD)
(Checklist verificável com checkboxes)

## 9. Checklist Final de Pós-Implementação
```

---

## 4. Guia Rígido de Preenchimento de Cada Seção

### Seção 1: Descrição
- **Problema Atual:** Descreva objetivamente a limitação, bug ou ausência de recurso no sistema hoje. O que falha ou o que não é possível fazer?
- **Objetivo da Alteração:** O que o sistema passará a fazer após a entrega.
- **Motivo da Mudança:** Qual o valor de negócio, segurança ou arquitetura que justifica a implementação.

### Seção 2: Contexto Arquitetural
- **Módulos Afetados:** Mapeie os pacotes exatos em `com.mosaico.core.<feature>` (ex: `com.mosaico.core.feira`, `com.mosaico.core.user`).
- **Entidades Envolvidas:** Liste as entidades JPA existentes que serão lidas/alteradas e as novas a serem criadas.
- **Dependências:** Tecnologias empregadas (ex: PostgreSQL, Spring Security, Bucket4j, Stream Chat, Resend).
- **Integrações Impactadas:** Fluxos adjacentes afetados (ex: fluxo de checkout, autorização de feirante, notificações push).

### Seção 3: Inventário Técnico de Arquivos
Liste todos os arquivos que sofrerão alteração ou serão criados, classificando-os formalmente:
- `[NEW]`: Arquivo novo a ser criado.
- `[MODIFY]`: Arquivo existente a ser alterado.
- `[DELETE]`: Arquivo obsoleto a ser excluído.

*Exemplo Obrigatório:*
| Ação | Caminho do Arquivo | Responsabilidade / Modificação |
|---|---|---|
| `[NEW]` | `backend/src/main/java/com/mosaico/core/user/entities/Lojista.java` | Entidade JPA com vínculo a User (role LOJISTA). |
| `[NEW]` | `backend/src/main/java/com/mosaico/core/user/repositories/LojistaRepository.java` | Interface Spring Data JPA. |
| `[NEW]` | `backend/src/main/java/com/mosaico/core/user/dto/LojistaProfileResponse.java` | Java record de resposta com dados públicos do lojista. |
| `[MODIFY]` | `backend/src/main/java/com/mosaico/core/user/entities/User.java` | Adição de relacionamento opcional OneToOne com Lojista. |
| `[NEW]` | `backend/src/test/java/com/mosaico/core/user/services/LojistaServiceTest.java` | Testes unitários das regras de negócio do lojista. |

### Seção 4: Modelagem de Dados e Contratos Reais
Esta seção não deve conter pseudocódigo genérico. Apresente o código exato planejado:
1. **Entidades JPA:**
   - Detalhe campos, tipos, anotações de tabela (`@Table(name = "...")`), chaves primárias (UUID ou Long), colunas (`@Column(name = "...", nullable = ...)`), chaves estrangeiras e relacionamentos com lazy loading explícito (`@ManyToOne(fetch = FetchType.LAZY)`).
2. **DTOs (Data Transfer Objects):**
   - **Obrigatoriamente Java `record`s imutáveis.**
   - Declarar todas as anotações do Bean Validation necessárias: `@NotNull`, `@NotBlank`, `@Size`, `@PositiveOrZero`, `@Email`, etc.
3. **Endpoints REST (Controllers):**
   - Verbo HTTP (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`).
   - Rota canônica (ex: `/api/feiras/{id}/schedule`).
   - Parâmetros de rota (`@PathVariable`), parâmetros de query (`@RequestParam`) ou payload no body (`@Valid @RequestBody`).
   - Código HTTP de resposta (`200 OK`, `201 Created`, `204 No Content`, `400 Bad Request`, `403 Forbidden`, `404 Not Found`).
   - Anotações de segurança e RBAC (ex: `@IsAdmin`, `@IsFeirante`, `@IsBarracaOwner`).
4. **Mappers (MapStruct):**
   - Assinatura dos métodos de conversão DTO <-> Entidade com `@Mapper(componentModel = "spring")`.

### Seção 5: Plano de Implementação Sequencial Ordenado
O plano de passos deve seguir estritamente a **Ordem Canônica das 7 Camadas** do backend Spring Boot:
1. **Passo 1 — Banco de Dados, Migrações e Entidades JPA:** Modelagem das classes de entidade e ajustes no esquema relacional.
2. **Passo 2 — Repositórios Spring Data JPA:** Criação de interfaces `Repository` e queries com `@Query` quando aplicável.
3. **Passo 3 — DTOs de Request e Response:** Criação dos Java records de entrada e saída com Bean Validation.
4. **Passo 4 — Mappers MapStruct:** Interface de conversão entre entidades e DTOs.
5. **Passo 5 — Regras de Negócio e Serviços (Service Layer):**
   - Métodos com regras de negócio completas.
   - `@Transactional(readOnly = true)` para leituras e `@Transactional` para escritas.
   - Métodos recebendo DTOs ou entidades completas em vez de parâmetros primitivos desestruturados.
   - Lançamento de exceções de negócio bem definidas (ex: `EntityNotFoundException`, `BusinessException`).
6. **Passo 6 — Camada Web e Segurança (Controller Layer):**
   - Controllers enxutos delegando 100% da lógica ao Service.
   - Validação de entrada com `@Valid`.
   - Aplicação de anotações de autorização customizadas (`@Is...`).
7. **Passo 7 — Testes Automatizados:**
   - Criação de testes unitários e de integração espelhando a feature em `src/test/java/com/mosaico/core/...`.
   - Validação de cenários de sucesso, validação de payload inválido (400) e acesso não autorizado (403).

### Seção 6: Restrições Técnicas & Decisões Arquiteturais
- **Restrições:** Respeitar integralmente o arquivo `backend/AGENTS.md` (Java 25 preview features, Spring Boot 3.5, PostgreSQL 16, porta 8081).
- **Decisões Técnicas:** Justifique cada escolha estrutural relevante. Por exemplo:
  - *"Optou-se por cálculo em memória em vez de persistir datas em lote no banco para mitigar sobrecarga de armazenamento."*
  - *"Utilizou-se UUID na entidade temporária para evitar colisões em instâncias distribuídas."*

### Seção 7: Análise de Riscos e Mitigações
Analise criticamente:
- **Risco de Concorrência / Race Condition:** Necessidade de lock pessimista/otimista ou controle transacional?
- **Quebra de Contrato:** O novo endpoint afeta contratos consumidos pelo frontend Vue 3?
- **Performance:** Há risco de queries N+1 no Hibernate? Mitigar com `JOIN FETCH` ou `EntityGraph`.

### Seção 8: Critérios de Aceite (Definition of Done - DoD)
Liste itens objetivos, mensuráveis e atômicos usando checkboxes (`- [ ]`). Devem cobrir:
- [ ] Endpoints implementados respondendo com os status HTTP corretos.
- [ ] Validações de payload (`@Valid`) rejeitando entradas inválidas com 400.
- [ ] Controle de acesso e ownership validado (403 para usuários não autorizados).
- [ ] Transações de banco confirmadas e consistência de dados preservada.
- [ ] Testes automatizados cobrindo cenários de sucesso e falha passando com `./mvnw test`.
- [ ] Build e compilação do projeto concluídos com `./mvnw clean compile`.

### Seção 9: Checklist Final de Pós-Implementação
Checklist padronizado para encerramento da spec:
- [ ] Implementação de código concluída no escopo delimitado.
- [ ] Todos os critérios de aceite (DoD) verificados e atendidos.
- [ ] Testes executados com sucesso (`mvn test`).
- [ ] Status da spec alterado de `IMPLEMENTING` para `DONE`.
- [ ] Data de implementação preenchida no cabeçalho YAML (`implemented_at`).

---

## 5. Protocolo de Aprovação Obrigatório (Ponto de Parada)

Ao concluir a elaboração do arquivo `SPEC.md`, o agente deve seguir rigorosamente este protocolo:

1. Salvar o arquivo com status `status: READY`.
2. Apresentar ao usuário uma síntese executiva contendo:
   - Caminho da spec criada.
   - Resumo da proposta e dos endpoints/entidades modelados.
   - Lista de arquivos impactados (`[NEW]` / `[MODIFY]`).
   - Principais decisões técnicas.
3. **PARAR IMEDIATAMENTE A EXECUÇÃO E PERGUNTAR:**
   > *"A especificação técnica foi gerada em `backend/.agents/spec/<nome>/SPEC.md`. Por favor, revise os contratos, DTOs e o plano de implementação. Posso iniciar o desenvolvimento?"*
4. **NÃO ESCREVA NENHUM CÓDIGO DA FEATURE ANTES DO USUÁRIO RESPONDER APROVANDO.**
