"""Tema visual do Gradio inspirado no design system da Binance
(canvas quase preto + amarelo como único acento de marca).

Referência: DESIGN-binance.md (paleta, tipografia e componentes extraídos do
site da Binance). BinanceNova/BinancePlex são fontes proprietárias — usamos
Inter como substituto aberto mais próximo, conforme a nota do próprio
documento de referência ("Note on Font Substitutes").
"""

import gradio as gr

# Paleta extraída de DESIGN-binance.md
_CANVAS_DARK = "#0b0e11"
_SURFACE_CARD_DARK = "#1e2329"
_SURFACE_ELEVATED_DARK = "#2b3139"
_HAIRLINE_ON_DARK = "#2b3139"
_BODY_TEXT = "#eaecef"
_MUTED_TEXT = "#707a8a"
_PRIMARY_YELLOW = "#fcd535"
_PRIMARY_YELLOW_ACTIVE = "#f0b90b"
_ON_PRIMARY = "#181a20"
_ON_DARK = "#ffffff"
_TRADING_UP = "#0ecb81"

FIN_THEME = gr.themes.Base(
    font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif", "system-ui", "sans-serif"],
    font_mono=[
        gr.themes.GoogleFont("JetBrains Mono"),
        "ui-monospace",
        "monospace",
    ],
    radius_size=gr.themes.sizes.radius_md,
).set(
    body_background_fill=_CANVAS_DARK,
    body_background_fill_dark=_CANVAS_DARK,
    body_text_color=_BODY_TEXT,
    body_text_color_dark=_BODY_TEXT,
    body_text_color_subdued=_MUTED_TEXT,
    body_text_color_subdued_dark=_MUTED_TEXT,
    background_fill_primary=_SURFACE_CARD_DARK,
    background_fill_primary_dark=_SURFACE_CARD_DARK,
    background_fill_secondary=_SURFACE_ELEVATED_DARK,
    background_fill_secondary_dark=_SURFACE_ELEVATED_DARK,
    border_color_primary=_HAIRLINE_ON_DARK,
    border_color_primary_dark=_HAIRLINE_ON_DARK,
    border_color_accent=_PRIMARY_YELLOW,
    border_color_accent_dark=_PRIMARY_YELLOW,
    block_background_fill=_SURFACE_CARD_DARK,
    block_background_fill_dark=_SURFACE_CARD_DARK,
    block_border_color=_HAIRLINE_ON_DARK,
    block_border_color_dark=_HAIRLINE_ON_DARK,
    block_label_background_fill=_SURFACE_ELEVATED_DARK,
    block_label_background_fill_dark=_SURFACE_ELEVATED_DARK,
    block_label_text_color=_BODY_TEXT,
    block_label_text_color_dark=_BODY_TEXT,
    block_title_background_fill=_SURFACE_CARD_DARK,
    block_title_background_fill_dark=_SURFACE_CARD_DARK,
    panel_background_fill=_CANVAS_DARK,
    panel_background_fill_dark=_CANVAS_DARK,
    input_background_fill=_SURFACE_CARD_DARK,
    input_background_fill_dark=_SURFACE_CARD_DARK,
    input_border_color=_HAIRLINE_ON_DARK,
    input_border_color_dark=_HAIRLINE_ON_DARK,
    input_border_color_focus=_PRIMARY_YELLOW,
    input_border_color_focus_dark=_PRIMARY_YELLOW,
    button_primary_background_fill=_PRIMARY_YELLOW,
    button_primary_background_fill_dark=_PRIMARY_YELLOW,
    button_primary_background_fill_hover=_PRIMARY_YELLOW_ACTIVE,
    button_primary_background_fill_hover_dark=_PRIMARY_YELLOW_ACTIVE,
    button_primary_text_color=_ON_PRIMARY,
    button_primary_text_color_dark=_ON_PRIMARY,
    button_primary_text_color_hover=_ON_PRIMARY,
    button_primary_text_color_hover_dark=_ON_PRIMARY,
    button_primary_border_color=_PRIMARY_YELLOW,
    button_primary_border_color_dark=_PRIMARY_YELLOW,
    button_secondary_background_fill=_SURFACE_CARD_DARK,
    button_secondary_background_fill_dark=_SURFACE_CARD_DARK,
    button_secondary_text_color=_ON_DARK,
    button_secondary_text_color_dark=_ON_DARK,
    button_secondary_border_color=_HAIRLINE_ON_DARK,
    button_secondary_border_color_dark=_HAIRLINE_ON_DARK,
)

# CSS complementar: pill no botão primário (assinatura visual da Binance) e
# realce amarelo no cabeçalho/título, sem depender de classes internas
# frágeis do Gradio.
FIN_CSS = f"""
.gradio-container {{
    max-width: 1100px !important;
    margin: 0 auto !important;
}}
h1, h2, h3 {{
    letter-spacing: -0.3px;
}}
#fincomigo-header {{
    color: {_PRIMARY_YELLOW} !important;
    font-weight: 700 !important;
}}
button.primary {{
    border-radius: 9999px !important;
    font-weight: 600 !important;
}}
#fincomigo-badge {{
    display: inline-block;
    background: {_SURFACE_ELEVATED_DARK};
    color: {_TRADING_UP};
    border-radius: 8px;
    padding: 4px 12px;
    font-size: 12px;
    font-weight: 600;
}}
"""
