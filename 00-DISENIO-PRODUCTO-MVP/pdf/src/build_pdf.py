#!/usr/bin/env python3
"""Generador de los PDFs del módulo 00 - Diseño de Producto MVP.

Guía completa  -> guia-completa.css + guia-completa.html (render: Chrome headless)
Guía resumen   -> guia-resumen.css  + guia-resumen.html  (render: wkhtmltopdf)

Uso:
    python3 build_pdf.py

Salidas (sobrescribe):
    pdf/00-DISENIO-PRODUCTO-MVP.pdf
    pdf/GUIA-RESUMEN-00-DISENIO-PRODUCTO-MVP.pdf
"""

import html
import os
import shutil
import subprocess
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
MODULE = os.path.dirname(os.path.dirname(BASE))
SRC = BASE
DIST = os.path.join(BASE, "dist")
PDF_DIR = MODULE

COVER = os.path.join(BASE, "guia-completa.css")
RESUMEN_HTML = os.path.join(BASE, "guia-resumen.html")
RESUMEN_CSS = os.path.join(BASE, "guia-resumen.css")

# ---------------------------------------------------------------------------
# Definición de la guía completa: partes -> capítulos -> archivo .md
# ---------------------------------------------------------------------------

PARTS = [
    (
        "Parte 1 · Design Sprint",
        [
            ("01", "Paso 01", "01-design-sprint-intro.md"),
            ("02", "Paso 02", "02-understand-define.md"),
            ("03", "Paso 03", "03-sketch-decide.md"),
        ],
    ),
    (
        "Parte 2 · Material Design 3",
        [
            ("04", "Paso 04", "04-m3-fundamentos.md"),
            ("05", "Paso 05", "05-m3-componentes-mobile.md"),
        ],
    ),
    (
        "Parte 3 · Prototipado y validación",
        [
            ("06", "Paso 06", "06-prototipado-validacion.md"),
        ],
    ),
    (
        "Parte 4 · Implementación Flutter",
        [
            ("07", "Paso 07", "07-m3-flutter-implementacion.md"),
            ("08", "Paso 08", "08-template-proyecto.md"),
        ],
    ),
    (
        "Parte 5 · Caso integrador",
        [
            ("09", "Caso 09", "09-caso-completo-mvp.md"),
        ],
    ),
    (
        "Parte 6 · Cierre",
        [
            ("BI", "Anexo", "BIBLIOGRAFIA.md"),
        ],
    ),
]


def sh(cmd):
    print("+ " + " ".join(cmd))
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.stdout.strip():
        print(proc.stdout.strip()[:4000])
    if proc.returncode != 0:
        print(proc.stderr.strip()[:4000], file=sys.stderr)
        sys.exit(proc.returncode)
    return proc


def md_to_html(path):
    """Convierte un .md a HTML con pandoc, quitando el H1 de portada del capítulo."""
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    title = ""
    while lines and not lines[0].strip():
        lines.pop(0)
    if lines and lines[0].startswith("# "):
        title = lines[0][2:].strip()
        lines = lines[1:]
    body = "\n".join(lines).strip()
    proc = subprocess.run(
        ["pandoc", "-f", "gfm", "-t", "html5", "--wrap=none"],
        input=body,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        print(f"pandoc falló en {path}:\n{proc.stderr[:2000]}", file=sys.stderr)
        sys.exit(1)
    return title, proc.stdout


def build_complete():
    toc_rows = []
    chapters = []
    total = sum(len(chaps) for _, chaps in PARTS)

    for part_idx, (part, chaps) in enumerate(PARTS, start=1):
        toc_rows.append(f'<div class="part">{html.escape(part)}</div>')
        for num, kick, fname in chaps:
            path = os.path.join(MODULE, fname)
            title, content = md_to_html(path)
            num_label = f"{num}"
            toc_rows.append(
                '<div class="row">'
                f'<span class="num">{html.escape(num_label)}</span>'
                f'<span class="title">{html.escape(title)}</span>'
                "</div>"
            )
            chapters.append(
                '<div class="chapter">'
                '<div class="chapter-head">'
                f'<span class="num-chip">{html.escape(kick)}</span>'
                f'<div class="kick">{html.escape(part)}</div>'
                f"<h2>{html.escape(title)}</h2>"
                "</div>"
                f'<div class="article">{content}</div>'
                "</div>"
            )

    toc = (
        '<div class="toc">'
        "<h2>Contenido</h2>"
        + f'<p class="toc-count">{total} capítulos · Design Sprint + Material Design 3 para MVP Flutter</p>'
        + "\n".join(toc_rows)
        + "</div>"
    )

    cover = """<div class="cover">
  <span class="module-tag">Módulo 00</span>
  <h1>Diseño de<br>Producto MVP</h1>
  <p class="subtitle">Design Sprint + Material Design 3 para apps Flutter. Define y valida qué construir antes de escribir una línea de código, y diseña la interfaz con el mismo sistema que usa Flutter de forma nativa.</p>
  <table class="meta">
    <tr>
      <td><span class="label">Metodología</span><span class="value">GV Design Sprint + Material Design 3</span></td>
      <td><span class="label">Backend</span><span class="value">Listo para implementar con Supabase (BaaS)</span></td>
    </tr>
    <tr>
      <td><span class="label">Nivel</span><span class="value">Producto / Diseño / Flutter</span></td>
      <td><span class="label">Tiempo estimado</span><span class="value">5 días de Sprint + implementación M3</span></td>
    </tr>
  </table>
  <div class="tags"><span>Design Sprint</span><span>Material Design 3</span><span>Flutter</span><span>MVP</span></div>
</div>"""

    doc = (
        "<!DOCTYPE html>\n<html lang=\"es\">\n<head>\n<meta charset=\"utf-8\">\n"
        "<title>00 — Diseño de Producto MVP</title>\n"
        '<link rel="stylesheet" href="guia-completa.css">\n</head>\n<body>\n'
        + cover
        + toc
        + "\n".join(chapters)
        + "\n</body>\n</html>\n"
    )

    out = os.path.join(SRC, "guia-completa.html")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(doc)
    print(f"guia-completa.html escrito ({len(doc)} bytes, {total} capítulos)")
    return out


def render_chrome(in_html, out_pdf):
    url = "file://" + in_html
    sh(
        [
            "google-chrome",
            "--headless=new",
            "--no-sandbox",
            "--disable-gpu",
            "--disable-software-rasterizer",
            "--no-pdf-header-footer",
            f"--print-to-pdf={out_pdf}",
            url,
        ]
    )


def render_wkhtmltopdf(in_html, out_pdf):
    sh(
        [
            "wkhtmltopdf",
            "--enable-local-file-access",
            "-s",
            "A4",
            "-T",
            "12mm",
            "-B",
            "12mm",
            "-L",
            "11mm",
            "-R",
            "11mm",
            in_html,
            out_pdf,
        ]
    )


def main():
    os.makedirs(DIST, exist_ok=True)

    # 1) Guía completa
    complete_html = build_complete()
    out_complete = os.path.join(DIST, "00-DISENIO-PRODUCTO-MVP.pdf")
    render_chrome(complete_html, out_complete)

    # 2) Guía resumen
    out_resumen = os.path.join(DIST, "GUIA-RESUMEN-00-DISENIO-PRODUCTO-MVP.pdf")
    render_wkhtmltopdf(RESUMEN_HTML, out_resumen)

    # 3) Copiar a la raíz del módulo (sobrescribir)
    for src, dst in [
        (out_complete, os.path.join(PDF_DIR, "00-DISENIO-PRODUCTO-MVP.pdf")),
        (out_resumen, os.path.join(PDF_DIR, "GUIA-RESUMEN-00-DISENIO-PRODUCTO-MVP.pdf")),
    ]:
        shutil.copy2(src, dst)
        print(f"copiado: {dst}")

    print("OK")


if __name__ == "__main__":
    main()
