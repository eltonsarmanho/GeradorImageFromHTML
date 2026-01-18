# Gerador de Imagens para Instagram - Jornada TCC

Este projeto automatiza a criação de imagens para Instagram a partir de dados CSV, convertendo informações de apresentações em layouts web e depois em imagens PNG otimizadas para redes sociais.

## 📋 O que os scripts fazem

### 1. `gerar_html.py` - Gerador de HTMLs
- Lê dados do arquivo CSV
- Agrupa apresentações por data
- Organiza cronologicamente
- Padroniza nomes dos alunos (primeira letra de cada palavra em maiúscula)
- Padroniza títulos dos trabalhos (primeira letra de cada palavra em maiúscula)
- Gera um arquivo HTML para cada data diferente

### 2. `gerar_posts.py` - Gerador de Imagens
- Lê arquivos HTML da pasta `html/`
- Renderiza cada arquivo em um navegador headless (Playwright)
- Carrega recursos locais (logo, imagens)
- Captura screenshots em alta qualidade
- Salva as imagens no formato adequado para Instagram (1080x1350px)

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

3. **Instale outras dependências (se necessário):**
   ```bash
   pip install -r requirements.txt
   ```

## 📁 Estrutura de Arquivos

Organize seu projeto da seguinte forma:

```
GeradorImageFromHTML/
├── gerar_html.py           # Script para gerar HTMLs a partir do CSV
├── gerar_posts.py          # Script para gerar imagens a partir dos HTMLs
├── requirements.txt        # Dependências do projeto
├── README.md              # Este arquivo
├── CSV/                   # Pasta com dados de entrada
│   └── Requisição de Defesa TCC (respostas).csv
├── html/                  # Pasta com arquivos HTML gerados
│   ├── Dia1.html
│   ├── Dia2.html
│   ├── Dia3.html
│   ├── Dia4.html
│   ├── Dia5.html
│   └── fasiOficial.png    # Logo (referenciada nos HTMLs)
└── instagram_posts/       # Pasta criada automaticamente
    ├── Dia1.png          # Imagens geradas
    ├── Dia2.png
    ├── Dia3.png
    ├── Dia4.png
    └── Dia5.png
```

## 🚀 Como Usar

### Passo 1: Preparar o arquivo CSV

Coloque um arquivo CSV na pasta `CSV/` com as seguintes colunas:

```
Nome, Matrícula, Email, Título do trabalho, Modalidade do Trabalho, 
Orientador, Membro 1 da Banca, Membro 2 da Banca, Membro 3 da Banca (Opcional), 
Data, Hora
```

**Exemplo de dados:**
```
Fernando Caldas Costa,201916040011,fernando@email.com,Projeto e Implementação de um Sistema...,Monografia,Fabricio de Souza Farias,Carlos dos Santos Portela,Leonardo Nunes Gonçalves,Keventon Rian Gimarães Gonçalves,09/02/26,09:00:00
```

### Passo 2: Gerar os arquivos HTML

Execute o script `gerar_html.py`:

```bash
python gerar_html.py
```

O script irá:
- Ler os dados do CSV
- Agrupar por data
- Criar um arquivo HTML para cada data
- Padronizar nomes e títulos

**Saída esperada:**
```
Encontradas 5 datas diferentes:
  - Dia 1: 09/02/26 (4 apresentações)
  - Dia 2: 10/02/26 (3 apresentações)
  ...
✅ Gerado: Dia1.html (4 apresentações)
✅ Gerado: Dia2.html (3 apresentações)
```

### Passo 3: Gerar as imagens PNG

Execute o script `gerar_posts.py`:

```bash
python gerar_posts.py
```

O script irá:
- Ler todos os arquivos HTML gerados
- Renderizar cada um como imagem
- Salvar as imagens na pasta `instagram_posts/`

**Saída esperada:**
```
Encontrados 5 arquivos HTML:
Processando: html/Dia1.html
Imagem gerada com sucesso: instagram_posts/Dia1.png
Processando: html/Dia2.html
Imagem gerada com sucesso: instagram_posts/Dia2.png
...
--- Processo Concluído! Verifique a pasta 'instagram_posts' ---
```

### Passo 4 (Opcional): Executar ambos os scripts

Para automatizar todo o processo:

```bash
python gerar_html.py && python gerar_posts.py
```

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