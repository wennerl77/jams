# Template de Issue (Mosaico)

Copie e preencha este template ao estruturar novas issues para o repositório `Mosaico-br/Mosaico`.
Lembre-se: **zero emojis** e **apenas uma responsabilidade por issue**.

---

```markdown
### Contexto e Problema
<!-- Primeiro parágrafo: Descreva de forma objetiva qual é a dor atual, limitação técnica ou necessidade de negócio. -->

### Proposta de Solução
<!-- Descreva exatamente o que deve ser implementado nesta issue específica. Mantenha o foco estritamente na responsabilidade única delimitada. -->

### Dependências
- Depende de: <!-- Ex: #12 ou "Nenhuma dependência prévia. Pode ser iniciada de forma independente." -->
- Bloqueia: <!-- Ex: #15 (se aplicável) -->

### Escopo e Domínios/Arquivos Afetados
<!-- Identifique claramente a fronteira técnica para evitar trabalho concorrente em mesmos arquivos/domínios. -->
- Domínio principal: <!-- Ex: auth | feira | catalog | shipment | order | cart | payment -->
- Módulos / Pacotes: <!-- Ex: com.mosaico.core.auth ou frontend/src/stores/ -->
- Arquivos afetados:
  - `caminho/para/arquivo1`
  - `caminho/para/arquivo2`

### Contratos e DTOs (quando aplicável)
<!-- Exiba a assinatura de endpoints, payloads JSON ou estruturas de dados. SEMPRE baseie-se no código existente no repositório. NUNCA invente parâmetros. -->
<!-- Exemplo:
```json
{
  "campo": "valor"
}
```
-->

### Critérios de Aceite (Definition of Done)
- [ ] Implementação de acordo com as regras de negócio descritas
- [ ] Tratamento adequado de erros e validações de entrada
- [ ] Testes automatizados escritos e passando
- [ ] Build e validação estática passando sem erros

### Responsáveis
- Responsável: <!-- @wennerl77 (Backend) ou @AntonnyCaldeiraSilva (Frontend) -->
```
