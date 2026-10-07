# Exemplo Real de Issue de Backend

### Título:
```text
[FEAT] - Adicionar endpoint para desativar barraca do feirante
```

### Labels:
```text
backend, feature, priority: high, domain: feirante
```

### Assignee:
```text
wennerl77
```

---

### Corpo da Issue (Body):

```markdown
### Contexto e Problema
Atualmente o feirante não possui um mecanismo para pausar ou desativar temporariamente as atividades da sua barraca na plataforma quando necessita se ausentar da feira. A barraca continua aparecendo como ativa na listagem pública, gerando expectativas incorretas aos clientes.

### Proposta de Solucao
Criar endpoint PATCH /api/barracas/my/status para alternar o status operacional da barraca (ativa: true/false). Apenas o feirante proprietário da barraca autenticado deve poder realizar a alteração, garantido pela anotação @IsBarracaOwner.

### Dependencias
- Nenhuma dependencia previa. Tarefa autonoma e isolada.

### Escopo e Dominios/Arquivos Afetados
- Dominio principal: feirante / barraca
- Modulos: com.mosaico.core.barraca
- Arquivos afetados:
  - `backend/src/main/java/com/mosaico/core/barraca/controllers/BarracaController.java`
  - `backend/src/main/java/com/mosaico/core/barraca/services/BarracaService.java`
  - `backend/src/main/java/com/mosaico/core/barraca/dto/BarracaStatusUpdateRequest.java`

### Contratos e DTOs
Payload de entrada:
```json
{
  "ativa": false,
  "motivoPausa": "Férias coletivas"
}
```

Resposta:
HTTP 204 No Content

### Criterios de Aceite (Definition of Done)
- [ ] Endpoint PATCH /api/barracas/my/status implementado com validacao de payload @Valid
- [ ] Acesso restrito via anotação de seguranca @IsBarracaOwner
- [ ] Barraca desativada deixa de ser retornada na listagem pública de barracas abertas
- [ ] Testes unitarios cobrindo cenarios de sucesso e usuario nao autorizado (403)
- [ ] Suite de testes passa com `./mvnw test -Dtest=BarracaServiceTest`

### Responsaveis
- Responsavel: @wennerl77
```
