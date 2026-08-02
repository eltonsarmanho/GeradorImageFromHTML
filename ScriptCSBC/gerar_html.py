#!/usr/bin/env python3
"""
Script para gerar arquivos HTML do carrossel Instagram da FASI
sobre a participação dos docentes no CSBC 2026.

Gera 3 slides:
  1. Capa — Banner do evento + título
  2. Artigos — Lista dos 4 trabalhos apresentados
  3. Destaque — Menção Honrosa no WASHES
"""

import os
import shutil
import base64

# ── Diretórios ──────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FOTOS_DIR = os.path.join(BASE_DIR, "Fotos")
HTML_DIR = os.path.join(BASE_DIR, "html")


def garantir_assets():
    """Cria pasta html/ e copia logos + fotos para ela."""
    os.makedirs(HTML_DIR, exist_ok=True)

    # Logos vindos do projeto raiz
    logos_dir = os.path.join(BASE_DIR, "..", "html")
    for logo in ("fasiOficial.png", "ufpa.png"):
        src = os.path.join(logos_dir, logo)
        dst = os.path.join(HTML_DIR, logo)
        if os.path.exists(src) and not os.path.exists(dst):
            shutil.copy2(src, dst)

    # Fotos do CSBC
    for foto in os.listdir(FOTOS_DIR):
        src = os.path.join(FOTOS_DIR, foto)
        dst = os.path.join(HTML_DIR, foto)
        if not os.path.exists(dst):
            shutil.copy2(src, dst)


# ── CSS Comum (temática CSBC 2026 — azul/verde/natureza) ────────────────────
CSS_COMMON = """
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;800;900&family=Inter:wght@300;400;500;600;700&display=swap');

    :root {
        --csbc-dark: #0a1628;
        --csbc-blue: #1a4b8c;
        --csbc-mid: #2563a8;
        --csbc-light: #3b82d6;
        --csbc-accent: #38bdf8;
        --csbc-green: #22c55e;
        --fasi-blue: #0000FF;
        --gold: #fbbf24;
        --text-white: #f1f5f9;
        --text-muted: #94a3b8;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
        display: flex; justify-content: center; align-items: center;
        background: #111; min-height: 100vh;
        font-family: 'Inter', sans-serif;
    }

    .slide {
        width: 1080px; height: 1080px;
        position: relative; overflow: hidden;
        display: flex; flex-direction: column;
        background: linear-gradient(160deg, var(--csbc-dark) 0%, #0f2847 40%, #122f54 70%, #0a1e3d 100%);
        color: var(--text-white);
    }

    /* Efeito de brilho atmosférico */
    .slide::before {
        content: "";
        position: absolute; inset: 0;
        background:
            radial-gradient(ellipse 600px 400px at 20% 10%, rgba(56,189,248,0.12) 0%, transparent 70%),
            radial-gradient(ellipse 500px 500px at 85% 85%, rgba(34,197,94,0.08) 0%, transparent 70%);
        z-index: 0;
        pointer-events: none;
    }

    /* Grid decorativo sutil */
    .slide::after {
        content: "";
        position: absolute; inset: 0;
        background-image:
            linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px);
        background-size: 60px 60px;
        z-index: 0;
        pointer-events: none;
    }

    .slide > * { position: relative; z-index: 1; }

    /* Header com logos */
    .header {
        display: flex; justify-content: space-between; align-items: center;
        padding: 40px 50px 20px;
    }
    .header img { height: 60px; object-fit: contain; }
    .header .logo-fasi { filter: brightness(0) invert(1); height: 50px; }
    .header .logo-ufpa { height: 65px; }

    /* Footer */
    .footer {
        padding: 20px 50px 30px;
        display: flex; justify-content: space-between; align-items: center;
        margin-top: auto;
    }
    .footer-bar {
        position: absolute; bottom: 0; left: 0; right: 0; height: 6px;
        background: linear-gradient(90deg, var(--csbc-accent), var(--csbc-green), var(--csbc-accent));
    }
    .footer-text {
        font-size: 16px; color: var(--text-muted);
        font-weight: 500; letter-spacing: 0.5px;
    }
    .footer-badge {
        background: rgba(56,189,248,0.15);
        border: 1px solid rgba(56,189,248,0.3);
        border-radius: 20px; padding: 6px 18px;
        font-size: 14px; font-weight: 600;
        color: var(--csbc-accent); letter-spacing: 1px;
    }

    /* Tag CSBC */
    .csbc-tag {
        display: inline-block;
        background: linear-gradient(135deg, var(--csbc-blue) 0%, var(--csbc-mid) 100%);
        color: #fff; font-family: 'Montserrat', sans-serif;
        font-weight: 800; font-size: 18px;
        padding: 8px 22px; border-radius: 8px;
        letter-spacing: 2px; text-transform: uppercase;
    }
"""


def gerar_slide1_capa():
    """Slide 1 — Capa do carrossel com foto do evento."""
    return f"""<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>CSBC 2026 — FASI presente</title>
    <style>
    {CSS_COMMON}

    .hero {{
        flex: 1; display: flex; flex-direction: column;
        justify-content: center; align-items: center;
        text-align: center; padding: 0 50px; gap: 28px;
    }}

    .event-photo {{
        width: 880px; height: 340px; border-radius: 18px;
        overflow: hidden; box-shadow: 0 20px 60px rgba(0,0,0,0.5);
        border: 2px solid rgba(56,189,248,0.2);
    }}
    .event-photo img {{
        width: 100%; height: 100%; object-fit: cover;
    }}

    .hero-title {{
        font-family: 'Montserrat', sans-serif;
        font-weight: 900; font-size: 52px; line-height: 1.15;
        text-transform: uppercase; letter-spacing: -1px;
    }}
    .hero-title .accent {{
        background: linear-gradient(90deg, var(--csbc-accent), var(--csbc-green));
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text;
    }}

    .hero-subtitle {{
        font-size: 24px; color: var(--text-muted);
        font-weight: 400; max-width: 750px; line-height: 1.5;
    }}
    .hero-subtitle strong {{ color: #fff; font-weight: 600; }}

    .swipe-cta {{
        display: flex; align-items: center; gap: 14px;
        background: rgba(56,189,248,0.1);
        border: 1px solid rgba(56,189,248,0.25);
        padding: 14px 32px; border-radius: 50px;
        margin-top: 10px;
    }}
    .swipe-cta span {{
        font-weight: 700; font-size: 18px; color: var(--csbc-accent);
        text-transform: uppercase; letter-spacing: 2px;
    }}
    .swipe-arrow {{
        font-size: 28px; color: var(--csbc-accent);
        animation: bounceRight 1.5s infinite ease-in-out;
    }}
    @keyframes bounceRight {{
        0%, 100% {{ transform: translateX(0); }}
        50% {{ transform: translateX(10px); }}
    }}
    </style>
</head>
<body>
    <div class="slide">
        <div class="header">
            <img src="ufpa.png" alt="UFPA" class="logo-ufpa">
            <div class="csbc-tag">CSBC 2026</div>
            <img src="fasiOficial.png" alt="FASI" class="logo-fasi">
        </div>

        <div class="hero">
            <div class="event-photo">
                <img src="Evento.png" alt="CSBC 2026 — Gramado">
            </div>

            <h1 class="hero-title">
                A FASI <span class="accent">marcou presença</span><br>
                no CSBC 2026
            </h1>

            <p class="hero-subtitle">
                Nossos docentes apresentaram <strong>4 trabalhos científicos</strong>
                no maior congresso de Computação da América Latina,
                em <strong>Gramado — RS</strong>.
            </p>

            <div class="swipe-cta">
                <span>Arraste para saber mais</span>
                <span class="swipe-arrow">→</span>
            </div>
        </div>

        <div class="footer">
            <span class="footer-text">@faboratoriofasi</span>
            <span class="footer-badge">19–23 JULHO 2026</span>
        </div>
        <div class="footer-bar"></div>
    </div>
</body>
</html>"""


def gerar_slide2_artigos():
    """Slide 2 — Lista dos artigos apresentados com foto dos professores."""

    artigos = [
        {
            "titulo": "No Farelo: Jogo Digital para Educação Ambiental sobre o Desmatamento e seus Efeitos Nocivos na Amazônia",
            "autores": "Fabrício Faria & Carlos Portela",
            "evento": "CSBC 2026",
        },
        {
            "titulo": "Aplicação do Software barometroR para Monitoramento da Sustentabilidade no Sudeste Paraense",
            "autores": "Fabrício Faria",
            "evento": "CSBC 2026",
        },
        {
            "titulo": "Benchmark de Ferramentas de OCR para Digitalização de Registros Imobiliários",
            "autores": "Carlos Portela & Elton Sarmanho",
            "evento": "CSBC 2026",
        },
        {
            "titulo": "Bad Smells of Communication in Multidisciplinary Agile Teams of a Remote Software Project",
            "autores": "Carlos Portela",
            "evento": "WASHES · 🏅 Menção Honrosa",
        },
    ]

    items_html = ""
    for i, art in enumerate(artigos, 1):
        badge = "🏅" if "Menção" in art["evento"] else f"0{i}"
        items_html += f"""
            <div class="article-card">
                <div class="card-number">{badge}</div>
                <div class="card-body">
                    <p class="card-title">{art['titulo']}</p>
                    <p class="card-authors">👤 {art['autores']}</p>
                    <span class="card-event">{art['evento']}</span>
                </div>
            </div>"""

    return f"""<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Artigos CSBC 2026</title>
    <style>
    {CSS_COMMON}

    .content {{
        flex: 1; display: flex; flex-direction: column;
        padding: 10px 50px; gap: 16px;
    }}

    .section-label {{
        font-family: 'Montserrat', sans-serif;
        font-weight: 800; font-size: 30px;
        text-transform: uppercase; letter-spacing: 1px;
        text-align: center;
    }}
    .section-label .accent {{
        background: linear-gradient(90deg, var(--csbc-accent), var(--csbc-green));
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text;
    }}

    .photo-row {{
        display: flex; justify-content: center; gap: 0;
        margin-bottom: 4px;
    }}
    .photo-circle {{
        width: 100px; height: 100px; border-radius: 50%;
        overflow: hidden; border: 3px solid var(--csbc-accent);
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    }}
    .photo-circle img {{ width: 100%; height: 100%; object-fit: cover; }}

    .article-card {{
        display: flex; gap: 18px; align-items: flex-start;
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px; padding: 18px 22px;
        transition: all 0.3s;
    }}
    .article-card:hover {{
        background: rgba(56,189,248,0.06);
        border-color: rgba(56,189,248,0.2);
    }}

    .card-number {{
        font-family: 'Montserrat', sans-serif;
        font-weight: 900; font-size: 26px;
        color: var(--csbc-accent); min-width: 44px;
        text-align: center; padding-top: 2px;
    }}

    .card-body {{ flex: 1; }}

    .card-title {{
        font-weight: 600; font-size: 17px;
        line-height: 1.35; margin-bottom: 6px; color: #e2e8f0;
    }}
    .card-authors {{
        font-size: 14px; color: var(--text-muted);
        margin-bottom: 6px;
    }}
    .card-event {{
        display: inline-block; font-size: 12px; font-weight: 700;
        color: var(--csbc-green); text-transform: uppercase;
        letter-spacing: 1px;
        background: rgba(34,197,94,0.1);
        padding: 3px 10px; border-radius: 6px;
    }}
    </style>
</head>
<body>
    <div class="slide">
        <div class="header">
            <img src="ufpa.png" alt="UFPA" class="logo-ufpa">
            <div class="csbc-tag">CSBC 2026</div>
            <img src="fasiOficial.png" alt="FASI" class="logo-fasi">
        </div>

        <div class="content">
            <div class="photo-row">
                <div class="photo-circle">
                    <img src="Fabricio_Carlos.jpeg" alt="Fabrício e Carlos">
                </div>
            </div>

            <h2 class="section-label">
                Trabalhos <span class="accent">Apresentados</span>
            </h2>

            <div class="articles-list">
                {items_html}
            </div>
        </div>

        <div class="footer">
            <span class="footer-text">Prof. Carlos Portela · Prof. Fabrício Faria · Prof. Elton Sarmanho</span>
            <span class="footer-badge">GRAMADO — RS</span>
        </div>
        <div class="footer-bar"></div>
    </div>
</body>
</html>"""


def gerar_slide3_mencao():
    """Slide 3 — Destaque da Menção Honrosa + mensagem de encerramento."""
    return f"""<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Menção Honrosa — WASHES</title>
    <style>
    {CSS_COMMON}

    .content {{
        flex: 1; display: flex; flex-direction: column;
        justify-content: center; align-items: center;
        text-align: center; padding: 0 50px; gap: 24px;
    }}

    .trophy {{ font-size: 56px; }}

    .highlight-title {{
        font-family: 'Montserrat', sans-serif;
        font-weight: 900; font-size: 42px;
        text-transform: uppercase; line-height: 1.15;
    }}
    .highlight-title .gold {{
        color: var(--gold);
    }}

    .cert-frame {{
        width: 820px; border-radius: 16px;
        overflow: hidden; box-shadow: 0 20px 60px rgba(0,0,0,0.5);
        border: 2px solid rgba(251,191,36,0.3);
    }}
    .cert-frame img {{ width: 100%; display: block; }}

    .award-detail {{
        font-size: 18px; color: var(--text-muted); line-height: 1.6;
        max-width: 800px;
    }}
    .award-detail strong {{ color: #fff; }}

    .closing-msg {{
        background: rgba(56,189,248,0.08);
        border: 1px solid rgba(56,189,248,0.2);
        border-radius: 14px; padding: 20px 36px;
        max-width: 800px;
    }}
    .closing-msg p {{
        font-size: 19px; font-weight: 500;
        color: var(--text-white); line-height: 1.5;
    }}
    .closing-msg .emoji {{ font-size: 22px; }}

    .people-photo {{
        display: flex; justify-content: center;
    }}
    .people-photo-frame {{
        width: 260px; height: 160px; border-radius: 14px;
        overflow: hidden; border: 2px solid rgba(56,189,248,0.2);
        box-shadow: 0 10px 40px rgba(0,0,0,0.4);
    }}
    .people-photo-frame img {{ width: 100%; height: 100%; object-fit: cover; }}
    </style>
</head>
<body>
    <div class="slide">
        <div class="header">
            <img src="ufpa.png" alt="UFPA" class="logo-ufpa">
            <div class="csbc-tag">CSBC 2026</div>
            <img src="fasiOficial.png" alt="FASI" class="logo-fasi">
        </div>

        <div class="content">
            <div class="trophy">🏆</div>

            <h1 class="highlight-title">
                <span class="gold">Menção Honrosa</span><br>
                no WASHES 2026
            </h1>

            <div class="cert-frame">
                <img src="MencaoHonrosa.jpeg" alt="Certificado Menção Honrosa">
            </div>

            <p class="award-detail">
                O artigo <strong>"Bad Smells of Communication in Multidisciplinary
                Agile Teams of a Remote Software Project"</strong>, do Prof. <strong>Carlos Portela</strong>,
                recebeu <strong>Menção Honrosa</strong> no XI WASHES.
            </p>

            <div class="closing-msg">
                <p>
                    <span class="emoji">🎓</span>
                    A FASI celebra a representatividade dos nossos docentes
                    no maior evento científico de Computação do Brasil!
                </p>
            </div>
        </div>

        <div class="footer">
            <span class="footer-text">XLVI Congresso da SBC · Gramado — RS</span>
            <span class="footer-badge">FASI · UFPA</span>
        </div>
        <div class="footer-bar"></div>
    </div>
</body>
</html>"""


def salvar_html(nome, conteudo):
    caminho = os.path.join(HTML_DIR, nome)
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(conteudo)
    print(f"  ✅  {nome}")


def main():
    print("=" * 60)
    print("  🎯  Gerador de Carrossel CSBC 2026 — Instagram FASI")
    print("=" * 60)

    print("\n📂 Copiando assets...")
    garantir_assets()

    print("\n📝 Gerando slides HTML...\n")
    salvar_html("Slide1_Capa.html", gerar_slide1_capa())
    salvar_html("Slide2_Artigos.html", gerar_slide2_artigos())
    salvar_html("Slide3_MencaoHonrosa.html", gerar_slide3_mencao())

    print(f"\n✨ Pronto! 3 slides gerados em: {HTML_DIR}")
    print("\n💡 Para converter em imagens, execute na raiz do projeto:")
    print("   python gerar_posts.py --plataforma instagram --arquivo ScriptCSBC/html/Slide1_Capa.html")
    print("   python gerar_posts.py --plataforma instagram --arquivo ScriptCSBC/html/Slide2_Artigos.html")
    print("   python gerar_posts.py --plataforma instagram --arquivo ScriptCSBC/html/Slide3_MencaoHonrosa.html")


if __name__ == "__main__":
    main()
