# Exemplo Real de Issue de Frontend

### Título:
```text
[FEAT] - Adicionar skeleton loader na visualização de detalhes da feira
```

### Labels:
```text
frontend, feature, priority: medium, domain: feira
```

### Assignee:
```text
AntonnyCaldeiraSilva
```

---

### Corpo da Issue (Body):

```markdown
### Contexto e Problema
A tela de detalhes da feira (FeiraDetailView.vue) apresenta um salto abrupto de layout (layout shift) durante o carregamento dos dados da API em conexões lentas (3G/offline), violando os princípios de feedback visual suave do Design System.

### Proposta de Solucao
Implementar um componente de Skeleton Screen pulsante que replique a silhueta do cabeçalho da feira, lista de barracas e mapa enquanto a store useFeiraStore estiver no estado de carregamento (isLoading).

### Dependencias
- Nenhuma dependencia de backend. O endpoint GET /api/feiras/{id} já está estável.

### Escopo e Dominios/Arquivos Afetados
- Dominio principal: feira
- Modulos: frontend/src/views/public
- Arquivos afetados:
  - `frontend/src/views/public/FeiraDetailView.vue`
  - `frontend/src/components/feira/SkeletonFeiraDetail.vue`

### Contratos e DTOs
Consumo da store existente:
```typescript
interface FeiraDetailState {
  feira: FeiraResponse | null
  carregando: boolean
}
```

### Criterios de Aceite (Definition of Done)
- [ ] Criado componente SkeletonFeiraDetail.vue com animacao pulsante usando tokens semanticos do tema
- [ ] Proibido o uso de spinner circular abstrato (em conformidade com a politica Anti-Spinner do Design System)
- [ ] Exibicao condicional limpa com v-if="carregando" e transicao suave para os dados reais
- [ ] Validado nos modos Light e Dark sem cores hardcoded (#fff/#000)
- [ ] Build do frontend executado sem erros via `npm run build`

### Responsaveis
- Responsavel: @AntonnyCaldeiraSilva
```
