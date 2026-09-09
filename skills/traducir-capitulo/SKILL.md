---
name: traducir-capitulo
description: Traduce un capítulo completo de un libro PDF al español de forma fiel (sin resumir ni omitir contenido), extrayendo las ilustraciones, auditando la fidelidad con scripts y generando PDF final con índice. Use cuando el usuario pida traducir un capítulo o sección de un libro/PDF al español, extraer y traducir contenido de un PDF, o generar la versión española de un capítulo con sus figuras.
---

# Skill: traducir-capitulo

Pipeline de traducción fiel de capítulos de libros PDF (inglés → español). Produce:

- `<capitulo>-es.md` — traducción completa con imágenes referenciadas
- `imagenes/figura-N.M.png` — ilustraciones extraídas del original
- `<Capitulo>-ES.pdf` — PDF autocontenido con índice y figuras embebidas
- Auditoría de fidelidad automática (todos los checks deben dar PASS)

## Requisitos

`pdftotext`, `pdfimages`, `pdfinfo` (poppler-utils), `pandoc`, `xelatex`. Verificar con `which` antes de empezar.

**Importante:** `fvextra` NO está instalado en este sistema → no usar `-H header.tex` en pandoc.

## Entradas

- **PDF**: ruta del libro
- **Capítulo y/o rango de páginas**: ej. "capítulo 4, páginas 136-174"

## Fase 1 — Verificación de límites (OBLIGATORIA)

**NUNCA confiar en el rango de páginas indicado por el usuario** (suele estar desplazado ±1-2 páginas). Verificar extrayendo las páginas límite:

```bash
pdfinfo LIBRO.pdf                                  # total de páginas
pdftotext -f INICIO -l INICIO LIBRO.pdf - | head -15
pdftotext -f FIN -l FIN LIBRO.pdf - | head -25
pdftotext -f FIN+1 -l FIN+1 LIBRO.pdf - | head -10
```

- **Inicio real**: página donde aparece el título del capítulo (línea inicial "N Título del capítulo").
- **Fin real**: última página antes del título del capítulo siguiente (típicamente tras la sección "N.x Conclusion").
- Presentar el rango corregido al usuario y confirmar antes de continuar.

## Fase 2 — Extracción

```bash
mkdir -p SALIDA/imagenes
pdftotext -f INICIO -l FIN LIBRO.pdf SALIDA/capitulo-original.txt
pdfimages -list -f INICIO -l FIN LIBRO.pdf        # imágenes por página
pdfimages -png -f INICIO -l FIN -p LIBRO.pdf SALIDA/imagenes/figura
```

**Mapeo imagen↔caption**: por cada página P con imagen:

```bash
pdftotext -f P -l P LIBRO.pdf - | grep -i "FIGURE"
```

Renombrar `figura-P-NNN.png` → `figura-N.M.png` según su caption (FIGURE N.M). Si hay varias imágenes por página, mapear por orden de aparición.

Analizar la estructura para planificar la traducción:

```bash
grep -nE "^[0-9]+\.[0-9]+[[:space:]]" SALIDA/capitulo-original.txt   # secciones
grep -icE "FIGURE" SALIDA/capitulo-original.txt                      # nº de figuras
wc -w SALIDA/capitulo-original.txt                                   # tamaño
```

## Fase 3 — Traducción fiel por partes

**Leer el texto original completo primero.** Traducir en 3-4 archivos `parte-01.md` … `parte-NN.md` (uno por sección mayor) y concatenar después. Nunca un solo Write gigante.

### Reglas de fidelidad (innegociables)

1. **No resumir, no omitir, no reducir**: cada párrafo del original debe existir traducido.
2. **Código intacto**: los bloques de código se copian tal cual (fenced ```dart), incluyendo las marcas `**...**` (en el libro indican líneas críticas). Traducir SOLO los comentarios dentro del código, si el usuario lo aprobó.
3. **Términos técnicos en inglés**: widget, mixin, extends, implements, with, on, abstract, interface, factory, override, callback, etc.
4. **Captions de figuras**: "FIGURE N.M: texto" → "FIGURA N.M: traducción", con embed `![FIGURA N.M: ...](imagenes/figura-N.M.png)` y la línea en cursiva `*FIGURA N.M: ...*` debajo.
5. **Referencias cruzadas del libro se mantienen tal cual** (aunque parezcan erratas del original, ej. "hablaremos de patrones en el Capítulo 4").
6. **Acrónimos** (KISS, DRY, YAGNI, SOLID...): mantener el acrónimo y glosar su expansión en español entre paréntesis en la primera mención.
7. **Encabezados**: traducidos conservando la numeración original (`## 4.1 ...`, `### 4.1.1 ...`). El título del capítulo es H1 (`# 4 ...`).
8. **Nombres propios sin traducir**: autores, revisores, títulos de libros citados.
9. **Hyphenation de pdftotext**: palabras partidas ("wellcrafted" = "well-crafted", "decisionmaking" = "decision-making") → traducir el sentido correcto.
10. Añadir al inicio una nota de traducción breve (blockquote) indicando libro, páginas de origen y convenciones usadas.

### ⚠️ Regla crítica de ensamblado

Cada archivo `parte-NN.md` **DEBE terminar con una línea en blanco** (doble salto de línea al final). Si no, el primer encabezado de la parte siguiente queda pegado al último párrafo y pandoc lo renderiza como texto literal (no aparece en el índice del PDF).

## Fase 4 — Ensamblado y QA de fidelidad

```bash
cat parte-*.md > capitulo-es.md   # ojo: cat parte-*.md ordena bien con 2 dígitos
python3 ~/.opencode/skills/traducir-capitulo/scripts/qa_fidelidad.py capitulo-original.txt capitulo-es.md
```

El script audita: cobertura de identificadores, mapeo de párrafos por anclas, prosa inglesa sin traducir, conteos estructurales (encabezados, figuras, declaraciones class/mixin, vallas de código) y encabezados pegados. **Corregir hasta que todos los checks den PASS.** Único falso positivo aceptable: `FIGURE` (traducido intencionalmente a `FIGURA`).

## Fase 5 — PDF

```bash
~/.opencode/skills/traducir-capitulo/scripts/generar_pdf.sh capitulo-es.md /ruta/absoluta/Capitulo-ES.pdf
```

El script: elimina el alt text de las imágenes en una copia temporal (evita captions duplicadas "Figure N:"), genera con pandoc+xelatex (tamaño carta, 10pt, TOC "Contenido", Latin Modern Mono, links azules) y verifica el PDF (páginas, encabezados presentes, 0 "###" literales, 0 captions duplicadas, imágenes embebidas = imágenes del .md).

Si alguna línea de código supera ~85 chars, el script avisa (sin fvextra no hay salto de línea automático en código).

## Fase 6 — Entrega

Reportar al usuario:

1. Rutas del `.md`, la carpeta `imagenes/` y el `.pdf`
2. Tabla resumen de la auditoría (checks PASS)
3. Recordar: el PDF es autocontenido (movible/compartible); el `.md` necesita `imagenes/` junto a él

## Pitfalls conocidos

1. **Rango del usuario desplazado ±1 página** → siempre ejecutar Fase 1 y confirmar.
2. **Encabezados fusionados en uniones de partes** → línea en blanco final obligatoria en cada parte (Fase 3); qa_fidelidad.py lo detecta.
3. **fvextra no instalado** → no usar header.tex; el script de PDF mide la línea de código más larga antes de generar.
4. **Doble caption en PDF** → el alt text del embed dispara captions automáticas de LaTeX; generar_pdf.sh lo elimina en la copia temporal.
5. **pdftotext antepone `\f` (form feed)** al inicio de cada página → los conteos con `^patrón` fallan; qa_fidelidad.py elimina `\f` antes de contar.
6. **Traducciones largas** → escribir en partes evita cortes de contexto; concatenar y auditar después.
7. **Comillas tipográficas**: el PDF puede renderizar `'` como `’`; generar_pdf.sh normaliza antes de comparar encabezados.
