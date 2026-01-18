# Gerador de Imagens para Instagram - Jornada TCC

Este script automatiza a criação de imagens para Instagram a partir de arquivos HTML, convertendo layouts web em imagens PNG otimizadas para redes sociais.

## 📋 O que o script faz

O script `gerar_posts.py` utiliza o Playwright para:
- Ler arquivos HTML da pasta `html/`
- Renderizar cada arquivo em um navegador headless
- Capturar screenshots em alta qualidade
- Salvar as imagens no formato adequado para Instagram (1080x1350px)

## 🔧 Pré-requisitos

- Python 3.7 ou superior
- pip (gerenciador de pacotes do Python)

## 📦 Instalação das Dependências

1. **Instale o Playwright:**
   ```bash
   pip install playwright
   ```

2. **Instale o navegador Chromium:**
   ```bash
   python -m playwright install chromium
   ```

## 📁 Estrutura de Arquivos

Organize seu projeto da seguinte forma:

```
GeradorImagemJornadaTCC/
├── gerar_posts.py          # Script principal
├── requirements.txt        # Dependências do projeto
├── README.md              # Este arquivo
├── html/                  # Pasta com arquivos HTML
│   ├── Dia1.html
│   ├── Dia2.html
│   ├── Dia3.html
│   ├── Dia4.html
│   └── Dia5.html
└── instagram_posts/       # Pasta criada automaticamente
    ├── Dia1.png          # Imagens geradas
    ├── Dia2.png
    ├── Dia3.png
    ├── Dia4.png
    └── Dia5.png
```

## 🚀 Como Usar

1. **Coloque seus arquivos HTML na pasta `html/`**
   - Os arquivos devem ter a extensão `.html`
   - Podem ter qualquer nome (ex: Dia1.html, evento.html, etc.)

2. **Execute o script:**
   ```bash
   python gerar_posts.py
   ```

3. **Verifique o resultado:**
   - As imagens serão salvas na pasta `instagram_posts/`
   - Cada arquivo HTML gerará uma imagem PNG correspondente

## ⚙️ Configurações

### Dimensões das Imagens
Por padrão, as imagens são geradas com:
- **Largura:** 1080px
- **Altura:** 1350px (formato vertical do Instagram)

Para alterar as dimensões, modifique a função `gerar_imagem_instagram()`:

```python
def gerar_imagem_instagram(html_content, output_filename, width=1080, height=1350):
    # Altere os valores de width e height conforme necessário
```

### Formato de Saída
- **Formato:** PNG
- **Qualidade:** Alta resolução (CSS scale)
- **Compatível:** Instagram, Facebook, outras redes sociais

## 🎨 Dicas para os Arquivos HTML

1. **Use CSS embutido:** Evite arquivos CSS externos para garantir que tudo seja renderizado corretamente

2. **Fontes Google:** Use `@import` ou `<link>` para Google Fonts:
   ```html
   <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap" rel="stylesheet">
   ```

3. **Dimensões fixas:** Configure seu HTML para 1080x1350px:
   ```css
   .flyer {
       width: 1080px;
       height: 1350px;
   }
   ```

## 🔍 Solução de Problemas

### Erro: "No module named playwright"
```bash
pip install playwright
python -m playwright install chromium
```

### Erro: "File not found"
- Verifique se a pasta `html/` existe
- Verifique se há arquivos `.html` na pasta

### Erro de renderização
- Verifique se o HTML está bem formado
- Teste o HTML no navegador antes de gerar a imagem
- Certifique-se de que recursos externos (fontes, imagens) estão acessíveis

### Imagens muito pequenas ou grandes
- Ajuste as dimensões na função `gerar_imagem_instagram()`
- Verifique o CSS dos seus arquivos HTML

## 📝 Exemplo de Saída

```
Encontrados 5 arquivos HTML:
Processando: html/Dia1.html
Imagem gerada com sucesso: instagram_posts/Dia1.png
Processando: html/Dia2.html
Imagem gerada com sucesso: instagram_posts/Dia2.png
...

--- Processo Concluído! Verifique a pasta 'instagram_posts' ---
```

## 🤝 Contribuições

Para contribuir com melhorias:
1. Faça um fork do projeto
2. Crie uma branch para sua feature
3. Faça commit das suas alterações
4. Envie um pull request

## 📄 Licença

Este projeto é de uso livre para fins educacionais e comerciais.

---

**Desenvolvido para automatizar a criação de conteúdo visual para redes sociais** 🎯