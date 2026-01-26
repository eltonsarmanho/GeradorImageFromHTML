from playwright.sync_api import sync_playwright
import os
import glob
import argparse

def obter_configuracoes_plataforma(plataforma, tipo_conteudo="auto"):
    """
    Retorna configurações específicas para cada plataforma de rede social.
    """
    configuracoes = {
        "instagram": {
            "square": {"width": 1080, "height": 1080, "full_page": False},
            "portrait": {"width": 1080, "height": 1350, "full_page": False},
            "mapa": {"width": 1080, "height": 1350, "full_page": True}
        },
        "whatsapp": {
            "square": {"width": 1080, "height": 1080, "full_page": False},
            "portrait": {"width": 1080, "height": 1080, "full_page": False},
            "mapa": {"width": 1080, "height": 1350, "full_page": True}
        },
        "original": {
            "carrossel": {"width": 1080, "height": 1350, "full_page": False},
            "portrait": {"width": 1080, "height": 1350, "full_page": False},
            "square": {"width": 1080, "height": 1080, "full_page": False},
            "mapa": {"width": 1200, "height": 1600, "full_page": True}
        }
    }
    
    if plataforma in configuracoes:
        if tipo_conteudo in configuracoes[plataforma]:
            config = configuracoes[plataforma][tipo_conteudo].copy()
            config["plataforma"] = plataforma
            config["formato"] = tipo_conteudo
            return config
        else:
            # Fallback seguro: tenta portrait, depois square, senão pega o primeiro preset disponível
            presets = configuracoes[plataforma]
            if "portrait" in presets:
                fallback_key = "portrait"
            elif "square" in presets:
                fallback_key = "square"
            else:
                fallback_key = next(iter(presets.keys()))

            config = presets[fallback_key].copy()
            config["plataforma"] = plataforma
            config["formato"] = fallback_key
            return config
    
    # Default original
    return {"width": 1080, "height": 1350, "full_page": False, "plataforma": "original", "formato": "carrossel"}

def detectar_tipo_arquivo(html_file_path, plataforma="original"):
    """
    Detecta o tipo de arquivo HTML e retorna configurações baseadas na plataforma.
    """
    try:
        with open(html_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
        # Verifica se é um arquivo do mapa de disciplinas
        if "MAPA DE DISCIPLINAS" in content or "mapa_disciplinas" in os.path.basename(html_file_path):
            config = obter_configuracoes_plataforma(plataforma, "mapa")
            config["tipo"] = "mapa"
        # Caso contrário, assume que é do carrossel TCC
        else:
            if plataforma == "whatsapp":
                config = obter_configuracoes_plataforma(plataforma, "square")
            else:
                config = obter_configuracoes_plataforma(plataforma, "portrait")
            config["tipo"] = "carrossel"
            
        return config
        
    except Exception as e:
        print(f"Erro ao detectar tipo do arquivo {html_file_path}: {e}")
        # Default para carrossel
        config = obter_configuracoes_plataforma(plataforma, "portrait")
        config["tipo"] = "carrossel"
        return config

def gerar_imagem_post(html_file_path, output_filename, config=None, plataforma="original"):
    """
    Renderiza arquivo HTML em uma imagem usando Playwright.
    Detecta automaticamente o tipo de arquivo e aplica configurações apropriadas para cada plataforma.
    """
    if config is None:
        config = detectar_tipo_arquivo(html_file_path, plataforma)
    
    with sync_playwright() as p:
        # Inicia um navegador Chromium (headless por padrão)
        browser = p.chromium.launch()
        
        # Cria uma nova página
        page = browser.new_page()
        
        # Define o tamanho da viewport
        page.set_viewport_size({"width": config["width"], "height": config["height"]})
        
        # Carrega o arquivo HTML diretamente
        file_url = f"file://{os.path.abspath(html_file_path)}"
        page.goto(file_url, wait_until="networkidle")
        
        # Aguarda um pouco para garantir que tudo carregou
        page.wait_for_timeout(1500)
        
        # Configurações de screenshot baseadas no tipo e plataforma
        screenshot_options = {
            "path": output_filename,
            "type": "png",
            "scale": "css"
        }
        
        if config["full_page"]:
            # Para mapas, captura a página inteira
            screenshot_options["full_page"] = True
        else:
            # Para outros tipos, usa dimensões fixas
            screenshot_options["clip"] = {
                "x": 0,
                "y": 0,
                "width": config["width"],
                "height": config["height"]
            }
        
        # Tira o screenshot e salva
        page.screenshot(**screenshot_options)
        
        plataforma_info = f"{config['plataforma']} ({config['width']}x{config['height']})"
        print(f"✅ {output_filename} - {config['tipo']} para {plataforma_info}")
        
        browser.close()

def main():
    """Função principal com argumentos de linha de comando."""
    parser = argparse.ArgumentParser(description="Gerador de Posts para Redes Sociais")
    parser.add_argument(
        "--plataforma", 
        choices=["instagram", "whatsapp", "original", "todas"], 
        default="original",
        help="Plataforma de destino: instagram, whatsapp, original ou todas"
    )
    parser.add_argument(
        "--arquivo", 
        type=str, 
        help="Arquivo HTML específico para processar (opcional)"
    )
    
    args = parser.parse_args()
    
    # Cria as pastas de saída se não existirem
    if args.plataforma == "todas":
        output_dirs = ["instagram_posts", "whatsapp_posts", "original_posts"]
        plataformas = ["instagram", "whatsapp", "original"]
    else:
        output_dir = f"{args.plataforma}_posts"
        output_dirs = [output_dir]
        plataformas = [args.plataforma]
    
    for output_dir in output_dirs:
        os.makedirs(output_dir, exist_ok=True)
    
    # Define arquivos a processar
    html_dir = "html"
    if args.arquivo:
        if os.path.exists(args.arquivo):
            html_files = [args.arquivo]
        else:
            print(f"❌ Arquivo não encontrado: {args.arquivo}")
            return
    else:
        html_files = glob.glob(os.path.join(html_dir, "*.html"))
        html_files.sort()
    
    if not html_files:
        print("❌ Nenhum arquivo HTML encontrado!")
        return
    
    print(f"📱 Gerando posts para: {', '.join(plataformas)}")
    print(f"📄 Arquivos encontrados: {len(html_files)}")
    
    # Processa cada arquivo para cada plataforma
    for plataforma in plataformas:
        output_dir = f"{plataforma}_posts"
        print(f"\n🎯 Processando para {plataforma.upper()}:")
        print("-" * 50)
        
        for html_file in html_files:
            nome_base = os.path.splitext(os.path.basename(html_file))[0]
            
            # Detecta configurações para a plataforma
            config = detectar_tipo_arquivo(html_file, plataforma)
            
            # Define nome do arquivo de saída
            nome_arquivo = os.path.join(output_dir, f"{nome_base}.png")
            
            try:
                gerar_imagem_post(html_file, nome_arquivo, config, plataforma)
                
            except Exception as e:
                print(f"❌ Erro ao processar {html_file}: {e}")
    
    print(f"\n✨ Processo Concluído!")
    print("📂 Verifique as pastas:")
    for output_dir in output_dirs:
        if os.path.exists(output_dir):
            arquivos = len([f for f in os.listdir(output_dir) if f.endswith('.png')])
            print(f"   • {output_dir}/ ({arquivos} imagens)")

if __name__ == "__main__":
    main()