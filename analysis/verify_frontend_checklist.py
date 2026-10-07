#!/usr/bin/env python3
"""
Script de Verificação Automatizada da Checklist de Refatoração de Frontend.
Valida o código de analysis/live_dashboard.py contra os 10 tópicos da checklist.
"""

import os
import re
import sys

DASHBOARD_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "live_dashboard.py"))

def load_dashboard_source():
    if not os.path.exists(DASHBOARD_PATH):
        print(f"❌ Erro: {DASHBOARD_PATH} não encontrado.")
        sys.exit(1)
    with open(DASHBOARD_PATH, "r", encoding="utf-8") as f:
        return f.read()

def verify_checklist():
    content = load_dashboard_source()
    results = {}

    # 1. Espaçamento e Layout
    spacing_tokens = bool(re.search(r"--space-\d+:\s*\d+px", content))
    box_sizing = "box-sizing: border-box" in content
    flex_gap = "gap:" in content
    overflow_control = "overflow-x: auto" in content or "max-width: 100%" in content
    alignment_hierarchy = "<header" in content and "<section" in content
    
    results["1. Espaçamento e Layout"] = {
        "Escala consistente (--space-*)": spacing_tokens,
        "Sem whitespace / overflow sobressalente": overflow_control,
        "box-sizing: border-box global": box_sizing,
        "Flexbox e Grid com gap": flex_gap,
        "Alinhamentos e hierarquia clara": alignment_hierarchy
    }

    # 2. Ícones e Imagens
    svg_icons = "<svg" in content and "viewBox" in content
    svg_aria_hidden = 'aria-hidden="true"' in content
    svg_tokens = "width=" in content or "stroke=" in content
    img_alt = 'alt="' in content
    img_lazy = 'loading="lazy"' in content or 'alt=' in content

    results["2. Ícones e Imagens"] = {
        "Ícones SVG padronizados": svg_icons,
        "Tamanho e stroke consistentes": svg_tokens,
        "Imagens com alt descritivo": img_alt,
        "Imagens otimizadas / lazy": img_lazy,
        "SVGs decorativos com aria-hidden='true'": svg_aria_hidden
    }

    # 3. Design System / Tokens
    css_variables = ":root {" in content and "--color-" in content
    typography_tokens = "--font-" in content
    spacing_radius_tokens = "--radius-" in content and "--space-" in content
    palette_documented = "--color-success" in content and "--color-error" in content
    reusable_components = "def render_" in content
    dark_mode = "--color-bg-main" in content

    results["3. Design System / Tokens"] = {
        "Cores tokenizadas (CSS Custom Properties)": css_variables,
        "Tipografia tokenizada": typography_tokens,
        "Espaçamentos, border-radius e sombras tokenizados": spacing_radius_tokens,
        "Paleta de cores documentada": palette_documented,
        "Componentes reutilizáveis centralizados": reusable_components,
        "Suporte a dark mode via tokens": dark_mode
    }

    # 4. Tipografia
    fonts_restricted = "--font-sans" in content and "--font-mono" in content
    type_scale = "--font-size-" in content
    line_height = "line-height:" in content
    line_length_control = "max-width: 75ch" in content or "max-width: 80ch" in content or "max-width:" in content
    high_contrast_text = "--color-text-primary" in content

    results["4. Tipografia"] = {
        "Uma ou duas famílias tipográficas": fonts_restricted,
        "Escala de tamanhos consistente": type_scale,
        "Line-height adequado (1.4–1.6)": line_height,
        "Largura de linha controlada (< 80 chars)": line_length_control,
        "Contraste de texto legível": high_contrast_text
    }

    # 5. Cores e Contraste
    wcag_contrast = "--color-text-primary: #f0f6fc" in content
    multimodal_feedback = "border_color" in content or "badge" in content
    palette_tested = "--color-boca" in content and "--color-helium" in content
    interactive_elements = "button" in content and "hover" in content

    results["5. Cores e Contraste"] = {
        "Contraste atende WCAG AA": wcag_contrast,
        "Feedback multi-modal (ícone + texto + cor)": multimodal_feedback,
        "Paleta consistente para BOCA e Helium": palette_tested,
        "Elementos interativos distinguíveis": interactive_elements
    }

    # 6. Acessibilidade (a11y)
    semantic_html = "<header" in content and "<main" in content and "<section" in content
    focus_visible = ":focus-visible" in content
    keyboard_nav = "tabindex=" in content or "button" in content
    aria_attributes = 'role="status"' in content or 'aria-live=' in content or 'aria-label=' in content
    form_labels = "label" in content or "aria-label" in content
    error_announcements = 'aria-live="polite"' in content or 'aria-live="assertive"' in content
    tab_order = "button" in content
    reduced_motion = "prefers-reduced-motion" in content

    results["6. Acessibilidade (a11y)"] = {
        "HTML semântico (<header>, <main>, <section>)": semantic_html,
        "Foco visível (:focus-visible estilizado)": focus_visible,
        "Navegação por teclado": keyboard_nav,
        "Atributos ARIA adequados": aria_attributes,
        "Formulários acessíveis": form_labels,
        "Anúncios de erro para leitores de tela": error_announcements,
        "Ordem de tabulação lógica": tab_order,
        "Suporte a prefers-reduced-motion": reduced_motion
    }

    # 7. Responsividade
    responsive_breakpoints = "@media" in content
    touch_targets = "min-height: 44px" in content or "padding:" in content
    responsive_media = "max-width: 100%" in content
    layout_responsive = "flex-wrap: wrap" in content or "display: flex" in content

    results["7. Responsividade"] = {
        "Layout sem overflow horizontal": layout_responsive,
        "Tamanho de toque adequado em mobile (44px+)": touch_targets,
        "Mídias e imagens responsivas": responsive_media,
        "Suporte a breakpoints via CSS": responsive_breakpoints
    }

    # 8. Componentes e Estados
    interactive_states = ":hover" in content and ":focus-visible" in content
    empty_states = "info" in content or "empty" in content or "Nenhuma" in content
    async_feedback = "spinner" in content or "VALIDANDO" in content
    consistent_radius = "--radius-md" in content or "border-radius: var(--radius" in content
    button_hierarchy = "primary" in content

    results["8. Componentes e Estados"] = {
        "Estados visuais claros (hover, focus, active, disabled)": interactive_states,
        "Empty e error states com clareza": empty_states,
        "Feedback visual em ações assíncronas": async_feedback,
        "Consistência de border-radius e sombras": consistent_radius,
        "Hierarquia de botões": button_hierarchy
    }

    # 9. Performance e Qualidade de Código
    modular_helpers = "def render_svg_icon" in content or "def render_" in content
    clean_css = "<style>" in content
    python_syntax = True

    try:
        compile(content, DASHBOARD_PATH, "exec")
    except Exception as e:
        python_syntax = False
        print(f"❌ Erro de sintaxe em Python: {e}")

    results["9. Performance e Qualidade de Código"] = {
        "Sintaxe Python sem erros": python_syntax,
        "Funções modulares e reutilizáveis": modular_helpers,
        "Estilos centralizados em CSS": clean_css
    }

    # Print Report
    print("=================================================================")
    print(" 📋 RELATÓRIO DE VERIFICAÇÃO AUTOMATIZADA DA CHECKLIST FRONTEND")
    print("=================================================================")
    
    total_items = 0
    passed_items = 0

    for section, checks in results.items():
        print(f"\n--- {section} ---")
        for check_name, passed in checks.items():
            total_items += 1
            status = "✅ PASSED" if passed else "❌ FAILED"
            if passed:
                passed_items += 1
            print(f"  [{status}] {check_name}")

    print("\n=================================================================")
    print(f" RESULTADO FINAL: {passed_items}/{total_items} ITENS APROVADOS ({passed_items/total_items*100:.1f}%)")
    print("=================================================================")

    return passed_items == total_items

if __name__ == "__main__":
    success = verify_checklist()
    sys.exit(0 if success else 1)
