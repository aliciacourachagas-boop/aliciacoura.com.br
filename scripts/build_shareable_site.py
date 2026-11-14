#!/usr/bin/env python3
"""Gera paginas estaticas compartilháveis de Alicia Coura a partir de site-parts."""
import base64
import html
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
DOMAIN="https://aliciacoura.com.br"
PAGES=["index","projetos","publicacoes","videos","musica","sobre","bio-extratus","batekoo","documentario-dj"]
META={
"index":("Alícia Coura | Jornalismo, Cultura e Conteúdo","Portfólio de Alícia Coura, jornalista, repórter e estrategista de conteúdo. Projetos de comunicação, reportagens, vídeos e pesquisa musical."),
"projetos":("Projetos | Alícia Coura","Conheça projetos de Alícia Coura em conteúdo, jornalismo e comunicação, incluindo trabalhos para Bio Extratus, BATEKOO e documentário autoral."),
"publicacoes":("Publicações | Alícia Coura","Reportagens e entrevistas publicadas por Alícia Coura no g1, Arquivo Nacional do Rap e Revista Curió."),
"videos":("Vídeos | Alícia Coura","Seleção de vídeos e produções de conteúdo audiovisual de Alícia Coura."),
"musica":("Lado B | Alícia Coura","Pesquisa musical, discotecagem, repertório e a relação da música com o jornalismo e a criação de conteúdo de Alícia Coura."),
"sobre":("Sobre | Alícia Coura","Conheça Alícia Coura, jornalista, repórter e estrategista de conteúdo. Trajetória profissional, interesses e atuação em comunicação e cultura."),
"bio-extratus":("Bio Extratus | Projeto de Alícia Coura","Projeto de conteúdo e redes sociais de Alícia Coura para a Bio Extratus. Conheça o trabalho e as peças selecionadas."),
"batekoo":("BATEKOO | Projeto de Alícia Coura","Conheça a experiência de Alícia Coura em conteúdo e produção cultural com a BATEKOO."),
"documentario-dj":("E eu não sou uma DJ? | Alícia Coura","Documentário autoral de Alícia Coura sobre trajetórias, experiências e desafios de mulheres negras DJs em Belo Horizonte.")
}
parts=sorted((ROOT/"site-parts").glob("part-*.txt"))
assert len(parts)==28,f"Esperadas 28 partes, encontrei {len(parts)}"
source="".join(p.read_text(encoding="utf-8") for p in parts)
match=re.search(r"const AC_PAGES=(\{.*?\});",source,re.S)
assert match,"Origem não contém AC_PAGES"
data=json.loads(match.group(1))
assert set(data)==set(PAGES)
links=re.compile(r'\bhref=(?P<q>["\'])(?:\./)?(?P<page>'+"|".join(PAGES)+r')\.html(?P<hash>\#[^"\']*)?(?P=q)',re.I)
for slug in PAGES:
    src=base64.b64decode(data[slug]).decode("utf-8")
    assert src.lstrip().startswith("<!DOCTYPE html>")
    src=links.sub(lambda m:'href='+m["q"]+('/' if m["page"]=="index" else '/'+m["page"]+'/')+(m["hash"] or '')+m["q"],src)
    src,n=re.subn(r'<script id="ac-v34-router-bridge">.*?</script>','',src,count=1,flags=re.S)
    assert n==1
    src=src.replace("__ANCHOR_PLACEHOLDER__","")
    src=re.sub(r'<title\b[^>]*>.*?</title>','',src,count=1,flags=re.I|re.S)
    src=re.sub(r'<meta\b(?=[^>]*\bname=["\']description["\'])[^>]*\/?>','',src,count=1,flags=re.I)
    title,desc=META[slug]
    url=DOMAIN+('/' if slug=="index" else '/'+slug+'/')
    esc=lambda s:html.escape(s,quote=True)
    tags=[
      f'<title>{esc(title)}</title>',
      f'<meta name="description" content="{esc(desc)}">',
      '<meta name="robots" content="index,follow,max-image-preview:large">',
      f'<link rel="canonical" href="{url}">',
      '<meta property="og:type" content="website">',
      '<meta property="og:locale" content="pt_BR">',
      '<meta property="og:site_name" content="Alícia Coura">',
      f'<meta property="og:title" content="{esc(title)}">',
      f'<meta property="og:description" content="{esc(desc)}">',
      f'<meta property="og:url" content="{url}">',
      f'<meta property="og:image" content="{DOMAIN}/assets/alicia-coura-og.jpg">',
      '<meta property="og:image:width" content="1200">',
      '<meta property="og:image:height" content="630">',
      '<meta property="og:image:type" content="image/jpeg">',
      '<meta property="og:image:alt" content="Alícia Coura. Jornalismo, cultura e conteúdo.">',
      '<meta name="twitter:card" content="summary_large_image">',
      f'<meta name="twitter:title" content="{esc(title)}">',
      f'<meta name="twitter:description" content="{esc(desc)}">',
      f'<meta name="twitter:image" content="{DOMAIN}/assets/alicia-coura-og.jpg">'
    ]
    src,n=re.subn(r'</head>',"\n".join(tags)+"\n</head>",src,count=1,flags=re.I)
    assert n==1
    if slug=="index":
        js="<script>(function(){const h=location.hash||'';if(!h.startsWith('#/'))return;const parts=h.slice(2).split('/');const list=new Set("+json.dumps(PAGES)+");if(!list.has(parts[0]))return;const path=parts[0]==='index'?'/':'/'+parts[0]+'/';location.replace(path+(parts.length>1?'#'+parts.slice(1).join('/'):''));})();</script>"
        src=src.replace("<head>","<head>"+js,1)
    path=ROOT/("index.html" if slug=="index" else slug+"/index.html")
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(src,encoding="utf-8")
    assert not links.search(src)
    print("Pagina gerada:",path.relative_to(ROOT))
(ROOT/".nojekyll").write_text("",encoding="utf-8")
(ROOT/"robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: "+DOMAIN+"/sitemap.xml\n",encoding="utf-8")
urls=[DOMAIN+('/' if p=="index" else '/'+p+'/') for p in PAGES]
(ROOT/"sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+"".join("  <url><loc>"+url+"</loc></url>\n" for url in urls)+"</urlset>\n",encoding="utf-8")
