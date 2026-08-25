#!/usr/bin/env python3
"""
Gerador de carrossel HTML — Prêmio de Inovação em Processos Organizacionais / UFPA 2026.

Contexto
--------
A Faculdade de Sistemas de Informação (FASI) do Campus Universitário do
Tocantins/Cametá conquistou o **1º lugar** no Edital de Inovação de Processos
Organizacionais da UFPA 2026 com o projeto *FasiTech*.

O que este script faz
---------------------
Ele resolve a etapa intermediária do fluxo de automação de imagens:

    [Design System] + [Mídia]  ──►  este script  ──►  HTMLs prontos
                                                            │
                                                            ▼
                                                    gerar_posts.py (Playwright)
                                                            │
                                                            ▼
                                                          PNGs

Entradas (todas configuráveis por linha de comando):

* ``--design-system``  pasta com estilos/tokens/templates e logotipos do evento;
* ``--midia``          pasta com as fotos (e opcionalmente o vídeo) da premiação;
* ``--saida``          pasta onde os arquivos ``.html`` serão gravados.

Saída: um arquivo HTML por slide, no formato 1080x1350 (Instagram retrato),
com todos os assets embutidos em ``data:`` URI — ou seja, cada HTML é
autocontido e pode ser renderizado isoladamente.

Uso
---
    python gerar_carrossel_proplan.py \
        --design-system "Design System" \
        --midia "Midia" \
        --saida "html"

    # Depois, na raiz do projeto:
    python gerar_posts.py --plataforma instagram --arquivo ScriptCarroselProplan/html/slide_01_capa.html

Autor: gerado para o fluxo de automação de posts da FASI/UFPA.
"""

from __future__ import annotations

import argparse
import base64
import html as _html
import json
import mimetypes
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Sequence

# ═══════════════════════════════════════════════════════════════════════════
# 1. CONSTANTES DE DOMÍNIO
# ═══════════════════════════════════════════════════════════════════════════

#: Extensões aceitas como imagem. Qualquer outro arquivo da pasta de mídia
#: é simplesmente ignorado (com aviso), conforme o requisito de robustez.
EXTENSOES_IMAGEM: frozenset[str] = frozenset(
    {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tif", ".tiff"}
)

#: Extensões aceitas como vídeo.
EXTENSOES_VIDEO: frozenset[str] = frozenset({".mp4", ".webm", ".mov", ".m4v"})

#: Dimensões padrão do slide (Instagram retrato 4:5).
LARGURA_PADRAO: int = 1080
ALTURA_PADRAO: int = 1350

#: Nome do template opcional que, se existir na raiz do Design System,
#: substitui o shell HTML embutido neste script.
NOME_TEMPLATE_BASE: str = "template_base.html"


# ═══════════════════════════════════════════════════════════════════════════
# 2. CONTEÚDO EDITORIAL
#    Tudo que é texto fica centralizado aqui — para reaproveitar o script em
#    outro evento basta editar este bloco (ou passar outro módulo de conteúdo).
# ═══════════════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class Conteudo:
    """Textos fixos do carrossel (independentes do Design System)."""

    evento: str = "Prêmio de Inovação em Processos Organizacionais"
    edicao: str = "UFPA 2026"
    colocacao: str = "1º Lugar"
    projeto_curto: str = "FasiTech"
    projeto_completo: str = (
        "Plataforma Digital Integrada para Gestão Acadêmica "
        "em Campus Multicampi no Interior da Amazônia"
    )
    unidade: str = "Faculdade de Sistemas de Informação — FASI"
    campus: str = "Campus Universitário do Tocantins/Cametá"
    instituicao: str = "Universidade Federal do Pará"
    organizador: str = "PROPLAN · UFPA"
    assinatura: str = "@laboratoriofasi"

    #: Substring usada para escolher qual foto vira o fundo da capa.
    #: Se nenhuma casar, a primeira foto da ordenação é usada.
    foto_capa_preferida: str = "doriedson"

    #: Cards de destaque do slide "O Projeto".
    destaques: tuple[tuple[str, str, str], ...] = (
        (
            "🗂️",
            "10 processos digitalizados",
            "Fluxos acadêmicos em papel substituídos por trâmites totalmente digitais.",
        ),
        (
            "🌎",
            "3 polos integrados",
            "Cametá e polos do interior atendidos por um único ambiente institucional.",
        ),
        (
            "🤖",
            "Inteligência Artificial",
            "Leitura automática de certificados e atendimento virtual ao discente.",
        ),
        (
            "📊",
            "Gestão orientada a dados",
            "Informação rastreável para decisões acadêmicas mais ágeis e transparentes.",
        ),
    )

    #: Coordenação do projeto premiado.
    equipe: tuple[tuple[str, str], ...] = (
        ("Prof. Dr. Elton Sarmanho Siqueira", "Coordenação do Projeto"),
        ("Prof. Dr. Carlos dos Santos Portela", "Coordenação do Projeto"),
    )

    #: Instituições/instâncias agradecidas no slide de encerramento.
    agradecimentos: tuple[str, ...] = (
        "Coordenação do Campus Universitário do Tocantins/Cametá",
        "Direção da Faculdade de Sistemas de Informação (FASI)",
        "Pró-Reitoria de Planejamento e Desenvolvimento Institucional (PROPLAN)",
    )

    mensagem_final: str = (
        "Um resultado que consolida anos de trabalho coletivo na gestão e no "
        "mapeamento de processos administrativos da UFPA."
    )


#: Legendas dos slides de foto, indexadas por trecho do nome do arquivo
#: (comparação em minúsculas). A chave mais longa que casar vence.
LEGENDAS_POR_ARQUIVO: dict[str, tuple[str, str]] = {
    "capa_premio": (
        "O anúncio do 1º lugar",
        "A FasiTech vence o Prêmio de Inovação em Processos "
        "Organizacionais da UFPA 2026.",
    ),
    "elton_carlos_doriedson_fabricio": (
        "A conquista é do Campus",
        "Coordenação do Campus de Cametá e docentes da FASI reunidos "
        "na cerimônia de premiação.",
    ),
    "elton_carlos": (
        "Troféu e certificado",
        "Prof. Elton Sarmanho Siqueira e Prof. Carlos dos Santos Portela "
        "recebem a premiação.",
    ),
}

#: Ordem editorial preferida das fotos no carrossel (por trecho do nome).
#: Arquivos não listados vão para o fim, em ordem alfabética.
ORDEM_PREFERIDA: tuple[str, ...] = (
    "capa_premio",
    "elton_carlos.",
    "doriedson",
)

#: Enquadramento da foto dentro da moldura, por trecho do nome do arquivo.
#:
#: * ``cover``   (padrão) preenche a moldura cortando as bordas — ideal para
#:               retratos e fotos de ambiente;
#: * ``contain`` mostra a foto inteira sobre um fundo desfocado da própria
#:               imagem — obrigatório para fotos de telas projetadas,
#:               certificados e documentos, cujo texto não pode ser cortado.
AJUSTE_POR_ARQUIVO: dict[str, str] = {
    "capa_premio": "contain",
    "certificado": "contain",
    "slide": "contain",
    "tela": "contain",
}


# ═══════════════════════════════════════════════════════════════════════════
# 3. DESIGN SYSTEM — leitura de tokens, estilos e logotipos
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class TokensDesign:
    """
    Tokens visuais do evento.

    Os valores começam com o padrão extraído da identidade do Prêmio
    (banner oficial + página da PROPLAN) e podem ser sobrescritos por
    ``tokens.json`` ou por variáveis CSS ``--nome: valor`` encontradas
    na pasta do Design System.
    """

    verde_noite: str = "#071F1D"
    verde_fundo: str = "#0B2B28"
    verde_escuro: str = "#01544A"
    verde_medio: str = "#1D8679"
    menta: str = "#8FC9BE"
    dourado: str = "#E0A12E"
    dourado_claro: str = "#F5C25B"
    branco: str = "#F4F8F7"
    cinza: str = "#9FB6B1"
    borda: str = "rgba(143, 201, 190, 0.22)"

    #: Data URIs dos logotipos localizados (chave → data URI).
    logos: dict[str, str] = field(default_factory=dict)
    #: Blocos ``@font-face`` gerados a partir das fontes do Design System.
    fontes_css: str = ""
    #: CSS adicional do autor (arquivos ``.css`` na raiz do Design System).
    css_autoral: str = ""
    #: Shell HTML customizado (``template_base.html``), se existir.
    template_base: str | None = None

    def como_variaveis_css(self) -> str:
        """Serializa os tokens de cor como custom properties CSS."""
        pares = {
            "--verde-noite": self.verde_noite,
            "--verde-fundo": self.verde_fundo,
            "--verde-escuro": self.verde_escuro,
            "--verde-medio": self.verde_medio,
            "--menta": self.menta,
            "--dourado": self.dourado,
            "--dourado-claro": self.dourado_claro,
            "--branco": self.branco,
            "--cinza": self.cinza,
            "--borda": self.borda,
        }
        return "\n".join(f"        {k}: {v};" for k, v in pares.items())


#: Mapeia nome lógico do logo → trechos de nome de arquivo a procurar.
_PADROES_LOGO: dict[str, tuple[str, ...]] = {
    "ufpa": ("logo_ufpa", "ufpa.png", "ufpa"),
    "premio": ("banner-premio", "banner_premio", "premio"),
    "icone_premio": ("icone-edital-premio", "icone-premio"),
}

#: Mapeia peso da fonte → trecho do nome do arquivo ``.woff``.
_PADROES_FONTE: dict[int, str] = {
    400: "opensans-400",
    600: "opensans-600",
    700: "opensans-700",
}


def carregar_design_system(pasta: Path) -> TokensDesign:
    """
    Lê a pasta do Design System e devolve os tokens consolidados.

    A leitura é *best-effort*: nenhum arquivo é obrigatório. Se a pasta só
    tiver imagens, os tokens padrão do Prêmio continuam valendo.

    Ordem de precedência (do menos para o mais forte):
        1. valores padrão da classe :class:`TokensDesign`;
        2. gradiente detectado no(s) HTML(s) do Design System;
        3. variáveis CSS ``--nome: valor`` declaradas em ``:root``;
        4. ``tokens.json`` / ``design-tokens.json``.
    """
    if not pasta.is_dir():
        raise NotADirectoryError(f"Pasta do Design System não encontrada: {pasta}")

    tokens = TokensDesign()

    _aplicar_gradiente_do_html(pasta, tokens)
    _aplicar_variaveis_css(pasta, tokens)
    _aplicar_tokens_json(pasta, tokens)

    tokens.logos = _localizar_logos(pasta)
    tokens.fontes_css = _montar_fontes(pasta)
    tokens.css_autoral = _ler_css_autoral(pasta)
    tokens.template_base = _ler_template_base(pasta)

    return tokens


def _arquivos(pasta: Path, sufixo: str) -> list[Path]:
    """Lista recursivamente arquivos com o sufixo dado (case-insensitive)."""
    return sorted(p for p in pasta.rglob("*") if p.is_file() and p.suffix.lower() == sufixo)


def _aplicar_gradiente_do_html(pasta: Path, tokens: TokensDesign) -> None:
    """
    Detecta o gradiente institucional nos HTMLs do Design System.

    A página do Prêmio usa ``linear-gradient(135deg, #01544A 0%, #1D8679 100%)``
    como bloco de destaque; reaproveitamos essas duas cores como verde escuro
    e verde médio do carrossel.
    """
    padrao = re.compile(
        r"linear-gradient\(\s*135deg\s*,\s*(#[0-9a-fA-F]{6})[^,]*,\s*(#[0-9a-fA-F]{6})"
    )
    for arquivo in _arquivos(pasta, ".html"):
        if arquivo.name == NOME_TEMPLATE_BASE:
            continue
        try:
            texto = arquivo.read_text(encoding="utf-8", errors="ignore")
        except OSError as erro:
            print(f"  ⚠️  Não foi possível ler {arquivo.name}: {erro}")
            continue
        achado = padrao.search(texto)
        if achado:
            tokens.verde_escuro, tokens.verde_medio = achado.group(1), achado.group(2)
            return


def _aplicar_variaveis_css(pasta: Path, tokens: TokensDesign) -> None:
    """
    Sobrescreve tokens a partir de custom properties CSS.

    Reconhece nomes no formato ``--verde-medio``, ``--dourado`` etc.
    (o hífen é normalizado para underscore ao casar com o atributo).
    """
    padrao = re.compile(r"--([a-zA-Z0-9_-]+)\s*:\s*([^;{}]+);")
    conhecidos = {c for c in vars(TokensDesign()) if isinstance(getattr(tokens, c), str)}

    for arquivo in _arquivos(pasta, ".css"):
        try:
            texto = arquivo.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for nome, valor in padrao.findall(texto):
            atributo = nome.strip().replace("-", "_").lower()
            if atributo in conhecidos:
                setattr(tokens, atributo, valor.strip())


def _aplicar_tokens_json(pasta: Path, tokens: TokensDesign) -> None:
    """Sobrescreve tokens a partir de um arquivo JSON de design tokens."""
    candidatos = [
        p
        for p in _arquivos(pasta, ".json")
        if any(chave in p.stem.lower() for chave in ("token", "design", "tema", "theme"))
    ]
    for arquivo in candidatos:
        try:
            dados = json.loads(arquivo.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as erro:
            print(f"  ⚠️  Tokens JSON ignorados ({arquivo.name}): {erro}")
            continue
        if not isinstance(dados, dict):
            continue
        # Aceita tanto {"cores": {...}} quanto {...} no nível raiz.
        cores = dados.get("cores") or dados.get("colors") or dados
        if not isinstance(cores, dict):
            continue
        for nome, valor in cores.items():
            atributo = str(nome).replace("-", "_").lower()
            if isinstance(valor, str) and hasattr(tokens, atributo):
                setattr(tokens, atributo, valor)


def _localizar_logos(pasta: Path) -> dict[str, str]:
    """Procura os logotipos do evento e devolve seus ``data:`` URIs."""
    imagens = [
        p
        for p in pasta.rglob("*")
        if p.is_file() and p.suffix.lower() in EXTENSOES_IMAGEM
    ]
    encontrados: dict[str, str] = {}

    for chave, padroes in _PADROES_LOGO.items():
        for padrao in padroes:
            achado = next((p for p in imagens if padrao in p.name.lower()), None)
            if achado is not None:
                try:
                    encontrados[chave] = para_data_uri(achado)
                except OSError as erro:
                    print(f"  ⚠️  Logo '{chave}' ilegível ({achado.name}): {erro}")
                break
        else:
            print(f"  ⚠️  Logo '{chave}' não localizado no Design System.")

    return encontrados


def _montar_fontes(pasta: Path) -> str:
    """
    Gera blocos ``@font-face`` embutindo as fontes ``.woff`` do Design System.

    Assim o slide não depende de rede para renderizar a tipografia
    institucional (Open Sans, padrão de governo).
    """
    arquivos = [
        p for p in pasta.rglob("*") if p.is_file() and p.suffix.lower() in {".woff", ".woff2"}
    ]
    blocos: list[str] = []

    for peso, padrao in _PADROES_FONTE.items():
        achado = next((p for p in arquivos if padrao in p.name.lower()), None)
        if achado is None:
            continue
        try:
            uri = para_data_uri(achado)
        except OSError:
            continue
        formato = "woff2" if achado.suffix.lower() == ".woff2" else "woff"
        blocos.append(
            f"""    @font-face {{
        font-family: 'Open Sans DS';
        src: url({uri}) format('{formato}');
        font-weight: {peso};
        font-style: normal;
        font-display: block;
    }}"""
        )

    return "\n".join(blocos)


def _ler_css_autoral(pasta: Path) -> str:
    """
    Concatena os ``.css`` que estiverem na *raiz* da pasta do Design System.

    Só a raiz é lida de propósito: subpastas como ``assets/`` costumam conter
    frameworks inteiros (Bootstrap, Font Awesome) que quebrariam o layout
    fechado do slide.
    """
    partes: list[str] = []
    for arquivo in sorted(pasta.glob("*.css")):
        try:
            partes.append(f"/* ← {arquivo.name} */\n{arquivo.read_text(encoding='utf-8')}")
        except OSError as erro:
            print(f"  ⚠️  CSS ignorado ({arquivo.name}): {erro}")
    return "\n\n".join(partes)


def _ler_template_base(pasta: Path) -> str | None:
    """Lê o shell HTML customizado, se o autor tiver fornecido um."""
    caminho = pasta / NOME_TEMPLATE_BASE
    if not caminho.is_file():
        return None
    try:
        return caminho.read_text(encoding="utf-8")
    except OSError as erro:
        print(f"  ⚠️  {NOME_TEMPLATE_BASE} ignorado: {erro}")
        return None


# ═══════════════════════════════════════════════════════════════════════════
# 4. DESCOBERTA DE MÍDIA
# ═══════════════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class Midia:
    """Um arquivo de mídia válido encontrado na pasta de fotos."""

    caminho: Path
    tipo: str  # "imagem" | "video"

    @property
    def chave(self) -> str:
        """Nome do arquivo em minúsculas — usado para casar legendas/ordem."""
        return self.caminho.name.lower()

    @property
    def rotulo(self) -> str:
        """Nome legível derivado do arquivo (fallback de legenda)."""
        return self.caminho.stem.replace("_", " ").replace("-", " ").strip()


def descobrir_midias(pasta: Path) -> tuple[list[Midia], list[Midia]]:
    """
    Varre a pasta de mídia e separa imagens de vídeos.

    Arquivos com extensão desconhecida são ignorados com aviso — é o
    tratamento de erro básico pedido no requisito.

    Returns:
        Tupla ``(imagens, videos)`` já ordenada segundo :data:`ORDEM_PREFERIDA`.
    """
    if not pasta.is_dir():
        raise NotADirectoryError(f"Pasta de mídia não encontrada: {pasta}")

    imagens: list[Midia] = []
    videos: list[Midia] = []

    for arquivo in sorted(pasta.iterdir()):
        if not arquivo.is_file() or arquivo.name.startswith("."):
            continue
        sufixo = arquivo.suffix.lower()
        if sufixo in EXTENSOES_IMAGEM:
            imagens.append(Midia(arquivo, "imagem"))
        elif sufixo in EXTENSOES_VIDEO:
            videos.append(Midia(arquivo, "video"))
        else:
            print(f"  ⏭️  Ignorado (não é imagem/vídeo): {arquivo.name}")

    if not imagens:
        raise FileNotFoundError(
            f"Nenhuma imagem válida em {pasta}. "
            f"Extensões aceitas: {', '.join(sorted(EXTENSOES_IMAGEM))}"
        )

    return _ordenar(imagens), videos


def _ordenar(itens: Sequence[Midia]) -> list[Midia]:
    """Ordena pela lista editorial :data:`ORDEM_PREFERIDA`; o resto vai ao fim."""

    def posicao(midia: Midia) -> tuple[int, str]:
        for indice, trecho in enumerate(ORDEM_PREFERIDA):
            if trecho in midia.chave:
                return (indice, midia.chave)
        return (len(ORDEM_PREFERIDA), midia.chave)

    return sorted(itens, key=posicao)


def legenda_de(midia: Midia) -> tuple[str, str]:
    """
    Resolve título e subtítulo da foto.

    Casa o nome do arquivo contra :data:`LEGENDAS_POR_ARQUIVO` preferindo a
    chave mais específica (mais longa). Sem correspondência, gera uma legenda
    genérica a partir do próprio nome do arquivo.
    """
    candidatas = [ch for ch in LEGENDAS_POR_ARQUIVO if ch in midia.chave]
    if candidatas:
        return LEGENDAS_POR_ARQUIVO[max(candidatas, key=len)]
    return (
        midia.rotulo.title(),
        f"Registro da cerimônia do {CONTEUDO.evento} — {CONTEUDO.edicao}.",
    )


def ajuste_de(midia: Midia) -> str:
    """
    Resolve o enquadramento (``cover`` ou ``contain``) de uma foto.

    Consulta :data:`AJUSTE_POR_ARQUIVO` preferindo a chave mais específica.
    """
    candidatas = [ch for ch in AJUSTE_POR_ARQUIVO if ch in midia.chave]
    if candidatas:
        return AJUSTE_POR_ARQUIVO[max(candidatas, key=len)]
    return "cover"


def escolher_foto_capa(imagens: Sequence[Midia]) -> Midia:
    """Escolhe a foto de fundo da capa segundo :attr:`Conteudo.foto_capa_preferida`."""
    preferida = CONTEUDO.foto_capa_preferida.lower()
    return next((img for img in imagens if preferida in img.chave), imagens[0])


# ═══════════════════════════════════════════════════════════════════════════
# 5. UTILIDADES
# ═══════════════════════════════════════════════════════════════════════════


def para_data_uri(caminho: Path) -> str:
    """
    Converte um arquivo em ``data:`` URI base64.

    Embutir os assets deixa cada HTML autocontido — importante porque o
    conversor abre o arquivo via ``file://`` e não teria como resolver
    caminhos relativos para fora da pasta de saída.
    """
    mime, _ = mimetypes.guess_type(caminho.name)
    if mime is None:
        mime = "application/octet-stream"
    dados = base64.b64encode(caminho.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{dados}"


def esc(texto: str) -> str:
    """Escapa texto para inserção segura no HTML."""
    return _html.escape(str(texto), quote=True)


def extrair_frame(video: Path, destino: Path, segundo: float = 1.0) -> Path | None:
    """
    Extrai um frame do vídeo para servir de ``poster``.

    Usa ``ffmpeg`` se estiver disponível no PATH. Se não estiver (ou se falhar),
    devolve ``None`` e o chamador cai no fallback de usar uma foto como poster —
    o slide continua sendo gerado normalmente.
    """
    if shutil.which("ffmpeg") is None:
        return None

    destino.parent.mkdir(parents=True, exist_ok=True)
    comando = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-ss", str(segundo), "-i", str(video),
        "-frames:v", "1", str(destino),
    ]
    try:
        subprocess.run(comando, check=True, capture_output=True, timeout=30)
    except (FileNotFoundError, subprocess.SubprocessError):
        return None
    return destino if destino.is_file() else None


# ═══════════════════════════════════════════════════════════════════════════
# 6. CAMADA DE TEMPLATES (HTML/CSS)
# ═══════════════════════════════════════════════════════════════════════════


def css_base(tokens: TokensDesign, largura: int, altura: int) -> str:
    """CSS compartilhado por todos os slides — reset, paleta, header e footer."""
    return f"""
{tokens.fontes_css}

    :root {{
{tokens.como_variaveis_css()}
        --slide-w: {largura}px;
        --slide-h: {altura}px;
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
        display: flex; justify-content: center; align-items: center;
        min-height: 100vh; background: #101314;
        font-family: 'Open Sans DS', 'Inter', 'Segoe UI', Arial, sans-serif;
        -webkit-font-smoothing: antialiased;
    }}

    /* ── Palco do slide ────────────────────────────────────────────── */
    .slide {{
        width: var(--slide-w); height: var(--slide-h);
        position: relative; overflow: hidden;
        display: flex; flex-direction: column;
        color: var(--branco);
        background: linear-gradient(158deg,
            var(--verde-noite) 0%,
            var(--verde-fundo) 38%,
            var(--verde-escuro) 100%);
        box-shadow: 0 0 60px rgba(0, 0, 0, .55);
    }}

    /* Brilhos atmosféricos */
    .slide::before {{
        content: ""; position: absolute; inset: 0; z-index: 0; pointer-events: none;
        background:
            radial-gradient(ellipse 620px 420px at 12% 6%, rgba(29, 134, 121, .38) 0%, transparent 70%),
            radial-gradient(ellipse 540px 460px at 92% 88%, rgba(224, 161, 46, .16) 0%, transparent 72%);
    }}

    /* Malha discreta */
    .slide::after {{
        content: ""; position: absolute; inset: 0; z-index: 0; pointer-events: none;
        background-image:
            linear-gradient(rgba(255, 255, 255, .022) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, .022) 1px, transparent 1px);
        background-size: 64px 64px;
    }}

    .slide > * {{ position: relative; z-index: 1; }}

    /* ── Cabeçalho ─────────────────────────────────────────────────── */
    .cabecalho {{
        display: flex; align-items: center; justify-content: space-between;
        gap: 20px; padding: 44px 52px 20px;
    }}
    .cabecalho .marca {{ display: flex; align-items: center; gap: 16px; }}
    .cabecalho img.logo-ufpa {{ height: 74px; object-fit: contain; }}
    .cabecalho .divisor {{
        width: 2px; height: 52px; border-radius: 2px;
        background: linear-gradient(180deg, var(--dourado), transparent);
    }}
    .cabecalho .marca-texto {{ line-height: 1.25; }}
    .cabecalho .marca-texto .linha1 {{
        font-size: 15px; font-weight: 700; letter-spacing: 2.4px;
        text-transform: uppercase; color: var(--menta);
    }}
    .cabecalho .marca-texto .linha2 {{
        font-size: 13px; font-weight: 400; color: var(--cinza); letter-spacing: .6px;
    }}

    .selo-evento {{
        display: inline-flex; align-items: center; gap: 8px; flex-shrink: 0;
        padding: 9px 18px; border-radius: 999px;
        background: rgba(224, 161, 46, .12);
        border: 1px solid rgba(224, 161, 46, .38);
        color: var(--dourado-claro);
        font-size: 13px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase;
    }}

    /* ── Rodapé ────────────────────────────────────────────────────── */
    .rodape {{
        margin-top: auto;
        display: flex; align-items: center; justify-content: space-between;
        gap: 18px; padding: 22px 52px 34px;
    }}
    .rodape .assinatura {{
        font-size: 16px; font-weight: 600; color: var(--cinza); letter-spacing: .4px;
    }}
    .rodape .contador {{
        padding: 6px 16px; border-radius: 999px;
        background: rgba(143, 201, 190, .12);
        border: 1px solid var(--borda);
        font-size: 14px; font-weight: 700; color: var(--menta); letter-spacing: 1.2px;
    }}
    .barra-rodape {{
        position: absolute; left: 0; right: 0; bottom: 0; height: 7px;
        background: linear-gradient(90deg,
            var(--dourado) 0%, var(--verde-medio) 45%,
            var(--menta) 72%, var(--dourado) 100%);
    }}

    /* ── Tipografia utilitária ─────────────────────────────────────── */
    .titulo-display {{
        font-weight: 800; letter-spacing: -1.2px; line-height: 1.06;
        text-transform: uppercase;
    }}
    .destaque-dourado {{ color: var(--dourado-claro); }}
    .destaque-menta {{ color: var(--menta); }}

    .selo-colocacao {{
        display: inline-flex; align-items: center; gap: 12px;
        padding: 14px 34px; border-radius: 999px;
        background: linear-gradient(120deg, var(--dourado) 0%, var(--dourado-claro) 100%);
        color: #23180A; font-size: 30px; font-weight: 800;
        letter-spacing: 2px; text-transform: uppercase;
        box-shadow: 0 10px 30px rgba(224, 161, 46, .34);
    }}

    .cartao {{
        background: rgba(255, 255, 255, .045);
        border: 1px solid var(--borda);
        border-radius: 18px;
    }}
"""


def montar_pagina(
    titulo: str,
    corpo: str,
    tokens: TokensDesign,
    largura: int,
    altura: int,
    css_extra: str = "",
) -> str:
    """
    Monta o documento HTML final.

    Se o Design System trouxer um ``template_base.html``, ele é usado como
    shell e os marcadores ``{{titulo}}``, ``{{css}}``, ``{{corpo}}``,
    ``{{largura}}`` e ``{{altura}}`` são substituídos. Caso contrário usa-se
    o shell embutido abaixo.
    """
    css = "\n".join(
        parte
        for parte in (css_base(tokens, largura, altura), css_extra, tokens.css_autoral)
        if parte.strip()
    )

    if tokens.template_base:
        pagina = tokens.template_base
        # Marcadores curtos podem aparecer mais de uma vez (ex.: largura no
        # <meta viewport> e num estilo inline) — substituímos todos.
        for chave, valor in (
            ("titulo", esc(titulo)),
            ("largura", str(largura)),
            ("altura", str(altura)),
        ):
            pagina = pagina.replace("{{" + chave + "}}", valor)
        # Já os blocos pesados entram só na primeira ocorrência: repetir CSS
        # ou corpo é sempre erro (e infla o arquivo em centenas de KB).
        for chave, valor in (("css", css), ("corpo", corpo)):
            pagina = pagina.replace("{{" + chave + "}}", valor, 1)
        return pagina

    return f"""<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width={largura}, initial-scale=1">
<title>{esc(titulo)}</title>
<style>
{css}
</style>
</head>
<body>
<div class="slide">
{corpo}
</div>
</body>
</html>
"""


def bloco_cabecalho(tokens: TokensDesign, selo: str | None = None) -> str:
    """Cabeçalho institucional: logo da UFPA + identificação + selo do evento."""
    logo = tokens.logos.get("ufpa", "")
    img = f'<img class="logo-ufpa" src="{logo}" alt="UFPA">' if logo else ""
    texto_selo = selo or f"{CONTEUDO.evento.split(' em ')[0]} · {CONTEUDO.edicao}"
    return f"""    <header class="cabecalho">
      <div class="marca">
        {img}
        <div class="divisor"></div>
        <div class="marca-texto">
          <div class="linha1">{esc(CONTEUDO.organizador)}</div>
          <div class="linha2">{esc(CONTEUDO.instituicao)}</div>
        </div>
      </div>
      <div class="selo-evento">{esc(texto_selo)}</div>
    </header>"""


def bloco_rodape(numero: int, total: int, assinatura: str | None = None) -> str:
    """Rodapé com assinatura, paginação do carrossel e barra colorida."""
    return f"""    <footer class="rodape">
      <span class="assinatura">{esc(assinatura or CONTEUDO.assinatura)}</span>
      <span class="contador">{numero:02d} / {total:02d}</span>
    </footer>
    <div class="barra-rodape"></div>"""


# ── Slides ─────────────────────────────────────────────────────────────────


def slide_capa(
    tokens: TokensDesign,
    numero: int,
    total: int,
    largura: int,
    altura: int,
    foto_uri: str | None = None,
) -> str:
    """
    Slide 1 — capa: banner do Prêmio, selo de 1º lugar e nome do projeto.

    Args:
        foto_uri: quando informado, entra como fundo esmaecido atrás do texto.
            O padrão é ``None`` (fundo só com o gradiente institucional), que
            deixa a leitura bem mais limpa. Ative com ``--capa-com-foto``.
    """
    banner = tokens.logos.get("premio", "")
    banner_html = (
        f'<img class="banner-premio" src="{banner}" alt="{esc(CONTEUDO.evento)}">'
        if banner
        else ""
    )
    fundo_html = (
        f'    <div class="capa-fundo"><img src="{foto_uri}" alt=""></div>\n'
        if foto_uri
        else ""
    )

    css = """
    /* Fundo fotográfico opcional (--capa-com-foto) */
    .capa-fundo { position: absolute; inset: 0; z-index: 0; }
    .capa-fundo img {
        width: 100%; height: 100%; object-fit: cover; object-position: center 38%;
        filter: saturate(.85) contrast(1.02);
    }
    .capa-fundo::after {
        content: ""; position: absolute; inset: 0;
        background: linear-gradient(180deg,
            rgba(7, 31, 29, .92) 0%,
            rgba(7, 31, 29, .78) 38%,
            rgba(1, 84, 74, .90) 72%,
            rgba(7, 31, 29, .97) 100%);
    }

    .capa-conteudo {
        flex: 1; display: flex; flex-direction: column;
        justify-content: center; align-items: center; text-align: center;
        gap: 30px; padding: 0 70px;
    }
    .banner-premio {
        width: 580px; max-width: 100%; height: auto;
        border-radius: 14px; box-shadow: 0 12px 34px rgba(0, 0, 0, .42);
    }
    .capa-projeto { font-size: 96px; letter-spacing: -3px; }
    .capa-descricao {
        font-size: 25px; line-height: 1.42; font-weight: 400;
        color: rgba(244, 248, 247, .90); max-width: 830px;
    }
    .capa-unidade {
        display: flex; flex-direction: column; gap: 5px;
        padding: 18px 34px; border-radius: 16px;
        background: rgba(0, 0, 0, .22);
        border: 1px solid var(--borda);
    }
    .capa-unidade .u1 {
        font-size: 19px; font-weight: 700; letter-spacing: .4px; color: var(--menta);
    }
    .capa-unidade .u2 { font-size: 17px; color: var(--cinza); }

    /* Chamada de arraste — típica de carrossel */
    .capa-arraste {
        display: inline-flex; align-items: center; gap: 14px;
        padding: 13px 30px; border-radius: 999px;
        background: rgba(143, 201, 190, .10);
        border: 1px solid var(--borda);
        font-size: 16px; font-weight: 700; letter-spacing: 2.4px;
        text-transform: uppercase; color: var(--menta);
    }
    .capa-arraste .seta { font-size: 22px; color: var(--dourado-claro); }
    """

    corpo = f"""{fundo_html}{bloco_cabecalho(tokens)}

    <div class="capa-conteudo">
      {banner_html}

      <div class="selo-colocacao">🏆 {esc(CONTEUDO.colocacao)}</div>

      <h1 class="titulo-display capa-projeto">
        Fasi<span class="destaque-dourado">Tech</span>
      </h1>

      <p class="capa-descricao">{esc(CONTEUDO.projeto_completo)}</p>

      <div class="capa-unidade">
        <span class="u1">{esc(CONTEUDO.unidade)}</span>
        <span class="u2">{esc(CONTEUDO.campus)}</span>
      </div>

      <div class="capa-arraste">
        <span>Arraste para ver</span><span class="seta">→</span>
      </div>
    </div>

{bloco_rodape(numero, total)}"""
    return montar_pagina("Slide 01 — Capa", corpo, tokens, largura, altura, css)


def slide_projeto(
    tokens: TokensDesign, numero: int, total: int, largura: int, altura: int
) -> str:
    """Slide 2 — o projeto: título + cards de destaque da solução premiada."""
    cartoes = "".join(
        f"""
        <div class="cartao destaque">
          <div class="icone">{icone}</div>
          <div class="texto">
            <div class="d-titulo">{esc(titulo)}</div>
            <div class="d-desc">{esc(descricao)}</div>
          </div>
        </div>"""
        for icone, titulo, descricao in CONTEUDO.destaques
    )

    css = """
    .conteudo {
        flex: 1; display: flex; flex-direction: column;
        gap: 26px; padding: 14px 56px 10px;
    }
    .rotulo-secao {
        font-size: 15px; font-weight: 700; letter-spacing: 3.4px;
        text-transform: uppercase; color: var(--dourado-claro);
    }
    .titulo-secao { font-size: 58px; letter-spacing: -1.6px; }
    .subtitulo-secao {
        font-size: 21px; line-height: 1.48; color: rgba(244, 248, 247, .82);
        max-width: 880px;
    }
    .lista-destaques {
        flex: 1; display: flex; flex-direction: column;
        justify-content: center; gap: 22px; margin-top: 4px;
    }
    .destaque {
        display: flex; align-items: flex-start; gap: 22px; padding: 24px 26px;
        border-left: 5px solid var(--dourado);
    }
    .destaque .icone { font-size: 40px; line-height: 1; flex-shrink: 0; }
    .destaque .d-titulo {
        font-size: 24px; font-weight: 700; color: var(--branco); margin-bottom: 6px;
    }
    .destaque .d-desc {
        font-size: 18px; line-height: 1.5; color: rgba(244, 248, 247, .76);
    }
    """

    corpo = f"""{bloco_cabecalho(tokens, "O Projeto")}

    <div class="conteudo">
      <div>
        <div class="rotulo-secao">Ação premiada</div>
        <h2 class="titulo-display titulo-secao">
          O que é a <span class="destaque-dourado">FasiTech</span>
        </h2>
      </div>

      <p class="subtitulo-secao">
        Plataforma desenvolvida no {esc(CONTEUDO.campus)} que digitaliza processos
        acadêmicos, integra polos do interior e aplica inteligência artificial
        no atendimento ao discente.
      </p>

      <div class="lista-destaques">{cartoes}
      </div>
    </div>

{bloco_rodape(numero, total)}"""
    return montar_pagina("Slide 02 — O Projeto", corpo, tokens, largura, altura, css)


def slide_foto(
    foto_uri: str,
    titulo: str,
    subtitulo: str,
    tokens: TokensDesign,
    numero: int,
    total: int,
    largura: int,
    altura: int,
    ajuste: str = "cover",
) -> str:
    """
    Slide de foto — moldura arredondada, gradiente de leitura e legenda.

    Args:
        ajuste: ``cover`` preenche a moldura (corta bordas); ``contain`` exibe
            a foto inteira sobre um fundo desfocado dela mesma, preservando
            textos de telas projetadas e certificados.
    """
    css = """
    .moldura {
        flex: 1; position: relative; overflow: hidden;
        margin: 6px 44px 8px; border-radius: 24px;
        border: 1px solid var(--borda);
        box-shadow: 0 18px 48px rgba(0, 0, 0, .46);
        background: var(--verde-noite);
    }
    .moldura > img.principal {
        position: absolute; inset: 0;
        width: 100%; height: 100%; object-fit: cover; object-position: center;
    }
    /* Fundo desfocado usado apenas no enquadramento "contain" */
    .moldura > img.fundo {
        position: absolute; inset: -8%;
        width: 116%; height: 116%; object-fit: cover;
        filter: blur(34px) brightness(.42) saturate(.7);
    }
    .moldura.contido > img.principal {
        object-fit: contain; padding: 26px 18px 150px;
    }
    .veu {
        position: absolute; inset: 0;
        background: linear-gradient(180deg,
            rgba(7, 31, 29, .34) 0%,
            rgba(7, 31, 29, .04) 34%,
            rgba(7, 31, 29, .74) 74%,
            rgba(7, 31, 29, .95) 100%);
    }
    .fita-superior {
        position: absolute; top: 22px; left: 22px;
        display: inline-flex; align-items: center; gap: 10px;
        padding: 9px 20px; border-radius: 999px;
        background: rgba(7, 31, 29, .72);
        border: 1px solid rgba(224, 161, 46, .5);
        color: var(--dourado-claro);
        font-size: 14px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase;
        backdrop-filter: blur(4px);
    }
    .legenda {
        position: absolute; left: 34px; right: 34px; bottom: 32px;
    }
    .legenda .traco {
        width: 76px; height: 5px; border-radius: 3px; margin-bottom: 16px;
        background: linear-gradient(90deg, var(--dourado), var(--menta));
    }
    .legenda .l-titulo {
        font-size: 40px; font-weight: 800; line-height: 1.14; letter-spacing: -.8px;
        text-shadow: 0 2px 12px rgba(0, 0, 0, .55); margin-bottom: 10px;
    }
    .legenda .l-sub {
        font-size: 20px; line-height: 1.46; color: rgba(244, 248, 247, .88);
        text-shadow: 0 1px 8px rgba(0, 0, 0, .5); max-width: 860px;
    }
    """

    contido = ajuste == "contain"
    classe = "moldura contido" if contido else "moldura"
    fundo = f'<img class="fundo" src="{foto_uri}" alt="">' if contido else ""

    corpo = f"""{bloco_cabecalho(tokens)}

    <div class="{classe}">
      {fundo}
      <img class="principal" src="{foto_uri}" alt="{esc(titulo)}">
      <div class="veu"></div>
      <div class="fita-superior">🏆 {esc(CONTEUDO.colocacao)} · {esc(CONTEUDO.edicao)}</div>
      <div class="legenda">
        <div class="traco"></div>
        <div class="l-titulo">{esc(titulo)}</div>
        <div class="l-sub">{esc(subtitulo)}</div>
      </div>
    </div>

{bloco_rodape(numero, total)}"""
    return montar_pagina(f"Slide {numero:02d} — {titulo}", corpo, tokens, largura, altura, css)


def slide_video(
    video_uri: str,
    poster_uri: str,
    tokens: TokensDesign,
    numero: int,
    total: int,
    largura: int,
    altura: int,
) -> str:
    """
    Slide de vídeo.

    O elemento ``<video>`` toca no navegador (autoplay silencioso em loop).
    Como o Chromium headless do Playwright pode não decodificar H.264, o
    ``poster`` fica visível por baixo — assim o slide continua rendendo um PNG
    apresentável mesmo quando vira imagem estática.
    """
    css = """
    .moldura-video {
        flex: 1; position: relative; overflow: hidden;
        margin: 6px 44px 8px; border-radius: 24px;
        border: 1px solid var(--borda);
        box-shadow: 0 18px 48px rgba(0, 0, 0, .46);
        background: #000;
    }
    .moldura-video img.poster,
    .moldura-video video {
        position: absolute; inset: 0;
        width: 100%; height: 100%; object-fit: cover;
    }
    .moldura-video video { z-index: 2; }
    .veu {
        position: absolute; inset: 0; z-index: 3;
        background: linear-gradient(180deg,
            rgba(7, 31, 29, .40) 0%,
            rgba(7, 31, 29, .06) 32%,
            rgba(7, 31, 29, .78) 76%,
            rgba(7, 31, 29, .96) 100%);
        pointer-events: none;
    }
    .botao-play {
        position: absolute; z-index: 4; top: 50%; left: 50%;
        transform: translate(-50%, -50%);
        width: 132px; height: 132px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        background: rgba(224, 161, 46, .92);
        box-shadow: 0 0 0 16px rgba(224, 161, 46, .18),
                    0 18px 40px rgba(0, 0, 0, .45);
        color: #23180A; font-size: 52px; padding-left: 10px;
    }
    .legenda-video {
        position: absolute; z-index: 4; left: 34px; right: 34px; bottom: 32px;
    }
    .legenda-video .traco {
        width: 76px; height: 5px; border-radius: 3px; margin-bottom: 16px;
        background: linear-gradient(90deg, var(--dourado), var(--menta));
    }
    .legenda-video .v-titulo {
        font-size: 40px; font-weight: 800; line-height: 1.14; letter-spacing: -.8px;
        text-shadow: 0 2px 12px rgba(0, 0, 0, .55); margin-bottom: 10px;
    }
    .legenda-video .v-sub {
        font-size: 20px; line-height: 1.46; color: rgba(244, 248, 247, .88);
        text-shadow: 0 1px 8px rgba(0, 0, 0, .5);
    }
    """

    corpo = f"""{bloco_cabecalho(tokens, "Vídeo")}

    <div class="moldura-video">
      <img class="poster" src="{poster_uri}" alt="">
      <video src="{video_uri}" poster="{poster_uri}"
             autoplay muted loop playsinline preload="auto"></video>
      <div class="veu"></div>
      <div class="botao-play">▶</div>
      <div class="legenda-video">
        <div class="traco"></div>
        <div class="v-titulo">Assista à premiação</div>
        <div class="v-sub">
          Momento do anúncio do {esc(CONTEUDO.colocacao)} na cerimônia
          do {esc(CONTEUDO.evento)}.
        </div>
      </div>
    </div>

{bloco_rodape(numero, total)}"""
    return montar_pagina(f"Slide {numero:02d} — Vídeo", corpo, tokens, largura, altura, css)


def slide_encerramento(
    tokens: TokensDesign, numero: int, total: int, largura: int, altura: int
) -> str:
    """Slide final — agradecimento, coordenação do projeto e créditos."""
    equipe = "".join(
        f"""
          <div class="pessoa">
            <span class="ponto"></span>
            <div>
              <div class="p-nome">{esc(nome)}</div>
              <div class="p-papel">{esc(papel)}</div>
            </div>
          </div>"""
        for nome, papel in CONTEUDO.equipe
    )
    creditos = "".join(
        f'<li>{esc(item)}</li>' for item in CONTEUDO.agradecimentos
    )

    css = """
    .conteudo-final {
        flex: 1; display: flex; flex-direction: column;
        align-items: center; justify-content: center; text-align: center;
        gap: 28px; padding: 6px 58px 6px;
    }
    .obrigado {
        font-size: 96px; letter-spacing: -3px; line-height: 1;
        color: var(--dourado-claro);
    }
    .mensagem {
        font-size: 22px; line-height: 1.5; color: rgba(244, 248, 247, .86);
        max-width: 800px;
    }
    .painel {
        width: 100%; padding: 26px 32px; text-align: left;
    }
    .painel-rotulo {
        font-size: 14px; font-weight: 700; letter-spacing: 3.2px;
        text-transform: uppercase; color: var(--dourado-claro); margin-bottom: 16px;
    }
    .pessoa { display: flex; align-items: center; gap: 14px; margin-bottom: 14px; }
    .pessoa:last-child { margin-bottom: 0; }
    .pessoa .ponto {
        width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0;
        background: var(--dourado);
    }
    .pessoa .p-nome { font-size: 21px; font-weight: 700; }
    .pessoa .p-papel { font-size: 15px; color: var(--cinza); }
    .painel ul { list-style: none; display: flex; flex-direction: column; gap: 11px; }
    .painel ul li {
        font-size: 17px; line-height: 1.4; color: rgba(244, 248, 247, .82);
        padding-left: 22px; position: relative;
    }
    .painel ul li::before {
        content: "▸"; position: absolute; left: 0; color: var(--menta);
    }
    .assinatura-final {
        font-size: 17px; font-weight: 600; letter-spacing: 1.4px;
        text-transform: uppercase; color: var(--menta);
    }
    """

    corpo = f"""{bloco_cabecalho(tokens, "Obrigado")}

    <div class="conteudo-final">
      <h2 class="titulo-display obrigado">Parabéns!</h2>

      <p class="mensagem">{esc(CONTEUDO.mensagem_final)}</p>

      <div class="cartao painel">
        <div class="painel-rotulo">Coordenação do projeto</div>
        {equipe}
      </div>

      <div class="cartao painel">
        <div class="painel-rotulo">Agradecimentos</div>
        <ul>{creditos}</ul>
      </div>

      <div class="assinatura-final">
        {esc(CONTEUDO.unidade)} · {esc(CONTEUDO.instituicao)}
      </div>
    </div>

{bloco_rodape(numero, total)}"""
    return montar_pagina("Slide final — Encerramento", corpo, tokens, largura, altura, css)


# ═══════════════════════════════════════════════════════════════════════════
# 7. ORQUESTRAÇÃO
# ═══════════════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class Slide:
    """Um slide pronto para gravação."""

    nome_arquivo: str
    html: str


def gerar_slides(
    tokens: TokensDesign,
    imagens: Sequence[Midia],
    videos: Sequence[Midia],
    largura: int,
    altura: int,
    incluir_video: bool,
    saida: Path,
    capa_com_foto: bool = False,
) -> list[Slide]:
    """
    Monta a sequência completa do carrossel.

    Ordem: capa → o projeto → uma página por foto → vídeo (se houver) →
    encerramento. O total de slides é calculado antes para que a paginação
    ``NN / TT`` do rodapé fique correta.
    """
    video = videos[0] if (incluir_video and videos) else None
    total = 2 + len(imagens) + (1 if video else 0) + 1

    slides: list[Slide] = []
    numero = 1

    # ── Capa ────────────────────────────────────────────────────────────
    # Por padrão a capa é limpa (só o gradiente institucional); a foto de
    # fundo é opcional porque compete visualmente com o banner e o título.
    foto_capa = para_data_uri(escolher_foto_capa(imagens).caminho) if capa_com_foto else None
    slides.append(
        Slide(
            "slide_01_capa.html",
            slide_capa(tokens, numero, total, largura, altura, foto_capa),
        )
    )
    numero += 1

    # ── O projeto ───────────────────────────────────────────────────────
    slides.append(
        Slide(
            f"slide_{numero:02d}_projeto.html",
            slide_projeto(tokens, numero, total, largura, altura),
        )
    )
    numero += 1

    # ── Uma página HTML por foto ────────────────────────────────────────
    for imagem in imagens:
        try:
            uri = para_data_uri(imagem.caminho)
        except OSError as erro:
            print(f"  ⚠️  Foto ignorada ({imagem.caminho.name}): {erro}")
            total -= 1
            continue

        titulo, subtitulo = legenda_de(imagem)
        nome = _slug(imagem.caminho.stem)
        slides.append(
            Slide(
                f"slide_{numero:02d}_foto_{nome}.html",
                slide_foto(
                    uri, titulo, subtitulo, tokens, numero, total,
                    largura, altura, ajuste_de(imagem),
                ),
            )
        )
        numero += 1

    # ── Vídeo ───────────────────────────────────────────────────────────
    if video is not None:
        slides.append(
            Slide(
                f"slide_{numero:02d}_video.html",
                _montar_slide_video(video, imagens, tokens, numero, total, largura, altura, saida),
            )
        )
        numero += 1

    # ── Encerramento ────────────────────────────────────────────────────
    slides.append(
        Slide(
            f"slide_{numero:02d}_encerramento.html",
            slide_encerramento(tokens, numero, total, largura, altura),
        )
    )

    return slides


def _montar_slide_video(
    video: Midia,
    imagens: Sequence[Midia],
    tokens: TokensDesign,
    numero: int,
    total: int,
    largura: int,
    altura: int,
    saida: Path,
) -> str:
    """Prepara o poster (frame do vídeo ou foto de reserva) e renderiza o slide."""
    poster_uri: str
    frame = extrair_frame(video.caminho, saida / ".cache" / f"{video.caminho.stem}_poster.jpg")
    if frame is not None:
        poster_uri = para_data_uri(frame)
        print("  🎞️  Poster extraído do vídeo via ffmpeg.")
    else:
        reserva = escolher_foto_capa(imagens)
        poster_uri = para_data_uri(reserva.caminho)
        print(
            f"  ℹ️  ffmpeg indisponível — usando '{reserva.caminho.name}' "
            "como poster do vídeo."
        )

    return slide_video(
        para_data_uri(video.caminho), poster_uri, tokens, numero, total, largura, altura
    )


def _slug(texto: str) -> str:
    """Normaliza um nome de arquivo para uso seguro no nome do slide."""
    limpo = re.sub(r"[^a-zA-Z0-9]+", "_", texto).strip("_").lower()
    return limpo or "foto"


def salvar_slides(slides: Iterable[Slide], saida: Path) -> int:
    """Grava os HTMLs na pasta de saída e devolve quantos foram escritos."""
    saida.mkdir(parents=True, exist_ok=True)
    gravados = 0
    for slide in slides:
        destino = saida / slide.nome_arquivo
        try:
            destino.write_text(slide.html, encoding="utf-8")
        except OSError as erro:
            print(f"  ❌ Falha ao gravar {slide.nome_arquivo}: {erro}")
            continue
        tamanho = destino.stat().st_size / 1024
        print(f"  ✅ {slide.nome_arquivo}  ({tamanho:,.0f} KB)")
        gravados += 1
    return gravados


# ═══════════════════════════════════════════════════════════════════════════
# 8. CLI
# ═══════════════════════════════════════════════════════════════════════════

CONTEUDO = Conteudo()
PASTA_SCRIPT = Path(__file__).resolve().parent


def analisar_argumentos(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Define e interpreta os argumentos de linha de comando."""
    parser = argparse.ArgumentParser(
        description="Gera os HTMLs do carrossel do Prêmio de Inovação UFPA 2026.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--design-system",
        type=Path,
        default=PASTA_SCRIPT / "Design System",
        help="Pasta com estilos, tokens, templates e logotipos do evento.",
    )
    parser.add_argument(
        "--midia",
        "--fotos",
        dest="midia",
        type=Path,
        default=PASTA_SCRIPT / "Midia",
        help="Pasta com as fotos (e o vídeo) da premiação.",
    )
    parser.add_argument(
        "--saida",
        type=Path,
        default=PASTA_SCRIPT / "html",
        help="Pasta onde os arquivos HTML serão gravados.",
    )
    parser.add_argument(
        "--max-fotos",
        type=int,
        default=3,
        help="Quantidade máxima de fotos representativas no carrossel (0 = todas).",
    )
    parser.add_argument("--largura", type=int, default=LARGURA_PADRAO, help="Largura do slide.")
    parser.add_argument("--altura", type=int, default=ALTURA_PADRAO, help="Altura do slide.")
    parser.add_argument(
        "--sem-video",
        action="store_true",
        help="Não gera o slide de vídeo mesmo que exista um arquivo de vídeo.",
    )
    parser.add_argument(
        "--capa-com-foto",
        action="store_true",
        help="Usa uma foto esmaecida como fundo da capa (padrão: capa limpa).",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Ponto de entrada. Devolve 0 em sucesso e 1 em erro tratado."""
    args = analisar_argumentos(argv)

    print("=" * 68)
    print("  🏆  Carrossel — Prêmio de Inovação em Processos Organizacionais")
    print(f"      UFPA 2026 · {CONTEUDO.projeto_curto} · {CONTEUDO.colocacao}")
    print("=" * 68)

    # ── Design System ───────────────────────────────────────────────────
    print(f"\n🎨 Lendo Design System: {args.design_system}")
    try:
        tokens = carregar_design_system(args.design_system)
    except NotADirectoryError as erro:
        print(f"❌ {erro}")
        return 1
    print(
        f"  • paleta: {tokens.verde_escuro} → {tokens.verde_medio} · "
        f"destaque {tokens.dourado}"
    )
    print(f"  • logotipos embutidos: {', '.join(tokens.logos) or 'nenhum'}")
    print(f"  • fontes embutidas: {'sim' if tokens.fontes_css else 'não'}")
    if tokens.template_base:
        print(f"  • usando {NOME_TEMPLATE_BASE} do Design System")

    # ── Mídia ───────────────────────────────────────────────────────────
    print(f"\n📸 Lendo mídia: {args.midia}")
    try:
        imagens, videos = descobrir_midias(args.midia)
    except (NotADirectoryError, FileNotFoundError) as erro:
        print(f"❌ {erro}")
        return 1

    if args.max_fotos > 0:
        descartadas = imagens[args.max_fotos:]
        imagens = imagens[: args.max_fotos]
        for extra in descartadas:
            print(f"  ⏭️  Fora do limite de --max-fotos: {extra.caminho.name}")

    print(f"  • {len(imagens)} foto(s) selecionada(s), {len(videos)} vídeo(s)")
    for imagem in imagens:
        print(f"      – {imagem.caminho.name}")

    # ── Geração ─────────────────────────────────────────────────────────
    print("\n📝 Gerando slides...")
    slides = gerar_slides(
        tokens=tokens,
        imagens=imagens,
        videos=videos,
        largura=args.largura,
        altura=args.altura,
        incluir_video=not args.sem_video,
        saida=args.saida,
        capa_com_foto=args.capa_com_foto,
    )
    gravados = salvar_slides(slides, args.saida)

    if gravados == 0:
        print("\n❌ Nenhum slide foi gravado.")
        return 1

    print(f"\n✨ {gravados} slide(s) em: {args.saida}")
    print("\n💡 Para converter em imagens, na raiz do projeto:")
    try:
        relativo = args.saida.resolve().relative_to(Path.cwd())
    except ValueError:
        relativo = args.saida
    print(f"   for f in {relativo}/*.html; do \\")
    print('     python gerar_posts.py --plataforma instagram --arquivo "$f"; done')
    return 0


if __name__ == "__main__":
    sys.exit(main())
