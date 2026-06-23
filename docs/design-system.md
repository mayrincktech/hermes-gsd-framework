# Design System

## Design Philosophy

### Inspiração
- **Apple HIG** — minimalista, premium, espaço em branco
- **Linear** — clean, escuro elegante, tipografia forte
- **Notion** — flexível, foco no conteúdo
- **Stripe** — profissional, confiança visual

### Características Obrigatórias
- Mobile-first (375px base)
- Minimalista
- Premium
- Muito espaço em branco
- Máx 3 cores principais
- Tipografia forte
- Hierarquia visual clara
- Espaçamento consistente

### Proibido
- Bootstrap visual
- Material Design padrão
- Cards genéricos
- Tabelas sem tratamento
- Mais de 3 cores principais
- Interfaces genéricas
- Cards excessivos
- Muitas bordas
- Formulários longos sem quebra

## UX Persona

Ativar antes de qualquer design:

> Você é um Product Designer Senior. Seu objetivo NÃO é apenas fazer a tela funcionar. Objetivos: visual premium, experiência semelhante a apps líderes, hierarquia visual clara, espaçamento consistente, mobile-first, acessibilidade, conversão e retenção. Referências: Stripe, Linear, Notion, Airbnb, Apple, Arc Browser.

## Design System Template

Todo projeto DEVE ter `DESIGN-SYSTEM.md` antes de qualquer task de UI.

### Border Radius
- 16px — cards, containers
- 8px — inputs, buttons
- 999px — pills, badges

### Spacing (8px base)
8px → 16px → 24px → 32px → 48px → 64px

### Typography
| Level | Size | Weight | Tracking |
|---|---|---|---|
| Heading XL | 32px | 700 | -0.02em |
| Heading L | 24px | 700 | -0.01em |
| Heading M | 20px | 600 | — |
| Body | 16px | 400 | 1.5 line-height |
| Caption | 14px | 400 | 1.4 line-height |
| Label | 12px | 500 | uppercase |

### Sombras (máx 3)
- sm: `0 1px 2px rgba(0,0,0,0.05)`
- md: `0 4px 6px rgba(0,0,0,0.07)`
- lg: `0 10px 15px rgba(0,0,0,0.1)`

### Cores (máx 3 principais)
- Primária, Secundária, Neutras (gray-50 → gray-900)
- Sucesso: green-500 | Erro: red-500 | Aviso: amber-500

## UX Score

6 critérios objetivos, 0-10 cada, **mínimo 42/60** para aprovar.

| Critério | Descrição |
|---|---|
| Hierarquia Visual | Elementos importantes se destacam? Ordem de leitura clara? |
| Legibilidade | Contraste, tamanho de fonte, espaçamento entre linhas |
| Espaçamento | Segue escala? Generoso e consistente? |
| Mobile Experience | 375px? Touch targets ≥44px? Sem scroll horizontal? |
| Acessibilidade | ARIA, contraste WCAG AA, navegação por teclado |
| Premium Feel | Profissional? Espaço em branco? Micro-interações? |

## Wireframe Format

Todo wireframe começa por mobile (375px). Desktop é adaptação.

```
Tela: [Nome] (Mobile-first — 375px)
Referências: [app1] (layout), [app2] (cards), [app3] (tipografia)

┌───────────────────────┐
│ [conteúdo mobile]     │
└───────────────────────┘

Desktop (≥768px) — adaptação:
┌─────────────────────────────────────┐
│ [conteúdo desktop]                  │
└─────────────────────────────────────┘
```

## Regras de Wireframe

1. **Mobile primeiro** — sempre 375px antes de desktop
2. **3 referências obrigatórias** — citar apps de inspiração
3. **Aprovação antes de código** — wireframe deve ser aprovado antes de EXECUTE
4. **Tasks de UI referenciam wireframe** — toda task de UI cita qual wireframe implementa
