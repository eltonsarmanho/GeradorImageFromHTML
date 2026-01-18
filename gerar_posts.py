from playwright.sync_api import sync_playwright
import os
import glob

def gerar_imagem_instagram(html_file_path, output_filename, width=1080, height=1350):
    """
    Renderiza arquivo HTML em uma imagem usando Playwright.
    """
    with sync_playwright() as p:
        # Inicia um navegador Chromium (headless por padrão)
        browser = p.chromium.launch()
        
        # Cria uma nova página
        page = browser.new_page()
        
        # Define o tamanho da viewport (essencial para o formato Instagram)
        # device_scale_factor=2 garante alta resolução (retina display) para textos nítidos
        page.set_viewport_size({"width": width, "height": height})
        
        # Carrega o arquivo HTML diretamente (permite carregar recursos locais como imagens)
        # Converte o caminho para file:// URL para funcionar com Playwright
        file_url = f"file://{os.path.abspath(html_file_path)}"
        page.goto(file_url, wait_until="networkidle")
        
        # Tira o screenshot e salva
        page.screenshot(path=output_filename, type='png', scale="css")
        
        print(f"Imagem gerada com sucesso: {output_filename}")
        
        browser.close()

# --- Geração de Imagens a partir dos arquivos HTML ---

# Cria a pasta de saída se não existir
output_dir = "instagram_posts"
os.makedirs(output_dir, exist_ok=True)

# Define o caminho da pasta HTML
html_dir = "html"

# Busca todos os arquivos HTML na pasta
html_files = glob.glob(os.path.join(html_dir, "*.html"))
html_files.sort()  # Ordena os arquivos

print(f"Encontrados {len(html_files)} arquivos HTML:")

# Loop para processar cada arquivo HTML
for html_file in html_files:
    # Extrai o nome base do arquivo (sem extensão)
    nome_base = os.path.splitext(os.path.basename(html_file))[0]
    
    print(f"Processando: {html_file}")
    
    # Define o nome do arquivo de saída
    nome_arquivo = os.path.join(output_dir, f"{nome_base}.png")
    
    # Gera a imagem diretamente do arquivo HTML (permite carregar imagens locais)
    try:
        gerar_imagem_instagram(html_file, nome_arquivo, width=1080, height=1350)
        
    except Exception as e:
        print(f"Erro ao processar {html_file}: {e}")

print("\n--- Processo Concluído! Verifique a pasta 'instagram_posts' ---")