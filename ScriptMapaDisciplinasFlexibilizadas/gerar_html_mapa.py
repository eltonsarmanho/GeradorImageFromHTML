#!/usr/bin/env python3
"""
Script para gerar arquivo HTML com mapa de disciplinas flexibilizadas.
Cria uma visualização organizada das disciplinas por curso com suas respectivas cargas horárias.
"""

import os
from collections import defaultdict

def obter_disciplinas_flexibilizadas():
    """Retorna o dicionário com as disciplinas flexibilizadas organizadas por curso."""
    disciplinas = {
        "Matemática": [
            {"nome": "Fundamentos da Lógica Matemática", "carga_horaria": "60h"},
            {"nome": "Estatística Aplicada à Educação", "carga_horaria": "60h"}
        ],
        "Geografia": [
            {"nome": "Geoprocessamento", "carga_horaria": "60h"}
        ],
        "Pedagogia": [
            {"nome": "Tecnologia Educacional", "carga_horaria": "60h"}
        ],
        "Letras": [
            {"nome": "Língua Estrangeira Instrumental", "carga_horaria": "60h"},
            {"nome": "Letramentos Acadêmicos e a Escrita", "carga_horaria": "60h"}
        ]
    }
    return disciplinas

def gerar_cards_disciplinas(disciplinas_por_curso):
    """Gera o HTML dos cards das disciplinas organizadas por curso."""
    cards_html = ""
    cores_cursos = {
        "Matemática": "#FF6B6B",
        "Geografia": "#4ECDC4", 
        "Pedagogia": "#45B7D1",
        "Letras": "#96CEB4"
    }
    
    for curso, disciplinas in disciplinas_por_curso.items():
        cor = cores_cursos.get(curso, "#6C5CE7")
        
        cards_html += f"""        <div class="course-section">
            <div class="course-header" style="background: linear-gradient(135deg, {cor} 0%, {cor}dd 100%);">
                <h3>{curso}</h3>
                <div class="course-badge">{len(disciplinas)} disciplina{'s' if len(disciplinas) > 1 else ''}</div>
            </div>
            <div class="subjects-grid">
"""
        
        for disciplina in disciplinas:
            cards_html += f"""                <div class="subject-card">
                    <div class="subject-name">{disciplina['nome']}</div>
                    <div class="subject-load">
                        <span class="load-icon">⏱️</span>
                        {disciplina['carga_horaria']}
                    </div>
                </div>
"""
        
        cards_html += """            </div>
        </div>

"""
    
    return cards_html

def calcular_estatisticas(disciplinas_por_curso):
    """Calcula estatísticas gerais das disciplinas."""
    total_disciplinas = sum(len(disciplinas) for disciplinas in disciplinas_por_curso.values())
    total_cursos = len(disciplinas_por_curso)
    
    # Assume que todas têm 60h para cálculo da carga total
    carga_total = total_disciplinas * 60
    
    return {
        "total_disciplinas": total_disciplinas,
        "total_cursos": total_cursos,
        "carga_total": carga_total
    }

def gerar_html_mapa(disciplinas_por_curso, estatisticas):
    """Gera o template HTML completo com o mapa de disciplinas."""
    
    cards_disciplinas = gerar_cards_disciplinas(disciplinas_por_curso)
    
    template = f"""<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mapa de Disciplinas Flexibilizadas</title>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;800&family=Roboto:ital,wght@0,300;0,400;0,500;1,400&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary-blue: #0000FF;
            --dark-blue: #000099;
            --text-dark: #333;
            --text-light: #666;
            --bg-color: #f8f9fa;
            --card-shadow: 0 8px 25px rgba(0,0,0,0.1);
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            display: flex;
            justify-content: center;
            align-items: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            font-family: 'Roboto', sans-serif;
            padding: 20px;
        }}

        .container {{
            width: 1200px;
            max-width: 95vw;
            background-color: #fff;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 20px 60px rgba(0,0,0,0.2);
        }}

        /* Cabeçalho */
        header {{
            background: linear-gradient(135deg, var(--dark-blue) 0%, var(--primary-blue) 100%);
            color: white;
            padding: 40px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }}

        header::before {{
            content: "";
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background-image: radial-gradient(circle, rgba(255,255,255,0.1) 1px, transparent 1px);
            background-size: 30px 30px;
            animation: float 20s infinite linear;
        }}

        @keyframes float {{
            0% {{ transform: translate(-50%, -50%) rotate(0deg); }}
            100% {{ transform: translate(-50%, -50%) rotate(360deg); }}
        }}

        h1 {{
            font-family: 'Montserrat', sans-serif;
            font-weight: 800;
            font-size: 48px;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            z-index: 2;
            position: relative;
        }}

        .subtitle {{
            font-family: 'Montserrat', sans-serif;
            font-size: 20px;
            font-weight: 400;
            opacity: 0.9;
            z-index: 2;
            position: relative;
        }}

        /* Estatísticas */
        .stats-banner {{
            background: var(--bg-color);
            padding: 30px 40px;
            display: flex;
            justify-content: space-around;
            text-align: center;
            border-bottom: 1px solid #e0e6ed;
        }}

        .stat-item {{
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}

        .stat-number {{
            font-family: 'Montserrat', sans-serif;
            font-weight: 800;
            font-size: 36px;
            color: var(--primary-blue);
        }}

        .stat-label {{
            font-size: 14px;
            color: var(--text-light);
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 600;
        }}

        /* Conteúdo principal */
        .main-content {{
            padding: 40px;
        }}

        .intro-text {{
            text-align: center;
            margin-bottom: 40px;
            font-size: 18px;
            color: var(--text-dark);
            line-height: 1.6;
        }}

        /* Seções dos cursos */
        .courses-container {{
            display: grid;
            gap: 30px;
        }}

        .course-section {{
            background: #fff;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: var(--card-shadow);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}

        .course-section:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 35px rgba(0,0,0,0.15);
        }}

        .course-header {{
            padding: 25px;
            color: white;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: relative;
        }}

        .course-header h3 {{
            font-family: 'Montserrat', sans-serif;
            font-weight: 700;
            font-size: 24px;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
        }}

        .course-badge {{
            background: rgba(255,255,255,0.2);
            padding: 8px 15px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            backdrop-filter: blur(10px);
        }}

        .subjects-grid {{
            padding: 30px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }}

        .subject-card {{
            background: var(--bg-color);
            border-radius: 12px;
            padding: 25px;
            border-left: 4px solid var(--primary-blue);
            transition: all 0.3s ease;
        }}

        .subject-card:hover {{
            background: #f0f3ff;
            transform: translateX(5px);
        }}

        .subject-name {{
            font-weight: 600;
            font-size: 18px;
            color: var(--text-dark);
            margin-bottom: 15px;
            line-height: 1.4;
        }}

        .subject-load {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 16px;
            color: var(--primary-blue);
            font-weight: 600;
        }}

        .load-icon {{
            font-size: 18px;
        }}

        /* Rodapé */
        footer {{
            background: var(--bg-color);
            padding: 30px 40px;
            text-align: center;
            color: var(--text-light);
            border-top: 1px solid #e0e6ed;
        }}

        .footer-text {{
            font-size: 14px;
            line-height: 1.6;
        }}

        .highlight {{
            color: var(--primary-blue);
            font-weight: 600;
        }}

        /* Responsividade */
        @media (max-width: 768px) {{
            .stats-banner {{
                flex-direction: column;
                gap: 20px;
            }}
            
            .subjects-grid {{
                grid-template-columns: 1fr;
            }}
            
            h1 {{
                font-size: 36px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📚 MAPA DE DISCIPLINAS FLEXIBILIZADAS</h1>
            <p class="subtitle">Bacharelado em Sistemas de Informação - FASI</p>
        </header>

        <div class="stats-banner">
            <div class="stat-item">
                <div class="stat-number">{estatisticas['total_disciplinas']}</div>
                <div class="stat-label">Disciplinas</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{estatisticas['total_cursos']}</div>
                <div class="stat-label">Cursos</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{estatisticas['carga_total']}h</div>
                <div class="stat-label">Carga Horária Total</div>
            </div>
        </div>

        <div class="main-content">
            <div class="intro-text">
                Explore as <span class="highlight">disciplinas flexibilizadas</span> disponíveis para complementar sua formação acadêmica.<br>
                Cada disciplina oferece <strong>60 horas</strong> de conteúdo especializado em diferentes áreas do conhecimento.
            </div>

            <div class="courses-container">
{cards_disciplinas}            </div>
        </div>

        <footer>
            <div class="footer-text">
                <strong>📋 Como funciona:</strong> Escolha as disciplinas que mais se alinham com seus objetivos acadêmicos e profissionais.<br>
                Para mais informações sobre <span class="highlight">inscrições e cronogramas</span>, entre em contato com a coordenação do curso.
            </div>
        </footer>
    </div>
</body>
</html>"""
    
    return template

def main():
    """Função principal que coordena a geração do HTML do mapa de disciplinas."""
    pasta_html = 'html'
    
    # Cria a pasta html se não existir
    if not os.path.exists(pasta_html):
        os.makedirs(pasta_html)
    
    print("Obtendo disciplinas flexibilizadas...")
    disciplinas_por_curso = obter_disciplinas_flexibilizadas()
    
    print("Calculando estatísticas...")
    estatisticas = calcular_estatisticas(disciplinas_por_curso)
    
    print(f"Encontradas {estatisticas['total_disciplinas']} disciplinas em {estatisticas['total_cursos']} cursos:")
    for curso, disciplinas in disciplinas_por_curso.items():
        print(f"  - {curso}: {len(disciplinas)} disciplina{'s' if len(disciplinas) > 1 else ''}")
        for disciplina in disciplinas:
            print(f"    • {disciplina['nome']} ({disciplina['carga_horaria']})")
    
    print("\nGerando arquivo HTML do mapa...")
    
    html_content = gerar_html_mapa(disciplinas_por_curso, estatisticas)
    
    nome_arquivo = "mapa_disciplinas_flexibilizadas.html"
    caminho_arquivo = os.path.join(pasta_html, nome_arquivo)
    
    with open(caminho_arquivo, 'w', encoding='utf-8') as file:
        file.write(html_content)
    
    print(f"✅ Gerado: {nome_arquivo}")
    print(f"📍 Localização: {caminho_arquivo}")
    print(f"📊 Total: {estatisticas['total_disciplinas']} disciplinas, {estatisticas['carga_total']}h de carga horária")
    print(f"\n✨ Processo concluído! O mapa de disciplinas foi gerado na pasta '{pasta_html}'.")

if __name__ == "__main__":
    main()
