#!/usr/bin/env python3
"""Genera el sitio completo a partir de datos/sitio.json y fuente/laboratorio.html.

Uso:  python3 build.py

Páginas que produce:
  index.html                              Inicio (perfil)
  presentaciones/index.html               Presentaciones
  docencia/index.html                     Docencia: años → semestres → cursos
  docencia/<semestre>/<curso>/index.html  Un curso con sus unidades
  docencia/laboratorio/index.html         Laboratorio interactivo (desde fuente/laboratorio.html)
"""
import json, html, os, pathlib

RAIZ = pathlib.Path(__file__).resolve().parent
D = json.loads((RAIZ / "datos" / "sitio.json").read_text(encoding="utf-8"))
P = D["perfil"]
e = html.escape
FUENTES = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
           '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
           '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Spectral:wght@500;600&'
           'family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">')


def escribir(ruta, texto):
    destino = RAIZ / ruta
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(texto, encoding="utf-8")
    print("  ", ruta)


def pagina(ruta, titulo, actual, cuerpo, descripcion=""):
    """Envuelve el contenido con encabezado, menú y pie. `ruta` define la profundidad para los enlaces relativos."""
    prof = len(pathlib.PurePosixPath(ruta).parts) - 1
    r = "../" * prof
    menu = [("Inicio", "", "inicio"), ("Docencia", "docencia/", "docencia"),
            ("Presentaciones", "presentaciones/", "presentaciones")]
    nav = "".join(f'<a href="{r}{h}"{" aria-current=page" if k == actual else ""}>{t}</a>' for t, h, k in menu)
    escribir(ruta, f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(titulo)}</title>
<meta name="description" content="{e(descripcion or P['resumen'])}">
{FUENTES}
<link rel="stylesheet" href="{r}assets/sitio.css">
</head>
<body>
<div class="top"><div class="wrap"><a class="brand" href="{r}">{e(P['nombre'])}</a><nav class="nav" aria-label="Secciones">{nav}</nav></div></div>
<main><div class="wrap">
{cuerpo}
</div></main>
<footer><div class="wrap"><span>{e(P['nombre'])} · {e(P['institucion'])}</span><span><a href="mailto:{e(P['correo'])}">{e(P['correo'])}</a></span></div></footer>
</body>
</html>
""")


def iniciales(nombre):
    partes = nombre.split()
    return (partes[0][0] + (partes[1][0] if len(partes) > 1 else "")).upper()


# ---------- Inicio ----------
def inicio():
    foto = (f'<img class="avatar" src="{e(P["foto"])}" alt="Foto de {e(P["nombre"])}">' if P.get("foto")
            else f'<div class="avatar" aria-hidden="true">{iniciales(P["nombre"])}</div>')
    enlaces = "".join(f'<a href="{e(x["url"])}">{e(x["nombre"])}</a>' for x in P.get("enlaces", []))
    actuales = [c for a in D["docencia"][:1] for s in a["semestres"][:1] for c in s["cursos"]]
    sem = D["docencia"][0]["semestres"][0]
    lista = "".join(f'<li><a href="docencia/{sem["id"]}/{c["slug"]}/">{e(c["nombre"])}</a> <span class="code">{e(c["codigo"])}</span></li>' for c in actuales)
    cuerpo = f"""
<section class="hero">
  {foto}
  <div>
    <p class="eyebrow">{e(P['cargo'])}</p>
    <h1>{e(P['nombre'])}</h1>
    <p class="affil">{e(P['unidad'])}<span>{e(P['institucion'])}</span></p>
    <p class="lede">{e(P['resumen'])}</p>
    <div class="links"><a href="mailto:{e(P['correo'])}">{e(P['correo'])}</a>{enlaces}</div>
  </div>
</section>
<section class="section">
  <div class="cards">
    <a class="card" href="docencia/"><h3>Docencia</h3><p>Mis cursos por año y semestre, con sus unidades y el material de cada una.</p><span class="go">Ver cursos →</span></a>
    <a class="card" href="{e(D['laboratorio'])}"><h3>Laboratorio interactivo</h3><p>Visualizaciones y ejercicios interactivos: integrales múltiples, ecuaciones diferenciales, matrices y vectores.</p><span class="go">Abrir el laboratorio →</span></a>
    <a class="card" href="presentaciones/"><h3>Presentaciones</h3><p>Charlas, exposiciones y material de presentaciones.</p><span class="go">Ver presentaciones →</span></a>
  </div>
</section>
<section class="section">
  <h2>Cursos este semestre</h2>
  <p class="muted" style="margin-top:-6px">{D['docencia'][0]['anio']} · {e(sem['nombre'])}</p>
  <ul>{lista}</ul>
</section>"""
    pagina("index.html", P["nombre"], "inicio", cuerpo)


# ---------- Presentaciones ----------
def presentaciones():
    items = sorted(D.get("presentaciones", []), key=lambda x: x.get("fecha", ""), reverse=True)
    if items:
        filas = "".join(f"""<article class="talk"><span class="when">{e(x.get('fecha',''))}{(' · ' + e(x['lugar'])) if x.get('lugar') else ''}</span>
<h3>{e(x['titulo'])}</h3><span class="muted">{e(x.get('evento',''))}</span>{('<p style="margin:4px 0 0">' + e(x['resumen']) + '</p>') if x.get('resumen') else ''}
{('<a href="' + e(x['enlace']) + '">Ver presentación →</a>') if x.get('enlace') else ''}</article>""" for x in items)
        lista = f'<div class="talks">{filas}</div>'
    else:
        lista = '<p class="empty">Aún no hay presentaciones publicadas.</p>'
    cuerpo = f'<p class="eyebrow">{e(P["nombre"])}</p><h1>Presentaciones</h1><p class="lede">Charlas, exposiciones y material de presentaciones.</p>{lista}'
    pagina("presentaciones/index.html", "Presentaciones · " + P["nombre"], "presentaciones", cuerpo)


# ---------- Docencia ----------
def recurso_url(x, r):
    if x.get("lab"):
        return f'{r}{D["laboratorio"]}#{x["lab"]}'
    return x.get("url", "#")


def docencia():
    bloques = ""
    for a in D["docencia"]:
        sems = ""
        for s in a["semestres"]:
            tarjetas = ""
            for c in s["cursos"]:
                nlab = sum(len(u.get("recursos", [])) for u in c["unidades"])
                extra = f'<span class="badge">{nlab} recurso{"s" if nlab != 1 else ""} interactivo{"s" if nlab != 1 else ""}</span>' if nlab else ""
                tarjetas += f"""<a class="card" href="{s['id']}/{c['slug']}/"><span class="code">{e(c['codigo'])}</span><h3>{e(c['nombre'])}</h3>
<p>{e(c['carreras'])}</p><div class="meta"><span>{len(c['unidades'])} unidades</span>{extra}</div><span class="go">Ver unidades →</span></a>"""
            sems += f'<div class="sem"><h3>{e(s["nombre"])}</h3><div class="cards">{tarjetas}</div></div>'
        bloques += f'<section class="year"><h2>{a["anio"]}</h2>{sems}</section>'
    cuerpo = f"""<p class="eyebrow">{e(P['nombre'])}</p><h1>Docencia</h1>
<p class="lede">Cursos por año y semestre. Cada curso está organizado por unidades, con los temas y el material interactivo de cada una.</p>
<p style="margin-top:14px"><a href="laboratorio/">Abrir el laboratorio interactivo completo →</a></p>
{bloques}"""
    pagina("docencia/index.html", "Docencia · " + P["nombre"], "docencia", cuerpo)

    for a in D["docencia"]:
        for s in a["semestres"]:
            for c in s["cursos"]:
                curso(a, s, c)


def curso(a, s, c):
    ruta = f"docencia/{s['id']}/{c['slug']}/index.html"
    r = "../../../"
    unidades = ""
    for i, u in enumerate(c["unidades"], 1):
        temas = "".join(f"<li>{e(t)}</li>" for t in u["temas"])
        recs = "".join(f'<a href="{e(recurso_url(x, r))}">{e(x["titulo"])}<small>{"Laboratorio interactivo" if x.get("lab") else e(x.get("tipo", "Material"))}</small></a>' for x in u.get("recursos", []))
        recs = recs or '<p class="none">Material en preparación.</p>'
        ahora = ' <span class="badge">En curso</span>' if u.get("actual") else ""
        unidades += f"""<article class="unit"><header><span class="n">Unidad {i}</span><h3>{e(u['titulo'])}</h3>{ahora}</header>
<div><ul>{temas}</ul></div><div class="res"><h4>Material</h4>{recs}</div></article>"""
    rol = f' · {e(c["rol"])}' if c.get("rol") else ""
    cuerpo = f"""<nav class="crumbs" aria-label="Ruta"><a href="{r}docencia/">Docencia</a> / {a['anio']} · {e(s['nombre'])}</nav>
<p class="eyebrow"><span class="code">{e(c['codigo'])}</span> · {a['anio']}, {e(s['nombre'].lower())}{rol}</p>
<h1>{e(c['nombre'])}</h1><p class="lede">{e(c['carreras'])}</p>
<div class="units">{unidades}</div>"""
    pagina(ruta, f"{c['nombre']} ({c['codigo']}) · {P['nombre']}", "docencia", cuerpo, f"{c['nombre']}: unidades y material del curso.")


# ---------- Laboratorio ----------
def laboratorio():
    fuente = (RAIZ / "fuente" / "laboratorio.html").read_text(encoding="utf-8")
    barra = (f'<div style="font:500 14px/1.4 \'IBM Plex Sans\',system-ui,sans-serif;padding:10px max(16px,env(safe-area-inset-left,0px));'
             f'border-bottom:1px solid var(--line);background:var(--panel);display:flex;flex-wrap:wrap;gap:6px 18px">'
             f'<a href="../../" style="color:var(--ink);text-decoration:none;font-weight:600">{e(P["nombre"])}</a>'
             f'<a href="../" style="color:var(--accent)">← Docencia</a></div>')
    escribir("docencia/laboratorio/index.html", f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<style>body{{margin:0}}[hidden]{{display:none!important}}</style>
</head>
<body>
{barra}
{fuente}
</body>
</html>
""")


if __name__ == "__main__":
    print("Generando el sitio:")
    inicio(); presentaciones(); docencia(); laboratorio()
    (RAIZ / ".nojekyll").write_text("")
    print("Listo.")
