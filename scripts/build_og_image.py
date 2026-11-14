#!/usr/bin/env python3
"""Reproduz a marca SVG original do cabecalho na imagem Open Graph."""
import base64
import io
import json
from pathlib import Path
import re
from PIL import Image, ImageDraw, ImageFont
import cairosvg

root = Path(__file__).resolve().parents[1]
source = ''.join(p.read_text(encoding='utf-8') for p in sorted((root / 'site-parts').glob('part-*.txt')))
match = re.search(r'const AC_PAGES=(\{.*?\});', source, re.S)
assert match, 'AC_PAGES ausente'
index = base64.b64decode(json.loads(match.group(1))['index']).decode('utf-8')

def get_svg(css_class, color, width):
    m = re.search(r'<svg\b[^>]*class="' + css_class + r'"[^>]*>.*?</svg>', index, re.S)
    assert m, f'Logotipo ausente: {css_class}'
    svg = m.group(0)
    svg = svg.replace('viewbox=', 'viewBox=')
    svg = svg.replace('fill="currentColor"', f'fill="{color}"')
    svg = svg.replace('<svg ', '<svg xmlns="http://www.w3.org/2000/svg" ', 1)
    return Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode('utf-8'), output_width=width))).convert('RGBA')

card = Image.new('RGB', (1200, 630), '#fafaf8')
for cls, color, width, x, y in [
    ('logo-symbol-svg', '#465A1B', 238, 92, 232),
    ('logo-name-svg', '#171915', 746, 348, 234),
]:
    logo = get_svg(cls, color, width)
    card.paste(logo, (x, y), logo)

d = ImageDraw.Draw(card)
d.line(((93,492),(1102,492)), fill='#dfded9', width=2)
font_path = Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
font = ImageFont.truetype(str(font_path), 23) if font_path.exists() else ImageFont.load_default()
d.text((93,522), 'JORNALISMO   ·   CULTURA   ·   CONTEÚDO', fill='#171915', font=font)
out = root / 'assets' / 'alicia-coura-og.jpg'
out.parent.mkdir(parents=True, exist_ok=True)
card.save(out, quality=92, optimize=True, subsampling=0)
print('Imagem Open Graph com logo original:', out, out.stat().st_size, 'bytes')
