#!/usr/bin/env python3
"""
qa_fidelidad.py — Auditoría de fidelidad para traducciones EN→ES de capítulos
extraídos con pdftotext.

Compara el texto original (inglés) contra la traducción (markdown español) y
verifica:
  1. Cobertura de identificadores (prosa + código, sin comentarios)
  2. Mapeo de párrafos del original por anclas de identificadores
  3. Fuga de prosa inglesa sin traducir (fuera de bloques de código)
  4. Encabezados originales = encabezados de la traducción
  5. Figuras originales = figuras de la traducción
  6. Declaraciones class/mixin originales = traducción
  7. Vallas de código balanceadas
  8. Encabezados pegados al párrafo previo (bug de ensamblado)

Uso:
    python3 qa_fidelidad.py <original.txt> <traduccion.md>

Exit 0 si todos los checks PASAN, 1 si hay fallos, 2 si hay error de uso.
"""
import re
import sys


def ids(text):
    """Extrae identificadores técnicos: camelCase, PascalCase, UPPER_SNAKE, snake_case."""
    out = set()
    out |= set(re.findall(r"\b[a-z]+(?:[A-Z][a-z0-9]*)+\b", text))
    out |= set(re.findall(r"\b[A-Z][a-z0-9]+(?:[A-Z][a-z0-9]*)+\b", text))
    out |= set(re.findall(r"\b[A-Z][A-Z0-9_]{1,}\b", text))
    out |= set(re.findall(r"\b[a-z]+(?:_[a-z0-9]+)+\b", text))
    return out


def strip_comments(text):
    return "\n".join(re.sub(r"//.*$", "", line) for line in text.splitlines())


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)

    # El \f (form feed) de pdftotext rompe los anclajes ^ de línea: eliminarlo.
    orig = open(sys.argv[1], encoding="utf-8").read().replace("\f", "")
    trad = open(sys.argv[2], encoding="utf-8").read()
    results = []

    # --- 1. Cobertura de identificadores ---
    orig_nc = strip_comments(orig)
    i_orig = ids(orig_nc)
    missing = sorted(i for i in i_orig if i not in trad and i != "FIGURE")
    detail = f"{len(i_orig)} únicos; faltan: {missing}" if missing else f"{len(i_orig)} únicos, ninguno faltante"
    results.append(("Cobertura de identificadores", not missing, detail))

    # --- 2. Mapeo de párrafos por anclas ---
    oparas = [re.sub(r"\s+", " ", p).strip() for p in re.split(r"\n\s*\n", orig) if p.strip()]
    uncovered = []
    for p in oparas:
        pi = {i for i in ids(strip_comments(p)) if len(i) > 2 and i != "FIGURE"}
        miss = {i for i in pi if i not in trad}
        if miss:
            uncovered.append((p[:60] + "...", sorted(miss)))
    cov = f"{len(oparas) - len(uncovered)}/{len(oparas)}"
    if uncovered:
        cov += "; sin cubrir: " + "; ".join(f"[{u[0]}] faltan {u[1]}" for u in uncovered[:5])
    results.append(("Párrafos cubiertos (anclas)", not uncovered, cov))

    # --- 3. Fuga de prosa inglesa fuera de bloques de código ---
    parts = re.split(r"(?m)^```[a-z]*\s*$", trad)
    noncode = "\n".join(p for i, p in enumerate(parts) if i % 2 == 0)
    noncode = re.sub(r"`[^`]*`", "", noncode)                 # código inline
    noncode = re.sub(r"(?m)^>.*$", "", noncode)               # blockquote (nota de traducción)
    noncode = re.sub(r"(?m)^!\[.*$", "", noncode)             # líneas de imagen
    noncode = re.sub(r"(?m)^\*FIGURA.*$", "", noncode)        # captions en cursiva
    engw = re.compile(
        r"\b(the|and|of|to|is|are|that|with|for|this|from|will|can|when|your|you|"
        r"not|but|by|be|as|it|on|or|which|their|these|those|into|more|than|also|"
        r"such|only|each|have|has|was|were|what|how|they|them|its|about|would|"
        r"should|could|may|might|do|does|make|use|used|using|get|like|both|any|"
        r"all|some|very|much|many|most|other|same|different|new|first|last|one|two)\b",
        re.I,
    )
    leaks = [ln[:120] for ln in noncode.splitlines() if len(engw.findall(ln)) >= 3]
    results.append(("Prosa inglesa sin traducir", not leaks,
                    "0 líneas sospechosas" if not leaks else f"{len(leaks)} líneas: {leaks[:5]}"))

    # --- 4. Encabezados ---
    o_heads = re.findall(r"(?m)^(\d+(?:\.\d+)*)\s+\S", orig)
    t_heads = re.findall(r"(?m)^#{1,4}\s+((?:\d+(?:\.\d+)*)?)\s*", trad)
    t_nums = [h for h in re.findall(r"(?m)^#{1,4}\s+(\d+(?:\.\d+)*)\s", trad)]
    ok = sorted(o_heads) == sorted(t_nums)
    results.append(("Encabezados orig=trad", ok,
                    f"orig={len(o_heads)} ({sorted(o_heads)}) vs trad={len(t_nums)} ({sorted(t_nums)})"))

    # --- 5. Figuras ---
    o_figs = sorted(set(re.findall(r"FIGURE (\d+\.\d+)", orig)))
    t_figs = sorted(set(re.findall(r"FIGURA (\d+\.\d+)", trad)))
    results.append(("Figuras orig=trad", o_figs == t_figs,
                    f"orig={o_figs} vs trad={t_figs}"))

    # --- 6. Declaraciones class/mixin (nombre capitalizado: evita falsos positivos de prosa) ---
    decl = re.compile(r"(?m)^((?:abstract |interface |base |final |sealed )*(?:mixin )?(?:mixin class|class)|mixin)\s+[A-Z_]")
    n_o, n_t = len(decl.findall(orig)), len(decl.findall(trad))
    results.append(("Declaraciones class/mixin", n_o == n_t, f"orig={n_o} trad={n_t}"))

    # --- 7. Vallas de código balanceadas ---
    fences = len(re.findall(r"(?m)^```", trad))
    results.append(("Vallas de código balanceadas", fences % 2 == 0,
                    f"{fences} vallas ({fences // 2} bloques)"))

    # --- 8. Encabezados pegados al párrafo previo (sin línea en blanco) ---
    lines = trad.splitlines()
    glued = [ln[:80] for i, ln in enumerate(lines)
             if ln.startswith("#") and i > 0 and lines[i - 1].strip() and not lines[i - 1].startswith("#")]
    results.append(("Encabezados sin línea en blanco previa", not glued,
                    "0" if not glued else f"{len(glued)}: {glued[:3]}"))

    # --- Informe ---
    print(f"\n=== AUDITORÍA DE FIDELIDAD ===")
    print(f"Original:     {sys.argv[1]}")
    print(f"Traducción:   {sys.argv[2]}\n")
    all_ok = True
    for name, passed, detail in results:
        mark = "PASS" if passed else "FAIL"
        if not passed:
            all_ok = False
        print(f"[{mark}] {name}: {detail}")
    print(f"\nVEREDICTO: {'TRADUCCIÓN FIEL Y COMPLETA' if all_ok else 'REVISAR — HAY FALLOS'}\n")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
