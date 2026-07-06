# Gerador de Imagens para Redes Sociais

Este projeto automatiza a criação de imagens para Instagram/WhatsApp a partir de dados (CSV ou conteúdo fixo), convertendo informações em layouts web (HTML) e depois em imagens PNG otimizadas para redes sociais.

O repositório contém **vários geradores de HTML independentes** (um por campanha/projeto) e **um único gerador de posts genérico** (`gerar_posts.py`) que renderiza qualquer HTML em PNG.

## 📋 Scripts disponíveis

| Pasta | Script | Gera | Saída (HTML) |
|---|---|---|---|
| `ScriptCarroselTCC/` | `gerar_html.py` | Carrossel da Jornada do TCC a partir de `CSV/data.csv` (agrupado por data, mescla duplas) | `ScriptCarroselTCC/html/DiaN.html` |
| `ScriptCalendarioRAJJ/` | `gerar_html_rajj.py` | Calendário semanal de treinos (grade) | `ScriptCalendarioRAJJ/html/calendario_treinos_rajj.html` |
| `ScriptMapaDisciplinasFlexibilizadas/` | `gerar_html_mapa.py` | Mapa de disciplinas flexibilizadas por curso | `ScriptMapaDisciplinasFlexibilizadas/html/mapa_disciplinas_flexibilizadas.html` |
| `ScriptProjetoManual/` | `gerar_htmls.py` | Slides de carrossel a partir de `Img/Texto.md` + imagens | `ScriptProjetoManual/html/slide_0N.html` |
| `ScriptSebrae/` | `gerar_html_premiacao_sebrae_2026.py` | Carrossel do Prêmio Educador Transformador (Sebrae) 2026 | `ScriptSebrae/html/*.html` |
| raiz `/` | `gerar_posts.py` | Renderiza qualquer HTML em PNG (Playwright), com variações por plataforma | `instagram_posts/`, `whatsapp_posts/`, `original_posts/` |

Cada gerador de HTML é independente e cria sua própria pasta `html/` **dentro da sua própria pasta**. O `gerar_posts.py` procura arquivos na pasta `html/` **relativa ao diretório onde é executado**, então rode-o de dentro da pasta do script desejado (veja exemplos abaixo).

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

## 🚀 Como gerar os HTMLs (por script)

### 1. Carrossel Jornada do TCC (`ScriptCarroselTCC`)

Requer o arquivo `CSV/data.csv` na raiz do projeto, com colunas como `Aluno`, `Título do Trabalho`, `Orientador`, `Membro Banca 1/2/3`, `Data de Defesa`, `Horário` (ver [Colunas esperadas do CSV](#-colunas-esperadas-do-csv-carrossel-tcc)).

```bash
cd ScriptCarroselTCC
python gerar_html.py
```

- Agrupa apresentações por `Data de Defesa` e ordena por `Horário`.
- Mescla automaticamente em uma dupla ("Nome 1 e Nome 2") quando dois registros têm o mesmo `Título do Trabalho`.
- Gera um arquivo `Dia1.html`, `Dia2.html`, ... (um por data).

### 2. Calendário de Treinos RAJJ (`ScriptCalendarioRAJJ`)

```bash
cd ScriptCalendarioRAJJ
python gerar_html_rajj.py
```

- Usa a `Logo.JPG`/`Logo_transparente.png` da própria pasta para extrair as cores da marca.
- Gera `calendario_treinos_rajj.html` com a grade semanal de treinos.

### 3. Mapa de Disciplinas Flexibilizadas (`ScriptMapaDisciplinasFlexibilizadas`)

```bash
cd ScriptMapaDisciplinasFlexibilizadas
python gerar_html_mapa.py
```

- Os dados das disciplinas estão fixos no próprio script (função `obter_disciplinas_flexibilizadas()`); edite-a para atualizar o conteúdo.
- Gera `mapa_disciplinas_flexibilizadas.html`.

### 4. Slides do Projeto Manual (`ScriptProjetoManual`)

```bash
cd ScriptProjetoManual
python gerar_htmls.py
```

- Lê o texto de `Img/Texto.md` (uma linha por slide) e as imagens da pasta `Img/`.
- Gera `slide_01.html` a `slide_0N.html`.

### 5. Carrossel Prêmio Sebrae 2026 (`ScriptSebrae`)

```bash
cd ScriptSebrae
python gerar_html_premiacao_sebrae_2026.py
```

- Usa as fotos e logos da própria pasta (`Foto1.jpg`, `Foto2.jpg`, `Foto3.jpg`, `sebrae.png`, `bet.png`) e a logo da FASI em `html/fasiOficial.png` (na raiz).
- Gera 6 slides (1080x1350px) na pasta `ScriptSebrae/html/`.

## 🖼️ Como gerar as imagens (PNG) — `gerar_posts.py`

O `gerar_posts.py` fica na raiz do projeto e é **genérico**: renderiza qualquer HTML da pasta `html/` (relativa ao diretório atual) em PNG, com Playwright.

### Uso básico

Rode a partir da pasta do script cujo HTML você quer transformar em imagem:

```bash
cd ScriptCarroselTCC
python ../gerar_posts.py
```

Por padrão (`--plataforma original`), gera imagens em `original_posts/` com as dimensões originais do layout (1080x1350, ou página inteira para mapas).

### Variações por plataforma (`--plataforma`)

```bash
# Instagram (portrait 1080x1350, ou 1080x1080 para o mapa em modo "square")
python ../gerar_posts.py --plataforma instagram

# WhatsApp Status (quadrado 1080x1080)
python ../gerar_posts.py --plataforma whatsapp

# Layout original do HTML (sem recorte/redimensionamento por plataforma)
python ../gerar_posts.py --plataforma original

# Gera para as três plataformas de uma vez
python ../gerar_posts.py --plataforma todas
```

Isso cria as pastas `instagram_posts/`, `whatsapp_posts/` e/ou `original_posts/` dentro do diretório onde o comando foi executado.

### Processar um único arquivo (`--arquivo`)

```bash
python ../gerar_posts.py --arquivo html/Dia1.html --plataforma instagram
```

### Combinações úteis

```bash
# Gera HTML e, em seguida, os PNGs para todas as plataformas, em um só comando
cd ScriptCarroselTCC && python gerar_html.py && python ../gerar_posts.py --plataforma todas

# Gerar apenas o post do mapa de disciplinas para Instagram
cd ScriptMapaDisciplinasFlexibilizadas && python gerar_html_mapa.py && python ../gerar_posts.py --plataforma instagram

# Gerar o carrossel do Sebrae para WhatsApp
cd ScriptSebrae && python gerar_html_premiacao_sebrae_2026.py && python ../gerar_posts.py --plataforma whatsapp
```

### Detecção automática de tipo de conteúdo

O `gerar_posts.py` detecta automaticamente se o HTML é um "mapa" (busca por `MAPA DE DISCIPLINAS` no conteúdo ou `mapa_disciplinas` no nome do arquivo) ou um "carrossel" comum, e aplica a configuração de dimensão correta para cada plataforma:

| Plataforma | Carrossel/Post | Mapa (página inteira) |
|---|---|---|
| `instagram` | 1080x1350 (portrait) | 1080x1350 (full page) |
| `whatsapp` | 1080x1080 (square) | 1080x1350 (full page) |
| `original` | 1080x1350 (portrait) | 1200x1600 (full page) |

## 📁 Estrutura de Arquivos

```
GeradorImageFromHTML/
├── gerar_posts.py                          # Gerador genérico de imagens (todas as plataformas)
├── requirements.txt
├── README.md
├── CSV/
│   └── data.csv                            # Dados de entrada do Carrossel TCC
├── ScriptCarroselTCC/
│   ├── gerar_html.py
│   └── html/Dia1.html, Dia2.html, ...
├── ScriptCalendarioRAJJ/
│   ├── gerar_html_rajj.py
│   └── html/calendario_treinos_rajj.html
├── ScriptMapaDisciplinasFlexibilizadas/
│   ├── gerar_html_mapa.py
│   └── html/mapa_disciplinas_flexibilizadas.html
├── ScriptProjetoManual/
│   ├── gerar_htmls.py
│   ├── Img/Texto.md, image.png, ...
│   └── html/slide_01.html, ...
├── ScriptSebrae/
│   ├── gerar_html_premiacao_sebrae_2026.py
│   └── html/*.html
├── instagram_posts/  whatsapp_posts/  original_posts/   # Saídas geradas (por plataforma)
└── removeBackground/Script.py              # Utilitário para remover fundo de imagens (PIL)
```

## ⚙️ Colunas esperadas do CSV (Carrossel TCC)

O `CSV/data.csv` (codificação UTF-8, pode ter BOM) deve conter, entre outras, as colunas:

- `Aluno` — nome do aluno (formatado com title case)
- `Título do Trabalho` — título do TCC (formatado com title case; usado também para detectar duplas)
- `Orientador`, `Membro Banca 1`, `Membro Banca 2`, `Membro Banca 3`
- `Data de Defesa` — formato `YYYY-MM-DD` (aceita também `DD/MM/AA` e `DD/MM/AAAA`)
- `Horário` — formato `H:MM`, `HH:MM` ou `HH:MM:SS`

Quando dois registros têm o mesmo `Título do Trabalho`, o script os une automaticamente em um único card exibindo "Nome 1 e Nome 2", mantendo os demais dados originais do primeiro registro.

## 🔍 Solução de Problemas

### Erro: "No module named playwright"
```bash
pip install playwright
python -m playwright install chromium
```

### Erro: "❌ Nenhum arquivo HTML encontrado!" ao rodar `gerar_posts.py`
- Verifique se você está executando o comando de dentro da pasta do script (ex: `ScriptCarroselTCC/`), pois o `gerar_posts.py` procura a pasta `html/` relativa ao diretório atual.
- Confirme que o gerador de HTML correspondente já foi executado antes.

### `KeyError` ao rodar `gerar_html.py` do Carrossel TCC
- Verifique se as colunas do `CSV/data.csv` correspondem exatamente às listadas em [Colunas esperadas do CSV](#-colunas-esperadas-do-csv-carrossel-tcc).

### Erro: "File not found" ao gerar imagens
- Verifique se a logo `fasiOficial.png` está na pasta `html/` (raiz) referenciada pelo script.
- Verifique se os arquivos HTML foram gerados corretamente antes de rodar `gerar_posts.py`.

### Erro de renderização das imagens
- Verifique se o Chromium está instalado: `python -m playwright install chromium`.
- Teste o HTML gerado no navegador antes de gerar a imagem.

## 📊 Fluxo do Processo

```
Dados (CSV / Markdown / conteúdo fixo)
    ↓
gerar_html*.py (organiza, formata, gera o layout)
    ↓
HTML (um por slide/dia/página)
    ↓
gerar_posts.py --plataforma {instagram|whatsapp|original|todas}
    ↓
PNG (imagens prontas para publicação)
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
