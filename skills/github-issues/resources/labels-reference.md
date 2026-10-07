# Catálogo de Labels do Repositório Mosaico (`Mosaico-br/Mosaico`)

Este documento serve como referência rápida para seleção de labels ao abrir issues. Toda issue **DEVE** conter pelo menos 4 labels: Área, Tipo, Prioridade e Domínio.

---

## 1. Labels de Área (Obrigatória: ao menos uma)
- `backend`: Módulo Spring Boot (Java 25, PostgreSQL, JPA, controllers, services).
- `frontend`: Aplicação Web/Mobile Vue 3 (Vite, TypeScript, Pinia, Capacitor).

---

## 2. Labels de Tipo (Obrigatória: selecione uma)
- `feature`: Nova funcionalidade ou novo endpoint/tela.
- `bug`: Correção de comportamento inesperado ou defeito.
- `enhancement`: Melhoria de funcionalidade já existente.
- `documentation`: Adição ou atualização de documentação técnica, specs ou READMEs.
- `security`: Ajustes de segurança, RBAC, validações de autorização ou hardening.

---

## 3. Labels de Prioridade (Obrigatória: selecione uma)
- `priority: high`: Bloqueante ou de impacto crítico para a entrega/usuário.
- `priority: medium`: Relevância intermediária, fluxo padrão de desenvolvimento.
- `priority: low`: Polimento, débito técnico menor ou baixa urgência.

---

## 4. Labels de Domínio (Obrigatória: selecione a área de negócio correspondente)
- `domain: auth`: Autenticação, JWT, credenciais, roles, recuperação de acesso.
- `domain: admin-auth`: Funcionalidades e acessos restritos a administradores e gerentes.
- `domain: feira`: Feiras municipais, horários, localização, vinculação.
- `domain: mapa-feira`: Visualizador do mapa de feira, disposição espacial de barracas, declinação magnética.
- `domain: catalog`: Produtos, categorias, fotos, vitrine e precificação.
- `domain: product-stock`: Controle e dedução de estoque de itens.
- `domain: feirante`: Perfil, barraca e operações do feirante/artesão.
- `domain: cliente`: Fluxos voltados aos compradores e visitantes.
- `domain: comunidade`: Painel de eventos comunitários, notícias e interações sociais.
- `domain: reservas`: Reservas de espaços físicos ou bancadas.
- `domain: ratings`: Avaliações e feedbacks de produtos e barracas.
- `domain: push-notifications`: Notificações Web Push (VAPID / Capacitor).
- `domain: b2b`: Funcionalidades institucionais, lojistas parceiros e pontos de coleta parceiros.

---

## 5. Labels Auxiliares / Especiais (Opcionais)
- `accessibility`: Ajustes de acessibilidade (WCAG AA, leitores de tela, navegação por teclado).
- `good first issue`: Adequada para contribuidores iniciantes.
- `help wanted`: Requer atenção adicional ou suporte de terceiros.
- `duplicate`: Issue duplicada.
- `invalid`: Fora de conformidade ou escopo.
- `wontfix`: Não será implementada.
