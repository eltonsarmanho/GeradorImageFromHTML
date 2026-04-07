import os

def render_slide(content, slide_num, total_slides, filename):
    dots = ""
    for i in range(1, total_slides + 1):
        if i == slide_num:
            dots += '<div class="dot active"></div>'
        else:
            dots += '<div class="dot"></div>'

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=1080, initial-scale=1.0">
    <title>Post Slide {slide_num}</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700;900&display=swap');
        
        body {{
            margin: 0;
            padding: 0;
            width: 1080px;
            height: 1080px;
            background-color: #ffffff;
            color: #333333;
            font-family: 'Roboto', sans-serif;
            display: flex;
            flex-direction: column;
            box-sizing: border-box;
            position: relative;
            overflow: hidden;
        }}

        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 50px 70px 20px;
            z-index: 10;
        }}

        .ufpa-logo {{
            font-size: 32px;
            font-weight: 900;
            color: #004c8f;
            display: flex;
            align-items: center;
            gap: 15px;
            letter-spacing: 1px;
        }}

        .ufpa-logo span {{
            color: #009342;
        }}

        .page-badge {{
            background-color: #fcb913;
            color: #004c8f;
            padding: 12px 25px;
            border-radius: 50px;
            font-weight: 900;
            font-size: 24px;
            box-shadow: 0 4px 10px rgba(252, 185, 19, 0.3);
        }}

        .content {{
            flex-grow: 1;
            padding: 30px 70px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            z-index: 10;
        }}

        h1 {{
            font-size: 65px;
            font-weight: 900;
            line-height: 1.15;
            color: #004c8f;
            margin-bottom: 30px;
        }}

        p {{
            font-size: 38px;
            line-height: 1.5;
            color: #444444;
            font-weight: 400;
            margin-top: 0;
            margin-bottom: 25px;
        }}

        .highlight-text {{
            color: #004c8f;
            font-weight: 700;
        }}

        .image-container {{
            width: 100%;
            height: 480px;
            border-radius: 30px;
            overflow: hidden;
            margin-top: 20px;
            box-shadow: 0 15px 30px rgba(0,0,0,0.1);
            position: relative;
        }}

        .image-container img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}

        .decorative-bar {{
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 25px;
            background: linear-gradient(to right, #004c8f 33%, #009342 33%, #009342 66%, #fcb913 66%);
            z-index: 20;
        }}

        .footer {{
            padding: 30px 70px 60px;
            display: flex;
            justify-content: space-between;
            font-size: 26px;
            font-weight: 700;
            color: #888888;
            z-index: 10;
        }}

        .slide-indicator {{
            display: flex;
            gap: 12px;
            align-items: center;
        }}

        .dot {{
            width: 14px;
            height: 14px;
            border-radius: 50%;
            background-color: #dddddd;
        }}

        .dot.active {{
            background-color: #004c8f;
            width: 35px;
            border-radius: 10px;
        }}

        /* Decorative shapes */
        .shape1 {{
            position: absolute;
            top: -100px;
            right: -100px;
            width: 400px;
            height: 400px;
            background-color: rgba(252, 185, 19, 0.15);
            border-radius: 50%;
            z-index: 1;
        }}

        .shape2 {{
            position: absolute;
            bottom: 100px;
            left: -150px;
            width: 350px;
            height: 350px;
            background-color: rgba(0, 147, 66, 0.08);
            border-radius: 50%;
            z-index: 1;
        }}

        .quote-box {{
            position: relative;
            background-color: #f4f8fb;
            border-left: 12px solid #004c8f;
            padding: 50px;
            border-radius: 0 30px 30px 0;
            margin-top: 20px;
            box-shadow: 0 10px 20px rgba(0,76,143,0.05);
        }}

        .quote-icon {{
            font-size: 100px;
            color: rgba(0, 76, 143, 0.2);
            position: absolute;
            top: -10px;
            left: 20px;
            z-index: 0;
            font-family: Georgia, serif;
            line-height: 1;
        }}

        .quote-text {{
            font-size: 36px;
            font-weight: 400;
            font-style: italic;
            color: #222222;
            margin-bottom: 30px;
            position: relative;
            z-index: 1;
            line-height: 1.4;
        }}

        .quote-author {{
            font-size: 28px;
            font-weight: 900;
            color: #009342;
            text-align: right;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        .grid-container {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 25px;
            margin-top: 10px;
        }}

        .grid-item {{
            background: #ffffff;
            padding: 30px;
            border-radius: 20px;
            border-left: 8px solid #fcb913;
            box-shadow: 0 8px 20px rgba(0,0,0,0.05);
        }}

        .grid-item.green {{
            border-left: 8px solid #009342;
        }}

        .grid-item.blue {{
            border-left: 8px solid #004c8f;
        }}

        .grid-item h3 {{
            margin: 0 0 10px 0;
            color: #333;
            font-size: 32px;
            font-weight: 900;
        }}
        
        .grid-item span {{
            display: block;
            margin-top: 10px;
            font-size: 24px;
            color: #666;
            font-weight: 700;
        }}

        .callout {{
            background-color: #004c8f;
            color: white;
            padding: 30px;
            border-radius: 20px;
            text-align: center;
            margin-top: 30px;
        }}

        .callout p {{
            color: white;
            margin: 0;
            font-weight: 700;
        }}
    </style>
</head>
<body>
    <div class="shape1"></div>
    <div class="shape2"></div>
    <div class="header">
        <div class="ufpa-logo">UNIVERSIDADE FEDERAL DO PARÁ <span>•</span> UFPA</div>
        <div class="page-badge">Campus Cametá</div>
    </div>
    
    <div class="content">
        {content}
    </div>

    <div class="footer">
        <div>@fasi.ufpa | ufpa.br</div>
        <div class="slide-indicator">
            {dots}
        </div>
    </div>
    <div class="decorative-bar"></div>
</body>
</html>"""

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)

def main():
    base_dir = "/home/nees/Documents/VSCodigo/GeradorImageFromHTML/ScriptProjetoManual"
    texto_path = os.path.join(base_dir, "Img", "Texto.md")
    
    # Create HTML output dir
    output_dir = os.path.join(base_dir, "html")
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        with open(texto_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
    except FileNotFoundError:
        print(f"Erro: Arquivo {texto_path} não encontrado.")
        return

    import base64
    def get_base64_image(image_path):
        try:
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                return f"data:image/png;base64,{encoded_string}"
        except Exception as e:
            print(f"Aviso: Não foi possível carregar a imagem {image_path}. Erro: {e}")
            return ""

    img1_path = get_base64_image(os.path.join(base_dir, "Img", "image.png"))
    img2_path = get_base64_image(os.path.join(base_dir, "Img", "image copy.png"))

    total_slides = 5

    # Slide 1: Cover
    title = lines[0]
    content1 = f"""
        <h1>{title}</h1>
        <div class="image-container">
            <img src="{img1_path}" alt="Cursos Cameta">
        </div>
    """
    render_slide(content1, 1, total_slides, os.path.join(output_dir, "slide_01.html"))

    # Slide 2: Introduction
    intro_txt = lines[1]
    content2 = f"""
        <h1 style="color: #009342;">Forma Muaná</h1>
        <p>{intro_txt}</p>
        <div class="callout">
            <p>Oportunidade de capacitação para o mercado de trabalho na região do Marajó!</p>
        </div>
    """
    render_slide(content2, 2, total_slides, os.path.join(output_dir, "slide_02.html"))

    # Slide 3: Cursos
    # linhas 2 fala sobre os cursos ofertados. Vamos criar um GRID.
    content3 = f"""
        <h1>Cursos Ofertados</h1>
        <p>Carga horária de <span class="highlight-text">60 horas</span> e turmas exclusivas.</p>
        
        <div class="grid-container">
            <div class="grid-item blue">
                <h3>Informática</h3>
                <span>30 vagas</span>
            </div>
            <div class="grid-item green">
                <h3>Libras</h3>
                <span>50 vagas</span>
            </div>
            <div class="grid-item">
                <h3>Tecnologias Digitais</h3>
                <span>30 vagas</span>
            </div>
            <div class="grid-item blue">
                <h3>Assistente Adm.</h3>
                <span>30 vagas</span>
            </div>
        </div>
        <p style="font-size: 28px; margin-top: 30px; text-align: center; color: #666;">
            Aumentando a <span class="highlight-text">empregabilidade</span> e empreendedorismo na região.
        </p>
    """
    render_slide(content3, 3, total_slides, os.path.join(output_dir, "slide_03.html"))

    # Slide 4: Quote
    quote_author_line = lines[3]
    # Limpando citação (extraindo texto até aspas e o restante)
    # A linha 3 eh: O professor Fabrício Farias... "Mesmo com 30 vagas..."
    quote = "Mesmo com 30 vagas ofertadas, recebemos 571 inscrições para as primeiras turmas de Informática, fato desafiador para selecionar os jovens e adultos que mais precisam da formação. Isso demonstra o interesse da população por formação."
    
    content4 = f"""
        <p>O coordenador do projeto ressalta a alta procura por qualificação na região:</p>
        <div class="quote-box">
            <div class="quote-icon">"</div>
            <div class="quote-text">{quote}</div>
            <div class="quote-author">Prof. Fabrício Farias</div>
        </div>
    """
    render_slide(content4, 4, total_slides, os.path.join(output_dir, "slide_04.html"))

    # Slide 5: Extensão / Conclusion
    extensao_txt = lines[4]
    
    content5 = f"""
        <h1>Iniciativa de Extensão</h1>
        <p>O projeto é executado pela <strong>FASI</strong> com apoio da <strong>SECTET</strong> e <strong>FADESP</strong>.</p>
        
        <div class="image-container" style="height: 350px;">
            <img src="{img2_path}" alt="Extensão UFPA">
        </div>
        
        <p style="font-size: 28px; margin-top: 30px; text-align: center; color: #004c8f; font-weight: 700;">
            Levar oportunidades para locais onde não há Escolas Tecnológicas.
        </p>
    """
    render_slide(content5, 5, total_slides, os.path.join(output_dir, "slide_05.html"))

    print(f"✅ Script finalizado! 5 Slides gerados na pasta '{output_dir}'.")

if __name__ == "__main__":
    main()
