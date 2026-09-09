#!/usr/bin/env bash
# generar_pdf.sh — Genera el PDF final desde el markdown traducido y lo verifica.
#
# Uso:
#   generar_pdf.sh <capitulo-es.md> </ruta/absoluta/salida.pdf>
#
# Pasos:
#   1. Verifica herramientas (pandoc, xelatex, poppler)
#   2. Mide la línea de código más larga (sin fvextra no hay salto automático)
#   3. Crea copia temporal sin alt text en imágenes (evita captions duplicadas "Figure N:")
#   4. Genera PDF con pandoc + xelatex (carta, 10pt, TOC "Contenido", Latin Modern Mono)
#   5. Verifica: páginas, encabezados presentes, 0 "###" literales,
#      0 captions duplicadas, imágenes embebidas = imágenes del .md
set -euo pipefail

MD="${1:?Uso: generar_pdf.sh <capitulo-es.md> </ruta/absoluta/salida.pdf>}"
PDF="${2:?Uso: generar_pdf.sh <capitulo-es.md> </ruta/absoluta/salida.pdf>}"

MD_DIR="$(cd "$(dirname "$MD")" && pwd)"
MD_FILE="$(basename "$MD")"
cd "$MD_DIR"

# --- 1) Herramientas ---
for t in pandoc xelatex pdftotext pdfinfo pdfimages; do
  command -v "$t" >/dev/null 2>&1 || { echo "ERROR: falta la herramienta '$t'"; exit 1; }
done

# --- 2) Longitud máxima de línea en bloques de código ---
MAXLEN=$(awk '/^```/{inb=!inb; next} inb{if(length($0)>m)m=length($0)} END{print m+0}' "$MD_FILE")
echo "Línea de código más larga: $MAXLEN chars"
if [ "$MAXLEN" -gt 85 ]; then
  echo "AVISO: hay líneas de código >85 chars; sin fvextra pueden desbordar el margen."
fi

# --- 3) Copia sin alt text ( LaTeX no genera caption automática "Figure N:" ) ---
sed 's/!\[[^]]*\](/![](/g' "$MD_FILE" > .pdf-source.tmp.md
trap 'rm -f .pdf-source.tmp.md' EXIT

# --- 4) Generación ---
pandoc .pdf-source.tmp.md -o "$PDF" \
  --pdf-engine=xelatex \
  --toc -V toc-title=Contenido \
  -V geometry:letterpaper -V geometry:margin=1in \
  -V fontsize=10pt \
  -V colorlinks=true -V linkcolor=blue \
  -V monofont="Latin Modern Mono"

# --- 5) Verificación ---
PAGES=$(pdfinfo "$PDF" | awk '/^Pages/{print $2}')
IMG_PDF=$(pdfimages -list "$PDF" | tail -n +3 | wc -l | tr -d ' ')
IMG_MD=$(grep -cE '!\[.*\]\(' "$MD_FILE" || true)
TXT=$(pdftotext "$PDF" - | sed "s/’/'/g; s/“/\"/g; s/”/\"/g")
LIT_HDR=$(printf '%s\n' "$TXT" | grep -c "###" || true)
DUP_CAP=$(printf '%s\n' "$TXT" | grep -cE "^Figure [0-9]+:" || true)

FAIL=0
[ "$PAGES" -gt 0 ] && echo "Páginas: $PAGES" || { echo "ERROR: PDF vacío"; exit 1; }

if [ "$IMG_PDF" = "$IMG_MD" ]; then
  echo "Imágenes embebidas: $IMG_PDF/$IMG_MD OK"
else
  echo "FAIL: imágenes embebidas ($IMG_PDF) != imágenes del .md ($IMG_MD)"; FAIL=1
fi

if [ "$LIT_HDR" -eq 0 ]; then
  echo "Encabezados literales '###': 0 OK"
else
  echo "FAIL: $LIT_HDR encabezados '###' renderizados como texto (fusionados)"; FAIL=1
fi

if [ "$DUP_CAP" -eq 0 ]; then
  echo "Captions duplicadas 'Figure N:': 0 OK"
else
  echo "FAIL: $DUP_CAP captions duplicadas 'Figure N:'"; FAIL=1
fi

# Encabezados del .md presentes en el PDF (comillas ya normalizadas)
while IFS= read -r h; do
  hn=$(printf '%s' "$h" | sed "s/’/'/g; s/“/\"/g; s/”/\"/g")
  if ! grep -qF -- "$hn" <<< "$TXT"; then
    echo "FAIL: encabezado ausente en el PDF: $h"; FAIL=1
  fi
done < <(grep -E '^#{1,4} ' "$MD_FILE" | sed 's/^#\+\s*//')
echo "Encabezados verificados en el PDF: $(grep -cE '^#{1,4} ' "$MD_FILE" || true)"

if [ "$FAIL" -eq 0 ]; then
  echo "PDF OK: $PDF"
else
  echo "PDF generado CON FALLOS — revisar antes de entregar"
  exit 1
fi
