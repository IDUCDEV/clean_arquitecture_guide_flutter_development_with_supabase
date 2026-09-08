#!/usr/bin/env python3
"""Generador de los PDFs del módulo 18 - Debugging Flutter.

Guía completa  -> guia-completa.css + guia-completa.html (render: Chrome headless)
Guía resumen   -> guia-resumen.css  + guia-resumen.html  (render: wkhtmltopdf)

Uso:
    python3 build_pdf.py

Salidas (sobrescribe):
    pdf/18-DEBUGGING-FLUTTER.pdf
    pdf/GUIA-RESUMEN-18-DEBUGGING-FLUTTER.pdf
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
        "Parte 1 · Debugging con VS Code",
        [
            ("01", "Capítulo 01", "01-fundamentos-debugging.md"),
            ("02", "Capítulo 02", "02-configuracion-launch-json.md"),
            ("03", "Capítulo 03", "03-breakpoints-avanzados.md"),
            ("04", "Capítulo 04", "04-inspeccion-datos-consola.md"),
            ("05", "Capítulo 05", "05-multi-target-remoto.md"),
            ("06", "Capítulo 06", "06-cheatsheet-vscode.md"),
            ("07", "Capítulo 07", "07-practicas-vscode.md"),
        ],
    ),
    (
        "Parte 2 · Flutter DevTools",
        [
            ("08", "Capítulo 08", "08-fundamentos-devtools.md"),
            ("09", "Capítulo 09", "09-inspector-layout.md"),
            ("10", "Capítulo 10", "10-performance-view.md"),
            ("11", "Capítulo 11", "11-cpu-profiler.md"),
            ("12", "Capítulo 12", "12-memory-profiler.md"),
            ("13", "Capítulo 13", "13-network-view.md"),
            ("14", "Capítulo 14", "14-debugger-view.md"),
            ("15", "Capítulo 15", "15-logging-view.md"),
            ("16", "Capítulo 16", "16-app-size.md"),
            ("17", "Capítulo 17", "17-cheatsheet-devtools.md"),
            ("18", "Capítulo 18", "18-practicas-devtools.md"),
        ],
    ),
    (
        "Parte 3 · Rendimiento y optimización",
        [
            ("19", "Capítulo 19", "19-fundamentos-rendimiento.md"),
            ("20", "Capítulo 20", "20-optimizar-rebuilds.md"),
            ("21", "Capítulo 21", "21-memory-leak-detection.md"),
            ("22", "Capítulo 22", "22-rendering-complejo.md"),
            ("23", "Capítulo 23", "23-cheatsheet-optimizacion.md"),
            ("24", "Capítulo 24", "24-practicas-optimizacion.md"),
        ],
    ),
    (
        "Parte 4 · Debugging avanzado",
        [
            ("25", "Capítulo 25", "25-debugging-asincrono.md"),
            ("26", "Capítulo 26", "26-workflow-debugging-por-tipo.md"),
        ],
    ),
    (
        "Parte 5 · Maestría: mentalidad y debugging por capa",
        [
            ("27", "Capítulo 27", "27-mentalidad-debugging.md"),
            ("28", "Capítulo 28", "28-debugging-programatico-flutter.md"),
            ("29", "Capítulo 29", "29-playbook-debugging-sistematico.md"),
            ("31", "Capítulo 31", "31-debugging-por-capa.md"),
        ],
    ),
    (
        "Parte 6 · Referencia rápida",
        [
            ("30", "Capítulo 30", "30-referencia-rapida-flutter-debugging.md"),
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
        + f'<p class="toc-count">{total} capítulos · Debugging con VS Code + DevTools + Rendimiento + Maestría (Flutter)</p>'
        + "\n".join(toc_rows)
        + "</div>"
    )

    cover = """<div class="cover">
  <span class="module-tag">Módulo 18</span>
  <h1>Debugging Flutter</h1>
  <p class="subtitle">Guía completa de debugging y optimización en Flutter: mentalidad anti-dependencia de la IA, debugger de VS Code (launch.json, breakpoints avanzados, Debug Console), DevTools (Inspector, Performance, Memory, CPU Profiler, Network, Logging, App Size), fundamentos de rendimiento, optimización de rebuilds y rendering, detección de memory leaks, debugging de código asíncrono, playbook sistemático y ejecución aislada de cada capa de Clean Architecture.</p>
  <table class="meta">
    <tr>
      <td><span class="label">Enfoque</span><span class="value">Debugging y profiling</span></td>
      <td><span class="label">Stack</span><span class="value">Flutter + Dart + DevTools</span></td>
    </tr>
    <tr>
      <td><span class="label">Nivel</span><span class="value">Básico a Avanzado</span></td>
      <td><span class="label">Tiempo estimado</span><span class="value">35–45 horas</span></td>
    </tr>
  </table>
  <div class="tags"><span>VS Code</span><span>DevTools</span><span>Rendimiento</span><span>Memory</span><span>Network</span><span>Debugging</span><span>Clean Architecture</span></div>
</div>"""

    doc = (
        "<!DOCTYPE html>\n<html lang=\"es\">\n<head>\n<meta charset=\"utf-8\">\n"
        "<title>18 — Debugging Flutter</title>\n"
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
    out_complete = os.path.join(DIST, "18-DEBUGGING-FLUTTER.pdf")
    render_chrome(complete_html, out_complete)

    # 2) Guía resumen
    out_resumen = os.path.join(DIST, "GUIA-RESUMEN-18-DEBUGGING-FLUTTER.pdf")
    render_wkhtmltopdf(RESUMEN_HTML, out_resumen)

    # 3) Copiar a la raíz del módulo (sobrescribir)
    for src, dst in [
        (out_complete, os.path.join(PDF_DIR, "18-DEBUGGING-FLUTTER.pdf")),
        (out_resumen, os.path.join(PDF_DIR, "GUIA-RESUMEN-18-DEBUGGING-FLUTTER.pdf")),
    ]:
        shutil.copy2(src, dst)
        print(f"copiado: {dst}")

    print("OK")


if __name__ == "__main__":
    main()
