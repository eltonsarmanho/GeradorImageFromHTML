#!/usr/bin/env python3
"""
Script para gerar HTML de carrossel Instagram - Prêmio Educador Transformador 2026.

Contexto: FASI conquistou o 2º Lugar na etapa estadual do Pará na categoria
Gestão Educacional Transformadora com o projeto:
"FasiTech: Automação e Inteligência Artificial na Gestão Acadêmica"

Gera 6 slides (1080x1350px) com a identidade visual do Prêmio.
Saída: ScriptSebrae/html/
"""

from __future__ import annotations

import base64
import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Caminhos
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).parent
HTML_DIR = SCRIPT_DIR / "html"

FOTO1 = SCRIPT_DIR / "Foto1.jpg"
FOTO2 = SCRIPT_DIR / "Foto2.jpg"
FOTO3 = SCRIPT_DIR / "Foto3.jpg"
LOGO_FASI = Path(__file__).parent.parent / "html" / "fasiOficial.png"
LOGO_BETT = SCRIPT_DIR / "bet.png"
LOGO_SEBRAE = SCRIPT_DIR / "sebrae.png"
LOGO_SIGNIFICARE = SCRIPT_DIR / "significare.png"

# ---------------------------------------------------------------------------
# Paleta – extraída da identidade visual do Prêmio Educador Transformador
# ---------------------------------------------------------------------------
COR_MAGENTA   = "#E31B7B"   # Rosa/magenta principal do prêmio
COR_LARANJA   = "#F47920"   # Laranja secundário
COR_VERDE     = "#8DC63F"   # Verde
COR_AZUL_CLARO= "#00A5CE"   # Azul claro
COR_ROXO      = "#7B3097"   # Roxo
COR_AZUL_DARK = "#1A2240"   # Navy escuro (títulos)
COR_FASI_AZUL = "#0000FF"   # Azul institucional FASI


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------
def encode_image(path: Path, mime: str | None = None) -> str:
    """Converte imagem para data URI base64."""
    if not path.exists():
        raise FileNotFoundError(f"Imagem não encontrada: {path}")
    if mime is None:
        ext = path.suffix.lower()
        mime = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png"}.get(ext.lstrip("."), "png")
    data = base64.b64encode(path.read_bytes()).decode()
    return f"data:image/{mime};base64,{data}"


def mosaic_bg(opacity: float = 1.0) -> str:
    """
    Retorna o HTML dos quadrados coloridos do canto superior e inferior
    que compõem a identidade visual do Prêmio Educador Transformador.
    """
    cols = [COR_LARANJA, "#F0F0F0", COR_VERDE, COR_MAGENTA,
            "#F0F0F0", COR_AZUL_CLARO, COR_ROXO, "#F0F0F0",
            COR_MAGENTA, COR_LARANJA, "#F0F0F0", COR_VERDE]
    size = 65  # largura/altura de cada quadrado
    gap = 0
    # Linha superior – 4 colunas × 3 linhas
    blocks_top = ""
    for row in range(3):
        for col in range(4):
            idx = (row * 4 + col) % len(cols)
            x = col * (size + gap)
            y = row * (size + gap)
            blocks_top += (
                f'<div style="position:absolute;left:{x}px;top:{y}px;'
                f'width:{size}px;height:{size}px;'
                f'background:{cols[idx]};opacity:{opacity};"></div>'
            )
    # Canto direito superior
    blocks_right_top = ""
    for row in range(3):
        for col in range(4):
            idx = (row * 4 + col + 3) % len(cols)
            x = 1080 - (4 - col) * (size + gap)
            y = row * (size + gap)
            blocks_right_top += (
                f'<div style="position:absolute;left:{x}px;top:{y}px;'
                f'width:{size}px;height:{size}px;'
                f'background:{cols[idx]};opacity:{opacity};"></div>'
            )
    # Linha inferior esquerda
    blocks_bot = ""
    for row in range(3):
        for col in range(4):
            idx = (row * 4 + col + 6) % len(cols)
            x = col * (size + gap)
            y = 1350 - (3 - row) * (size + gap)
            blocks_bot += (
                f'<div style="position:absolute;left:{x}px;top:{y}px;'
                f'width:{size}px;height:{size}px;'
                f'background:{cols[idx]};opacity:{opacity};"></div>'
            )
    # Linha inferior direita
    blocks_bot_r = ""
    for row in range(3):
        for col in range(4):
            idx = (row * 4 + col + 2) % len(cols)
            x = 1080 - (4 - col) * (size + gap)
            y = 1350 - (3 - row) * (size + gap)
            blocks_bot_r += (
                f'<div style="position:absolute;left:{x}px;top:{y}px;'
                f'width:{size}px;height:{size}px;'
                f'background:{cols[idx]};opacity:{opacity};"></div>'
            )
    return blocks_top + blocks_right_top + blocks_bot + blocks_bot_r


def award_logo_svg() -> str:
    """
    SVG inline que reproduz o logotipo textual do Prêmio Educador Transformador.
    Arrow (◄) antes de EDUCADOR é característica da marca.
    """
    return """
    <div style="text-align:center; line-height:1.1;">
      <div style="font-family:'Montserrat',sans-serif; font-weight:700;
                  font-size:28px; color:#555; letter-spacing:6px; text-transform:uppercase;
                  margin-bottom:4px;">PRÊMIO</div>
      <div style="font-family:'Montserrat',sans-serif; font-weight:900;
                  font-size:66px; color:{navy}; text-transform:uppercase; letter-spacing:-1px;
                  display:flex; align-items:center; justify-content:center; gap:8px;">
        <span style="color:{magenta}; font-size:54px;">◄</span>EDUCADOR
      </div>
      <div style="font-family:'Montserrat',sans-serif; font-weight:900;
                  font-size:66px; color:{navy}; text-transform:uppercase; letter-spacing:-1px;">
        TRANSF<span style="color:{magenta};">O</span>RMADOR
      </div>
      <div style="font-family:'Montserrat',sans-serif; font-weight:600;
                  font-size:26px; color:{magenta}; letter-spacing:4px; margin-top:8px;">
        3ª EDIÇÃO
      </div>
    </div>
    """.replace("{navy}", COR_AZUL_DARK).replace("{magenta}", COR_MAGENTA)


def logos_parceiros_html(fasi_b64: str, bett_b64: str, sebrae_b64: str, sig_b64: str,
                          show_fasi: bool = True, height: int = 60) -> str:
    """Barra inferior com logos dos parceiros/organizadores."""
    fasi_tag = (
        f'<img src="{fasi_b64}" style="height:{height}px;object-fit:contain;">'
        if show_fasi else ""
    )
    return f"""
    <div style="display:flex; align-items:center; justify-content:center;
                gap:40px; padding:20px 60px; flex-wrap:wrap;">
      {fasi_tag}
      <img src="{bett_b64}"     style="height:{height}px;object-fit:contain;">
      <img src="{sebrae_b64}"   style="height:{height}px;object-fit:contain;">
      <img src="{sig_b64}"      style="height:{height}px;object-fit:contain;">
    </div>
    """


def base_html(title: str, body: str) -> str:
    """Estrutura HTML base com fonte e reset."""
    return f"""<!DOCTYPE html>
<html lang="pt-br">
<head>
  <meta charset="UTF-8">
  <title>{title}</title>
  <link href="https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,400;0,600;0,700;0,800;0,900;1,400&display=swap" rel="stylesheet">
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: #222;
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      font-family: 'Montserrat', sans-serif;
    }}
    .slide {{
      width: 1080px;
      height: 1350px;
      background: #fff;
      position: relative;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      box-shadow: 0 0 60px rgba(0,0,0,0.6);
    }}
  </style>
</head>
<body>
  <div class="slide">
    {body}
  </div>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Slide 01 – Capa (anúncio do prêmio)
# ---------------------------------------------------------------------------
def gerar_slide_01_capa(fasi_b64: str, bett_b64: str, sebrae_b64: str, sig_b64: str) -> str:
    mosaic = mosaic_bg(opacity=1.0)
    award  = award_logo_svg()
    logos  = logos_parceiros_html(fasi_b64, bett_b64, sebrae_b64, sig_b64,
                                   show_fasi=True, height=55)
    body = f"""
    <!-- Mosaico de fundo -->
    {mosaic}

    <!-- Conteúdo central -->
    <div style="position:relative; z-index:10; flex:1;
                display:flex; flex-direction:column;
                align-items:center; justify-content:center;
                padding: 200px 80px 30px 80px; gap:30px;">

      <!-- Badge 2º Lugar -->
      <div style="background:{COR_MAGENTA}; color:#fff; border-radius:60px;
                  padding:18px 55px; font-size:36px; font-weight:900;
                  letter-spacing:2px; text-transform:uppercase;
                  box-shadow: 0 8px 24px rgba(227,27,123,0.4);">
        🥈 2º LUGAR
      </div>

      <!-- Logo textual do prêmio -->
      <div style="margin: 10px 0;">
        {award}
      </div>

      <!-- Categoria -->
      <div style="background:{COR_AZUL_DARK}; color:#fff; border-radius:12px;
                  padding:16px 40px; text-align:center; max-width:700px;">
        <div style="font-size:18px; font-weight:600; letter-spacing:3px; opacity:0.8;
                    text-transform:uppercase; margin-bottom:6px;">CATEGORIA</div>
        <div style="font-size:30px; font-weight:800; line-height:1.2; text-transform:uppercase;">
          Gestão Educacional<br>Transformadora
        </div>
      </div>

      <!-- Etapa -->
      <div style="font-size:24px; font-weight:700; color:{COR_AZUL_DARK};
                  letter-spacing:1px; text-transform:uppercase;">
        Etapa Estadual — Pará
      </div>

    </div>

    <!-- Barra de logos inferior -->
    <div style="position:relative; z-index:10; border-top:3px solid #eee;">
      {logos}
    </div>
    """
    return base_html("Slide 01 – Capa", body)


# ---------------------------------------------------------------------------
# Slide 02 – Projeto FasiTech
# ---------------------------------------------------------------------------
def gerar_slide_02_projeto(fasi_b64: str, bett_b64: str, sebrae_b64: str, sig_b64: str) -> str:
    mosaic = mosaic_bg(opacity=1.0)
    logos  = logos_parceiros_html(fasi_b64, bett_b64, sebrae_b64, sig_b64,
                                   show_fasi=True, height=48)

    destaques = [
        ("🤖", "Automação de Processos", f"Uso de RPA para eliminar tarefas manuais repetitivas na gestão acadêmica"),
        ("🧠", "Inteligência Artificial", f"IA aplicada à análise de dados, previsão e apoio à tomada de decisão"),
        ("⚡", "Inovação Pública", f"Transformação digital em Faculdade Pública Federal — UFPA Cametá"),
    ]

    cards_html = ""
    for icon, titulo, desc in destaques:
        cards_html += f"""
        <div style="display:flex; align-items:flex-start; gap:20px;
                    background:#f9f9f9; border-radius:16px; padding:22px 26px;
                    border-left: 6px solid {COR_MAGENTA};">
          <div style="font-size:42px; line-height:1; flex-shrink:0;">{icon}</div>
          <div>
            <div style="font-size:22px; font-weight:800; color:{COR_AZUL_DARK};
                        margin-bottom:6px; text-transform:uppercase;">{titulo}</div>
            <div style="font-size:18px; font-weight:400; color:#444; line-height:1.5;">{desc}</div>
          </div>
        </div>"""

    body = f"""
    {mosaic}

    <div style="position:relative; z-index:10; flex:1;
                display:flex; flex-direction:column;
                padding: 195px 70px 20px 70px; gap:24px;">

      <!-- Header -->
      <div style="display:flex; align-items:center; gap:20px; margin-bottom:4px;">
        <img src="{fasi_b64}" style="height:64px; object-fit:contain;">
        <div style="width:2px; height:60px; background:{COR_MAGENTA};"></div>
        <div>
          <div style="font-size:16px; font-weight:600; color:{COR_MAGENTA};
                      letter-spacing:3px; text-transform:uppercase; margin-bottom:2px;">
            Prêmio Educador Transformador 3ª Ed.
          </div>
          <div style="font-size:14px; color:#777; font-weight:500;">2º Lugar · Etapa Estadual</div>
        </div>
      </div>

      <!-- Título do projeto -->
      <div>
        <div style="font-size:52px; font-weight:900; color:{COR_AZUL_DARK};
                    text-transform:uppercase; line-height:1.1; letter-spacing:-1px;">
          Fasi<span style="color:{COR_FASI_AZUL};">Tech</span>
        </div>
        <div style="font-size:22px; font-weight:600; color:{COR_MAGENTA};
                    margin-top:8px; line-height:1.4;">
          Automação e Inteligência Artificial<br>na Gestão Acadêmica
        </div>
      </div>

      <!-- Cards de destaque -->
      <div style="display:flex; flex-direction:column; gap:18px; flex:1;">
        {cards_html}
      </div>

    </div>

    <!-- Barra de logos inferior -->
    <div style="position:relative; z-index:10; border-top:3px solid #eee;">
      {logos}
    </div>
    """
    return base_html("Slide 02 – Projeto FasiTech", body)


# ---------------------------------------------------------------------------
# Slide genérico com foto
# ---------------------------------------------------------------------------
def gerar_slide_foto(
    foto_b64: str,
    fasi_b64: str,
    legenda_titulo: str,
    legenda_subtitulo: str,
    numero_slide: int,
    total_slides: int,
) -> str:
    mosaic = mosaic_bg(opacity=1.0)

    body = f"""
    {mosaic}

    <!-- Foto principal -->
    <div style="position:relative; z-index:5; flex:1; overflow:hidden;
                margin: 190px 40px 14px 40px; border-radius:20px;
                box-shadow: 0 12px 40px rgba(0,0,0,0.25);">
      <img src="{foto_b64}"
           style="width:100%; height:100%; object-fit:cover; object-position:center;">
      <!-- Overlay gradiente no rodapé da foto -->
      <div style="position:absolute; bottom:0; left:0; right:0; height:55%;
                  background:linear-gradient(to top, rgba(26,34,64,0.88) 0%, transparent 100%);
                  border-radius:0 0 20px 20px;"></div>
      <!-- Badge de slide -->
      <div style="position:absolute; top:18px; right:18px;
                  background:rgba(255,255,255,0.9); border-radius:30px;
                  padding:8px 20px; font-size:16px; font-weight:700; color:{COR_AZUL_DARK};">
        {numero_slide}/{total_slides}
      </div>
      <!-- Logo FASI no canto da foto -->
      <img src="{fasi_b64}"
           style="position:absolute; top:16px; left:16px; height:42px;
                  object-fit:contain; filter:brightness(0) invert(1); opacity:0.92;">
      <!-- Legenda sobre a foto -->
      <div style="position:absolute; bottom:28px; left:28px; right:28px;">
        <div style="font-size:32px; font-weight:900; color:#fff; line-height:1.2;
                    text-shadow:0 2px 8px rgba(0,0,0,0.5); margin-bottom:8px;">
          {legenda_titulo}
        </div>
        <div style="font-size:20px; font-weight:500; color:rgba(255,255,255,0.88);
                    text-shadow:0 1px 4px rgba(0,0,0,0.4); line-height:1.4;">
          {legenda_subtitulo}
        </div>
      </div>
    </div>

    <!-- Barra inferior com badge do prêmio -->
    <div style="position:relative; z-index:10; display:flex; align-items:center;
                justify-content:center; gap:16px; padding:14px 60px;
                border-top:3px solid {COR_MAGENTA};">
      <div style="width:10px; height:10px; border-radius:50%;
                  background:{COR_MAGENTA}; flex-shrink:0;"></div>
      <div style="font-size:17px; font-weight:700; color:{COR_AZUL_DARK};
                  text-transform:uppercase; letter-spacing:2px; text-align:center;">
        Prêmio Educador Transformador · 3ª Edição · 2º Lugar
      </div>
      <div style="width:10px; height:10px; border-radius:50%;
                  background:{COR_MAGENTA}; flex-shrink:0;"></div>
    </div>
    """
    return base_html(f"Slide {numero_slide:02d} – Foto", body)


# ---------------------------------------------------------------------------
# Slide 06 – Agradecimento / Encerramento
# ---------------------------------------------------------------------------
def gerar_slide_06_agradecimento(fasi_b64: str, bett_b64: str, sebrae_b64: str, sig_b64: str) -> str:
    mosaic = mosaic_bg(opacity=1.0)
    award  = award_logo_svg()

    equipe = [
        ("Elton Sarmanho Siqueira",   "Gestor / Coordenador"),
        ("Carlos dos Santos Portela", "Desenvolvedor"),
        ("Alexandre Reis Fernandes",  "Desenvolvedor"),
    ]
    equipe_html = ""
    for nome, cargo in equipe:
        equipe_html += f"""
        <div style="display:flex; align-items:center; gap:14px;">
          <div style="width:8px; height:8px; border-radius:50%;
                      background:{COR_MAGENTA}; flex-shrink:0;"></div>
          <div>
            <span style="font-size:20px; font-weight:700; color:{COR_AZUL_DARK};">{nome}</span>
            <span style="font-size:16px; color:#777; margin-left:8px;">— {cargo}</span>
          </div>
        </div>"""

    body = f"""
    {mosaic}

    <div style="position:relative; z-index:10; flex:1;
                display:flex; flex-direction:column;
                align-items:center; justify-content:center;
                padding: 195px 80px 20px 80px; gap:28px;">

      <!-- Obrigado -->
      <div style="text-align:center;">
        <div style="font-size:80px; font-weight:900; color:{COR_MAGENTA};
                    text-transform:uppercase; letter-spacing:-2px; line-height:1;">
          Obrigado!
        </div>
        <div style="font-size:22px; font-weight:500; color:#555; margin-top:12px; line-height:1.5;">
          Uma conquista da equipe <strong style="color:{COR_FASI_AZUL};">FASI</strong> que acredita<br>
          na transformação da educação pública.
        </div>
      </div>

      <!-- Logo do prêmio menor -->
      <div style="transform:scale(0.72); transform-origin:center top;">
        {award}
      </div>

      <!-- Equipe -->
      <div style="width:100%; background:#f5f5f5; border-radius:16px;
                  padding:24px 32px; display:flex; flex-direction:column; gap:14px;">
        <div style="font-size:16px; font-weight:700; color:{COR_MAGENTA};
                    letter-spacing:3px; text-transform:uppercase; margin-bottom:2px;">Equipe</div>
        {equipe_html}
      </div>

      <!-- Logos de parceiros -->
      <div style="display:flex; align-items:center; justify-content:center;
                  gap:32px; flex-wrap:wrap; padding:0 20px;">
        <img src="{fasi_b64}"      style="height:50px; object-fit:contain;">
        <img src="{bett_b64}"      style="height:50px; object-fit:contain;">
        <img src="{sebrae_b64}"    style="height:50px; object-fit:contain;">
        <img src="{sig_b64}"       style="height:50px; object-fit:contain;">
      </div>

    </div>
    """
    return base_html("Slide 06 – Agradecimento", body)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    HTML_DIR.mkdir(parents=True, exist_ok=True)

    print("🔄 Carregando imagens...")
    fasi_b64      = encode_image(LOGO_FASI)
    bett_b64      = encode_image(LOGO_BETT)
    sebrae_b64    = encode_image(LOGO_SEBRAE)
    sig_b64       = encode_image(LOGO_SIGNIFICARE)
    foto1_b64     = encode_image(FOTO1)
    foto2_b64     = encode_image(FOTO2)
    foto3_b64     = encode_image(FOTO3)

    slides = [
        (
            "slide_01_capa.html",
            gerar_slide_01_capa(fasi_b64, bett_b64, sebrae_b64, sig_b64),
        ),
        (
            "slide_02_projeto.html",
            gerar_slide_02_projeto(fasi_b64, bett_b64, sebrae_b64, sig_b64),
        ),
        (
            "slide_03_foto1.html",
            gerar_slide_foto(
                foto_b64=foto1_b64,
                fasi_b64=fasi_b64,
                legenda_titulo="2º Lugar — Etapa Estadual",
                legenda_subtitulo="Categoria: Gestão Educacional Transformadora · Pará",
                numero_slide=3,
                total_slides=6,
            ),
        ),
        (
            "slide_04_foto2.html",
            gerar_slide_foto(
                foto_b64=foto2_b64,
                fasi_b64=fasi_b64,
                legenda_titulo="Premiação com a organização",
                legenda_subtitulo="Instituto Significare · Bett Brasil · SEBRAE",
                numero_slide=4,
                total_slides=6,
            ),
        ),
        (
            "slide_05_foto3.html",
            gerar_slide_foto(
                foto_b64=foto3_b64,
                fasi_b64=fasi_b64,
                legenda_titulo="Todos os premiados — Pará",
                legenda_subtitulo="Prêmio Educador Transformador 3ª Edição · 2026",
                numero_slide=5,
                total_slides=6,
            ),
        ),
        (
            "slide_06_agradecimento.html",
            gerar_slide_06_agradecimento(fasi_b64, bett_b64, sebrae_b64, sig_b64),
        ),
    ]

    for filename, html in slides:
        out = HTML_DIR / filename
        out.write_text(html, encoding="utf-8")
        print(f"  ✅ {out.relative_to(SCRIPT_DIR.parent)}")

    print(f"\n✨ {len(slides)} slides gerados em: {HTML_DIR}")
    print("📌 Use gerar_posts.py --arquivo para converter em imagem.")


if __name__ == "__main__":
    main()
