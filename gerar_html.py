#!/usr/bin/env python3
"""
Script para gerar arquivos HTML de cronograma de TCC a partir de dados CSV.
Gera um arquivo HTML para cada data diferente, organizando os dados cronologicamente.
"""

import csv
import os
from datetime import datetime
from collections import defaultdict

def ler_csv(arquivo_csv):
    """Lê o arquivo CSV e retorna uma lista de dicionários com os dados."""
    dados = []
    
    with open(arquivo_csv, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Limpa espaços extras dos valores
            row = {k: v.strip() if v else '' for k, v in row.items()}
            dados.append(row)
    
    return dados

def agrupar_por_data(dados):
    """Agrupa os dados por data e organiza cronologicamente."""
    dados_agrupados = defaultdict(list)
    
    for item in dados:
        data = item['Data']
        dados_agrupados[data].append(item)
    
    # Ordena cada grupo por horário
    for data in dados_agrupados:
        dados_agrupados[data].sort(key=lambda x: datetime.strptime(x['Hora'], '%H:%M:%S').time())
    
    return dict(dados_agrupados)

def formatar_data_exibicao(data_str):
    """Converte data de DD/MM/AA para formato de exibição."""
    try:
        # Parse da data no formato DD/MM/AA
        data_obj = datetime.strptime(data_str, '%d/%m/%y')
        # Mapear dias da semana
        dias_semana = {
            0: 'Segunda-feira',
            1: 'Terça-feira', 
            2: 'Quarta-feira',
            3: 'Quinta-feira',
            4: 'Sexta-feira',
            5: 'Sábado',
            6: 'Domingo'
        }
        dia_semana = dias_semana[data_obj.weekday()]
        return f"{data_obj.strftime('%d de %B')} ({dia_semana})", data_obj
    except ValueError:
        return data_str, None

def formatar_banca(orientador, membro1, membro2, membro3=""):
    """Formata a string da banca examinadora."""
    membros = [orientador, membro1, membro2]
    if membro3:
        membros.append(membro3)
    
    # Remove prefixos comuns dos nomes
    membros_limpos = []
    for membro in membros:
        if membro:
            # Remove prefixos como "Prof. Me.", "Esp.", etc.
            nome_limpo = membro.replace("Prof. Me. ", "Prof. ").replace("Esp. ", "Prof. ").replace("Me. ", "Prof. ")
            if not nome_limpo.startswith("Prof."):
                nome_limpo = "Prof. " + nome_limpo
            membros_limpos.append(nome_limpo)
    
    return ", ".join(membros_limpos)

def gerar_html_template(data_exibicao, dia_numero, itens_cronograma):
    """Gera o template HTML com os dados fornecidos."""
    
    # Mapear meses para português
    meses_pt = {
        'January': 'Janeiro', 'February': 'Fevereiro', 'March': 'Março',
        'April': 'Abril', 'May': 'Maio', 'June': 'Junho',
        'July': 'Julho', 'August': 'Agosto', 'September': 'Setembro',
        'October': 'Outubro', 'November': 'Novembro', 'December': 'Dezembro'
    }
    
    for ing, pt in meses_pt.items():
        data_exibicao = data_exibicao.replace(ing, pt)
    
    # Gerar itens do cronograma
    cronograma_html = ""
    for item in itens_cronograma:
        hora = datetime.strptime(item['Hora'], '%H:%M:%S').strftime('%H:%M')
        nome = item['Nome']
        titulo = item['Título do trabalho'].title()  # Aplica title case (primeira letra maiúscula)
        banca = formatar_banca(
            item['Orientador'],
            item['Membro 1 da Banca'],
            item['Membro 2 da Banca'],
            item['Membro 3 da Banca (Opcional)']
        )
        
        cronograma_html += f"""            <div class="schedule-item">
                <div class="time">{hora}</div>
                <div class="info">
                    <div class="student-name">{nome}</div>
                    <div class="theme">Tema: {titulo}</div>
                    <div class="banca"><strong>Banca:</strong> {banca}</div>
                </div>
            </div>

"""
    
    template = f"""<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Flyer Jornada TCC</title>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;800&family=Roboto:ital,wght@0,300;0,400;0,500;1,400&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary-blue: #0000FF; /* Azul FASI */
            --dark-blue: #000099;
            --text-dark: #333;
            --text-light: #666;
            --bg-color: #f4f7fa;
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
            background-color: #222;
            min-height: 100vh;
            font-family: 'Roboto', sans-serif;
        }}

        /* Container do Flyer (Proporção Instagram Portrait 4:5 ou similar) */
        .flyer {{
            width: 1080px;
            height: 1350px;
            background-color: #fff;
            position: relative;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            box-shadow: 0 0 50px rgba(0,0,0,0.5);
        }}

        /* Background Tech Sutil */
        .flyer::before {{
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-image: 
                radial-gradient(circle at 10% 20%, rgba(0, 0, 255, 0.03) 0%, transparent 20%),
                radial-gradient(circle at 90% 80%, rgba(0, 0, 255, 0.03) 0%, transparent 20%);
            background-size: 100% 100%;
            z-index: 0;
        }}

        /* Elementos Gráficos Decorativos */
        .circle-decor {{
            position: absolute;
            border-radius: 50%;
            z-index: 0;
        }}
        .c1 {{ width: 300px; height: 300px; background: rgba(0,0,255,0.05); top: -100px; right: -50px; }}
        .c2 {{ width: 150px; height: 150px; border: 20px solid rgba(0,0,255,0.05); bottom: 50px; left: -50px; }}

        /* Cabeçalho */
        header {{
            padding: 60px 80px 20px 80px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            z-index: 2;
        }}

        .logo-placeholder {{
            height: 100px;
            display: flex;
            align-items: center;
            margin: 0 auto;
          
        }}
        
        .logo-placeholder img {{
            max-height: 300%;
            max-width: 300px;
            object-fit: contain;
            margin: 0 auto;
            
        }}

        /* Títulos */
        .title-section {{
            text-align: center;
            padding: 20px 0;
            z-index: 2;
        }}

        h1 {{
            font-family: 'Montserrat', sans-serif;
            font-weight: 800;
            font-size: 56px;
            color: var(--primary-blue);
            letter-spacing: -1px;
            margin-bottom: 10px;
            text-transform: uppercase;
        }}

        h2 {{
            font-family: 'Montserrat', sans-serif;
            font-weight: 600;
            font-size: 28px;
            color: var(--text-dark);
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        /* Data em destaque */
        .date-banner {{
            background: linear-gradient(90deg, var(--dark-blue) 0%, var(--primary-blue) 100%);
            color: white;
            text-align: center;
            padding: 20px;
            margin: 30px 80px;
            border-radius: 12px;
            font-family: 'Montserrat', sans-serif;
            font-size: 32px;
            font-weight: 700;
            box-shadow: 0 10px 20px rgba(0, 0, 255, 0.2);
            z-index: 2;
            position: relative;
        }}

        /* Cronograma */
        .schedule {{
            flex: 1;
            padding: 20px 100px;
            display: flex;
            flex-direction: column;
            gap: 35px;
            z-index: 2;
        }}

        .schedule-item {{
            display: flex;
            gap: 30px;
            border-left: 4px solid var(--primary-blue);
            padding-left: 30px;
            position: relative;
        }}

        .schedule-item::before {{
            content: "";
            position: absolute;
            left: -12px;
            top: 0;
            width: 20px;
            height: 20px;
            background-color: #fff;
            border: 4px solid var(--primary-blue);
            border-radius: 50%;
        }}

        .time {{
            font-family: 'Montserrat', sans-serif;
            font-weight: 800;
            font-size: 32px;
            color: var(--primary-blue);
            min-width: 110px;
        }}

        .info {{
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}

        .student-name {{
            font-size: 28px;
            font-weight: 700;
            color: #222;
        }}

        .theme {{
            font-style: italic;
            font-size: 20px;
            color: #444;
            font-weight: 500;
            background-color: rgba(0,0,255,0.05);
            padding: 8px 12px;
            border-radius: 6px;
            display: inline-block;
        }}

        .banca {{
            font-size: 16px;
            color: #666;
            margin-top: 5px;
            line-height: 1.4;
        }}

        .banca strong {{
            color: var(--primary-blue);
            font-weight: 600;
        }}

        /* Rodapé decorativo */
        footer {{
            height: 20px;
            background: var(--primary-blue);
            margin-top: auto;
        }}

    </style>
</head>
<body>

    <div class="flyer">
        <div class="circle-decor c1"></div>
        <div class="circle-decor c2"></div>

        <header>
            <div class="logo-placeholder" >
                <img src="fasiOficial.png" alt="Logo FASI">
            </div>
        </header>

        <div class="title-section">
            <h1>JORNADA DO TCC 2026</h1>
            <h2>Bacharelado em Sistemas de Informação</h2>
        </div>

        <div class="date-banner">
            📅 DIA {dia_numero}: {data_exibicao}
        </div>

        <div class="schedule">
{cronograma_html}        </div>

        <footer></footer>
    </div>

</body>
</html>"""
    
    return template

def main():
    """Função principal que coordena a geração dos HTMLs."""
    arquivo_csv = 'CSV/Requisição de Defesa TCC (respostas).csv'
    pasta_html = 'html'
    
    # Cria a pasta html se não existir
    if not os.path.exists(pasta_html):
        os.makedirs(pasta_html)
    
    print("Lendo dados do CSV...")
    dados = ler_csv(arquivo_csv)
    
    print("Agrupando dados por data...")
    dados_por_data = agrupar_por_data(dados)
    
    # Ordena as datas cronologicamente
    datas_ordenadas = sorted(dados_por_data.keys(), 
                           key=lambda x: datetime.strptime(x, '%d/%m/%y'))
    
    print(f"Encontradas {len(datas_ordenadas)} datas diferentes:")
    for i, data in enumerate(datas_ordenadas, 1):
        print(f"  - Dia {i}: {data} ({len(dados_por_data[data])} apresentações)")
    
    print("\nGerando arquivos HTML...")
    
    for i, data in enumerate(datas_ordenadas, 1):
        data_exibicao, _ = formatar_data_exibicao(data)
        itens = dados_por_data[data]
        
        html_content = gerar_html_template(data_exibicao, i, itens)
        
        nome_arquivo = f"Dia{i}.html"
        caminho_arquivo = os.path.join(pasta_html, nome_arquivo)
        
        with open(caminho_arquivo, 'w', encoding='utf-8') as file:
            file.write(html_content)
        
        print(f"✅ Gerado: {nome_arquivo} ({len(itens)} apresentações)")
    
    print(f"\n✨ Processo concluído! {len(datas_ordenadas)} arquivos HTML foram gerados na pasta '{pasta_html}'.")

if __name__ == "__main__":
    main()
