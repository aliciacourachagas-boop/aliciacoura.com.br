#!/usr/bin/env python3
"""Publica a composição aprovada sem redesenhar o logo: usa os vetores do site."""
import re, json, base64, io
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import cairosvg

root=Path(__file__).resolve().parents[1]
src=''.join(p.read_text(encoding='utf-8') for p in sorted((root/'site-parts').glob('part-*.txt')))
data=json.loads(re.search(r'const AC_PAGES=(\{.*?\});',src,re.S).group(1))
html=base64.b64decode(data['index']).decode('utf-8')

W,H=1200,630
scale=3
base=Image.new('RGB',(W*scale,H*scale),'#FAF8F4')
d=ImageDraw.Draw(base)
S=lambda x:int(x*scale)
lime='#D2FF00'; olive='#405916'; darkolive='#324806'

# O enquadramento da arte APROVADA. Sem degradês e sem alterar a marca.
d.ellipse((S(-305),S(-335),S(360),S(330)),fill=lime)
d.ellipse((S(960),S(440),S(1710),S(1190)),fill=darkolive)
for r in (132,196,260):
    d.arc((S(1245-r),S(-65-r),S(1245+r),S(-65+r)),0,200,fill=olive,width=S(1.6))
d.arc((S(220-315),S(850-315),S(220+315),S(850+315)),170,350,fill=olive,width=S(2))

def exact_svg(classname,color,width):
    m=re.search(r'<svg\b[^>]*class="'+re.escape(classname)+r'"[^>]*>.*?</svg>',html,re.S)
    assert m,classname
    svg=m.group(0).replace('viewbox=','viewBox=').replace('fill="currentColor"',f'fill="{color}"')
    svg=svg.replace('<svg ','<svg xmlns="http://www.w3.org/2000/svg" ',1)
    png=cairosvg.svg2png(bytestring=svg.encode('utf-8'),output_width=S(width))
    return Image.open(io.BytesIO(png)).convert('RGBA')

logo=exact_svg('logo-symbol-svg',olive,378)
name=exact_svg('logo-name-svg','#171915',609)
base.paste(logo,(S(78),S(225)),logo)
base.paste(name,(S(506),S(240)),name)
font=ImageFont.truetype('/usr/share/fonts/truetype/lato/Lato-Regular.ttf',S(24))
d.text((S(507),S(359)),'JORNALISMO  ·  CULTURA  ·  CONTEÚDO',font=font,fill='#171915')
base=base.resize((W,H),Image.Resampling.LANCZOS)
out=root/'assets'/'alicia-coura-og.jpg'
out.parent.mkdir(parents=True,exist_ok=True)
base.save(out,quality=95,subsampling=0,optimize=True)
print('Capa aprovada aplicada:',out,out.stat().st_size,'bytes')
