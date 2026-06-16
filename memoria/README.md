# Memoria — informe final (LaTeX, plantilla FCFM/UChile)

Esqueleto de la memoria usando la clase `umemoria` de
[dccuchile/memoria-tesis-latex](https://github.com/dccuchile/memoria-tesis-latex),
que ya cumple con el [Manual de Normalización de Formato y Escritura](https://repositorio.uchile.cl/handle/2250/185276)
de la FCFM (tamaño carta, márgenes 3/2/2/2 cm, portada, numeración romana/arábiga, etc.).

## Cómo trabajar en Overleaf

Opción A — importar desde GitHub (recomendada, mantiene todo sincronizado):

1. Subir este repo a GitHub.
2. En Overleaf: **New Project → Import from GitHub** y elegir el repo.
3. En **Menu → Settings**: *Compiler* = `pdfLaTeX`, *Main document* = `memoria/main.tex`.

Opción B — subir un ZIP:

1. Comprimir **solo la carpeta `memoria/`** (`zip -r memoria.zip memoria`).
2. En Overleaf: **New Project → Upload Project** y subir el ZIP.
3. Compilador `pdfLaTeX`, documento principal `main.tex`.

> No hay LaTeX instalado localmente, por eso la compilación se hace en Overleaf.
> Si luego instalas una distribución (MacTeX), puedes compilar con
> `latexmk -pdf main.tex` dentro de `memoria/`.

## Estructura de archivos

| Archivo | Contenido |
|---|---|
| `main.tex` | Documento maestro: metadatos de portada, resumen, índice, `\input` de capítulos. |
| `intro.tex` | Capítulo 1 — Introducción (contexto, problema, objetivos, alcances, estructura). |
| `cap_marco_teorico.tex` | Capítulo 2 — Marco teórico y revisión de la literatura. |
| `cap_metodologia.tex` | Capítulo 3 — Materiales y métodos (fuentes, normalización, modelos, métricas). |
| `cap_resultados.tex` | Capítulo 4 — Resultados. |
| `cap_discusion.tex` | Capítulo 5 — Discusión (optativo según el manual). |
| `conclu.tex` | Capítulo 6 — Conclusiones. |
| `anexoA.tex` | Anexo A — material complementario. |
| `bibliografia.bib` | Referencias en BibTeX (sembradas desde `REFERENCIAS.md`). |
| `umemoria.cls` | Clase LaTeX de la FCFM (no editar). |
| `imagenes/` | Escudo U. de Chile y logo FCFM para la portada. |

## Pendientes antes de la entrega

- [ ] Completar los integrantes de la comisión en `main.tex` (`\comision{...}`), con
      **nombre y los dos apellidos** de cada uno (Biblioteca lo revisa).
- [ ] Confirmar el título definitivo y el alcance (Francia, o Francia + Chile).
- [ ] Redactar el resumen ejecutivo (1 página) al final.
- [ ] Reemplazar los comentarios guía de cada sección por el texto real.
- [ ] Revisar las citas de `bibliografia.bib` (las de cohesión partidaria están por confirmar).
