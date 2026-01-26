#!/usr/bin/env python3
"""Gerador de HTML para Calendário de Treinos (RAJJ).

Cria um layout no estilo "grade" com:
- Moldura (frame) nas cores da marca (extraídas da Logo)
- Logo no cabeçalho
- Relógio segmentado em 3 partes (Aquecimento, Teoria, Luta) com 20 min cada
- Grade semanal dos treinos conforme horários informados

Saída: ScriptCalendarioRAJJ/html/calendario_treinos_rajj.html
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from PIL import Image


@dataclass(frozen=True)
class BrandColors:
		blue: str
		gold: str
		black: str = "#111111"
		white: str = "#FFFFFF"
		gray_100: str = "#F3F3F3"
		gray_200: str = "#E3E3E3"
		gray_300: str = "#D0D0D0"


def obter_cores_marca() -> BrandColors:
		"""Cores extraídas da Logo (paleta dominante).

		Observação importante:
		- A logo fornecida é predominantemente azul e dourado.
		- O frame e títulos usam as cores da marca.
		- O relógio segmentado pode usar cores específicas conforme solicitado.
		"""

		# Dominantes observadas em Logo.JPG/Logo.pdf renderizado.
		return BrandColors(
				blue="#0000F0",
				gold="#F0B000",
		)


def gerar_svg_relogio_segmentado(colors: BrandColors) -> str:
		"""Relógio circular com 3 segmentos iguais (20 min cada).

		Implementação via SVG com 3 arcos de 120°.
		"""

		# Cores solicitadas para os 3 segmentos
		# (o restante do layout continua usando as cores da marca no frame e títulos).
		warmup = "#F6B3B3"   # vermelho claro
		theory = "#A9D7FF"   # azul claro
		fight = "#7EDFA1"    # verde

		# Arcos (círculo central em (60,60), raio 46; stroke largo vira donut)
		# Segmentos: 0–120, 120–240, 240–360.
		# Para simplificar e manter consistência, usamos stroke-dasharray em 3 círculos
		# e rotacionamos cada um.
		r = 46
		c = 2 * 3.141592653589793 * r
		seg = c / 3

		return f"""
<div class="clock">
	<div class="clock-title">Metodologia</div>
	<svg class="clock-svg" viewBox="0 0 120 120" role="img" aria-label="Relógio segmentado: aquecimento, teoria e luta">
		<circle class="clock-bg" cx="60" cy="60" r="{r}" />
		<g transform="rotate(-90 60 60)">
			<circle class="clock-seg" cx="60" cy="60" r="{r}" style="stroke: {warmup}; stroke-dasharray: {seg:.2f} {c:.2f}; stroke-dashoffset: 0;" />
			<circle class="clock-seg" cx="60" cy="60" r="{r}" style="stroke: {theory}; stroke-dasharray: {seg:.2f} {c:.2f}; stroke-dashoffset: {-seg:.2f};" />
			<circle class="clock-seg" cx="60" cy="60" r="{r}" style="stroke: {fight}; stroke-dasharray: {seg:.2f} {c:.2f}; stroke-dashoffset: {-2*seg:.2f};" />
		</g>
		<circle class="clock-hole" cx="60" cy="60" r="30" />
		<text x="60" y="64" text-anchor="middle" class="clock-center">60min</text>
	</svg>
	<div class="clock-legend">
		<div class="legend-row"><span class="dot" style="background: {warmup}"></span><span>Aquecimento • 20min</span></div>
		<div class="legend-row"><span class="dot" style="background: {theory}"></span><span>Teoria • 20min</span></div>
		<div class="legend-row"><span class="dot" style="background: {fight}"></span><span>Luta • 20min</span></div>
	</div>
</div>
""".strip()


def gerar_grade_treinos() -> dict:
		"""Define a grade de treinos conforme solicitado."""

		# Seg–Sex
		semana = {
				"Seg": [
						("08:00–10:00", "Mista"),
						("15:00–17:00", "Mista"),
						("17:00–18:00", "Kids 1"),
						("18:00–19:00", "Kids 2"),
						("19:00–20:00", "Juvenil"),
						("20:00–21:00", "Adulto"),
				],
				"Ter": [
						("08:00–10:00", "Mista"),
						("15:00–17:00", "Mista"),
						("17:00–18:00", "Kids 1"),
						("18:00–19:00", "Kids 2"),
						("19:00–20:00", "Juvenil"),
						("20:00–21:00", "Adulto"),
				],
				"Qua": [
						("08:00–10:00", "Mista"),
						("15:00–17:00", "Mista"),
						("17:00–18:00", "Kids 1"),
						("18:00–19:00", "Kids 2"),
						("19:00–20:00", "Juvenil"),
						("20:00–21:00", "Adulto"),
				],
				"Qui": [
						("08:00–10:00", "Mista"),
						("15:00–17:00", "Mista"),
						("17:00–18:00", "Kids 1"),
						("18:00–19:00", "Kids 2"),
						("19:00–20:00", "Juvenil"),
						("20:00–21:00", "Adulto"),
				],
				"Sex": [
						("08:00–10:00", "Mista"),
						("15:00–17:00", "Mista"),
						("17:00–18:00", "Kids 1"),
						("18:00–19:00", "Kids 2"),
						("19:00–20:00", "Juvenil"),
						("20:00–21:00", "Adulto"),
				],
		}

		sabado = [("18:00–20:00", "Adulto")]

		return {"semana": semana, "sabado": sabado}


def gerar_html(colors: BrandColors) -> str:
		logo_rel = "../Logo_transparente.png"  # arquivo está em ScriptCalendarioRAJJ/

		relogio_html = gerar_svg_relogio_segmentado(colors)
		grade = gerar_grade_treinos()

		# Cores por categoria (apenas marca + neutros)
		# Adulto: azul sólido (forte)
		# Mista: azul da marca em tom claro (mesma cor, só com transparência)
		cat_styles = {
				"Mista": {"bg": "rgba(0, 0, 240, 0.20)", "fg": colors.black},
				"Adulto": {"bg": colors.blue, "fg": colors.white},
				"Kids 1": {"bg": colors.gold, "fg": colors.black},
				"Kids 2": {"bg": colors.gold, "fg": colors.black},
				"Juvenil": {"bg": colors.gray_300, "fg": colors.black},
		}

		# Grade Seg–Sex em colunas
		dias_ordem = ["Seg", "Ter", "Qua", "Qui", "Sex"]
		cards_semana = ""
		for dia in dias_ordem:
				linhas = ""
				for horario, categoria in grade["semana"][dia]:
						st = cat_styles[categoria]
						linhas += f"""
							<div class=\"slot\" style=\"background:{st['bg']}; color:{st['fg']}\">
								<div class=\"slot-time\">{horario}</div>
								<div class=\"slot-cat\">{categoria}</div>
							</div>
						"""

				cards_semana += f"""
					<div class="day-card">
						<div class="day-title">{dia}</div>
						<div class="day-slots">
							{linhas}
						</div>
					</div>
				"""

		# Sábado (card separado)
		sab_linhas = ""
		for horario, categoria in grade["sabado"]:
				st = cat_styles[categoria]
				sab_linhas += f"""
					<div class=\"slot\" style=\"background:{st['bg']}; color:{st['fg']}\">
						<div class=\"slot-time\">{horario}</div>
						<div class=\"slot-cat\">{categoria}</div>
					</div>
				"""

		return f"""<!DOCTYPE html>
<html lang="pt-br">
<head>
	<meta charset="UTF-8" />
	<meta name="viewport" content="width=device-width, initial-scale=1.0" />
	<title>Grade de Treinos</title>
	<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@500;600;700;800&family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
	<style>
		:root {{
			--brand-blue: {colors.blue};
			--brand-gold: {colors.gold};
			--ink: {colors.black};
			--paper: {colors.white};
			--g100: {colors.gray_100};
			--g200: {colors.gray_200};
			--g300: {colors.gray_300};
		}}

		* {{ box-sizing: border-box; margin: 0; padding: 0; }}

		body {{
			background: #222;
			min-height: 100vh;
			display: flex;
			align-items: center;
			justify-content: center;
			font-family: 'Roboto', sans-serif;
		}}

		/* Canvas no formato post (Instagram portrait) */
		.flyer {{
			width: 1080px;
			height: 1350px;
			background: var(--paper);
			position: relative;
			overflow: hidden;
		}}

		/* FRAME nas cores da marca */
		.frame {{
			position: absolute;
			inset: 26px;
			border: 10px solid var(--brand-blue);
			border-radius: 28px;
			pointer-events: none;
		}}
		.frame::before {{
			content: "";
			position: absolute;
			inset: 10px;
			border: 6px solid var(--brand-gold);
			border-radius: 20px;
		}}

		.content {{
			position: relative;
			padding: 60px 70px 60px 70px;
			height: 100%;
			display: flex;
			flex-direction: column;
			gap: 26px;
			background:
				linear-gradient(180deg, rgba(0,0,0,0.02) 0%, rgba(0,0,0,0) 18%),
				radial-gradient(900px 500px at 10% 15%, rgba(240,176,0,0.12) 0%, transparent 55%),
				radial-gradient(900px 500px at 95% 10%, rgba(0,0,240,0.10) 0%, transparent 55%);
		}}

		header {{
			display: grid;
			grid-template-columns: 1fr auto;
			align-items: start;
			gap: 18px;
		}}

		.brand {{
			display: flex;
			align-items: center;
			gap: 18px;
		}}

		.brand img {{
			width: 110px;
			height: 110px;
			object-fit: contain;
		}}

		.title {{
			display: flex;
			flex-direction: column;
			gap: 6px;
		}}

		.title h1 {{
			font-family: 'Montserrat', sans-serif;
			font-weight: 800;
			letter-spacing: 0.5px;
			font-size: 44px;
			color: var(--brand-blue);
			text-transform: uppercase;
			line-height: 1.05;
		}}

		.title .sub {{
			font-family: 'Montserrat', sans-serif;
			font-weight: 600;
			font-size: 18px;
			color: var(--ink);
			opacity: 0.85;
		}}

		/* Relógio no topo-direito */
		.clock {{
			width: 250px;
			background: rgba(255,255,255,0.92);
			border: 2px solid var(--g200);
			border-radius: 18px;
			padding: 14px 14px 12px 14px;
		}}
		.clock-title {{
			font-family: 'Montserrat', sans-serif;
			font-weight: 800;
			font-size: 14px;
			color: var(--ink);
			text-transform: uppercase;
			letter-spacing: 1px;
			margin-bottom: 10px;
		}}
		.clock-svg {{ width: 100%; height: auto; display: block; }}
		.clock-bg {{ fill: none; stroke: var(--g200); stroke-width: 16; }}
		.clock-seg {{
			fill: none;
			stroke-width: 16;
			stroke-linecap: butt;
		}}
		.clock-hole {{ fill: var(--paper); }}
		.clock-center {{
			font-family: 'Montserrat', sans-serif;
			font-weight: 800;
			font-size: 14px;
			fill: var(--ink);
		}}
		.clock-legend {{
			margin-top: 10px;
			display: grid;
			gap: 6px;
			font-size: 12px;
			color: var(--ink);
		}}
		.legend-row {{ display: flex; align-items: center; gap: 8px; }}
		.dot {{ width: 10px; height: 10px; border-radius: 50%; display: inline-block; }}

		/* Bloco principal */
		.board {{
			background: rgba(255,255,255,0.92);
			border: 2px solid var(--g200);
			border-radius: 22px;
			padding: 22px;
			display: flex;
			flex-direction: column;
			gap: 16px;
			flex: 1;
		}}

		.board-head {{
			display: flex;
			align-items: baseline;
			justify-content: space-between;
			gap: 12px;
		}}

		.board-head h2 {{
			font-family: 'Montserrat', sans-serif;
			font-weight: 800;
			font-size: 22px;
			color: var(--ink);
			text-transform: uppercase;
			letter-spacing: 1px;
		}}

		.legend {{
			display: flex;
			gap: 10px;
			align-items: center;
			font-size: 12px;
			color: var(--ink);
		}}
		.pill {{
			display: inline-flex;
			align-items: center;
			gap: 7px;
			padding: 7px 10px;
			border-radius: 999px;
			border: 1px solid var(--g200);
			background: var(--paper);
			font-weight: 600;
		}}
		.sw {{ width: 10px; height: 10px; border-radius: 3px; display: inline-block; }}
		.sw-mista {{ background: rgba(0, 0, 240, 0.20); border: 1px solid var(--brand-blue); }}
		.sw-adulto {{ background: var(--brand-blue); }}
		.sw-kids {{ background: var(--brand-gold); }}
		.sw-juvenil {{ background: var(--g300); }}

		.week-grid {{
			display: grid;
			grid-template-columns: repeat(5, 1fr);
			gap: 14px;
			flex: 1;
		}}

		.day-card {{
			border: 1px solid var(--g200);
			border-radius: 16px;
			overflow: hidden;
			background: var(--paper);
			display: flex;
			flex-direction: column;
			min-height: 0;
		}}
		.day-title {{
			background: linear-gradient(90deg, var(--brand-blue), var(--brand-gold));
			color: var(--paper);
			font-family: 'Montserrat', sans-serif;
			font-weight: 800;
			letter-spacing: 1px;
			text-transform: uppercase;
			padding: 10px 12px;
			font-size: 14px;
		}}
		.day-slots {{
			padding: 10px;
			display: grid;
			gap: 10px;
			overflow: hidden;
		}}
		.slot {{
			border-radius: 12px;
			padding: 10px 10px;
			display: grid;
			gap: 4px;
		}}
		.slot-time {{ font-weight: 800; font-size: 13px; letter-spacing: 0.2px; }}
		.slot-cat {{ font-weight: 700; font-size: 12px; opacity: 0.95; text-transform: uppercase; letter-spacing: 0.6px; }}

		.sat {{
			margin-top: 14px;
			border: 1px solid var(--g200);
			border-radius: 16px;
			overflow: hidden;
			background: var(--paper);
		}}
		.sat-head {{
			background: var(--brand-gold);
			color: var(--ink);
			font-family: 'Montserrat', sans-serif;
			font-weight: 800;
			letter-spacing: 1px;
			text-transform: uppercase;
			padding: 10px 12px;
			font-size: 14px;
		}}
		.sat-body {{ padding: 12px; display: grid; gap: 10px; }}

		footer {{
			display: flex;
			justify-content: space-between;
			align-items: center;
			gap: 14px;
			font-size: 12px;
			color: var(--ink);
			opacity: 0.85;
		}}
		.tag {{
			border: 1px solid var(--g200);
			border-radius: 999px;
			padding: 8px 12px;
			background: rgba(255,255,255,0.9);
			font-weight: 600;
		}}
	</style>
</head>
<body>
	<div class="flyer">
		<div class="frame"></div>
		<div class="content">
			<header>
				<div class="brand">
					<img src="{logo_rel}" alt="Logo" />
					<div class="title">
						<h1>Cronograma de Aulas</h1>
						<div class="sub">Segunda a Sábado • RAJJ</div>
					</div>
				</div>

				{relogio_html}
			</header>

			<section class="board">
				<div class="board-head">
					<h2>Grade Semanal</h2>
					<div class="legend">
						<span class="pill"><span class="sw sw-mista"></span>Mista</span>
						<span class="pill"><span class="sw sw-adulto"></span>Adulto</span>
						<span class="pill"><span class="sw sw-kids"></span>Kids</span>
						<span class="pill"><span class="sw sw-juvenil"></span>Juvenil</span>
					</div>
				</div>

				<div class="week-grid">
					{cards_semana}
				</div>

				<div class="sat">
					<div class="sat-head">Sábado</div>
					<div class="sat-body">
						{sab_linhas}
					</div>
				</div>
			</section>

			<footer>
				<div class="tag">Documento Oficial: Versão 1.0</div>
			</footer>
		</div>
	</div>
</body>
</html>
"""


def gerar_logo_transparente(base_dir: Path) -> None:
		"""Gera uma logo PNG com transparência removendo o branco do fundo.

		Estratégia:
		- Considera como fundo os pixels "quase brancos".
		- Remove apenas o fundo conectado às bordas (flood fill), preservando brancos internos.
		"""

		src = base_dir / "Logo.JPG"
		dst = base_dir / "Logo_transparente.png"

		if not src.exists():
			return

		if dst.exists() and dst.stat().st_mtime >= src.stat().st_mtime:
			return

		img = Image.open(src).convert("RGB")
		w, h = img.size
		px = img.load()

		# Define fundo como "quase branco" (ajuste fino para JPG com compressão)
		def is_bg(x: int, y: int) -> bool:
			r, g, b = px[x, y]
			return r >= 245 and g >= 245 and b >= 245

		visited = [[False] * w for _ in range(h)]
		stack = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]

		# Flood fill no fundo conectado às bordas
		while stack:
			x, y = stack.pop()
			if x < 0 or y < 0 or x >= w or y >= h:
				continue
			if visited[y][x]:
				continue
			if not is_bg(x, y):
				continue
			visited[y][x] = True
			stack.append((x + 1, y))
			stack.append((x - 1, y))
			stack.append((x, y + 1))
			stack.append((x, y - 1))

		rgba = img.convert("RGBA")
		out_px = rgba.load()
		for y in range(h):
			row = visited[y]
			for x in range(w):
				if row[x]:
					r, g, b, _a = out_px[x, y]
					out_px[x, y] = (r, g, b, 0)

		rgba.save(dst)


def main() -> None:
		base_dir = Path(__file__).resolve().parent
		out_dir = base_dir / "html"
		out_dir.mkdir(parents=True, exist_ok=True)

		gerar_logo_transparente(base_dir)

		colors = obter_cores_marca()
		html = gerar_html(colors)

		out_file = out_dir / "calendario_treinos_rajj.html"
		out_file.write_text(html, encoding="utf-8")
		print(f"✅ Gerado: {out_file}")


if __name__ == "__main__":
		main()
