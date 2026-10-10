# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A Quarto website documenting a high-altitude pico-balloon magnetometry project: payload design, launches, calculators, and reference material. Content is Markdown/Quarto (`.qmd`) with embedded Python, Julia, and LaTeX, not an application codebase.

## Commands

Render the site (requires the podman/Docker container — Quarto, TeX, Julia, and `uv` aren't expected on the host):

```bash
podman-compose run quarto   # drop into the container
uv run quarto render        # inside the container, renders to _site/
```

The Julia depot is stored in-repo (`.julia/`) so it's visible inside the container; set `JULIA_DEPOT_PATH=/opt/project/.julia` when running Julia directly.

Python deps are managed with `uv` (`pyproject.toml` / `uv.lock`); Julia deps with `Project.toml`/`Manifest.toml`.

`quarto render` runs `make` as a `pre-render` step (see `_quarto.yml`). The root `Makefile` just recurses into `_sources/` (`SUBDIRS = _sources`), whose own `Makefile` regenerates standalone TikZ diagrams: `.tex` → `.pdf` (pdflatex) → `.png`/`.svg` (convert/inkscape). Run `make -C _sources` directly to rebuild just those figures, or `make -C _sources clean` to remove generated `.aux`/`.log`/`.pdf`/`.png`.

There is no test suite or linter.

## Architecture / layout conventions

- Directories prefixed with `_` (`_sources`, `_datasheets`, `_extensions`, `_external`, `_test`, `_agents`, `_freeze`, `_site`) are excluded from Quarto's page/nav build — they hold source assets, generated output, vendored code, or tooling rather than site pages.
- `_quarto.yml` is the single source of truth for site structure (navbar, sidebar, bibliography list, theme). When adding a new page (e.g. a launch or calculator), it must be added to the `sidebar.contents` there (launches and build pages are picked up via glob — `launches/*.qmd`, `build/*.qmd` — so new files in those two directories don't need a sidebar edit).
- `launches/*.qmd` are individual launch writeups, each named `YYYY-MM-DD-<codename>.qmd`; a same-named directory (e.g. `launches/2026-05-02-smore-004/`) holds that launch's images/data. `launches/index.qmd` and the homepage listing (`index.qmd`) surface these automatically via Quarto's `listing` feature sorted by `date`/`date-modified`.
- `calculators/*.qmd` are standalone interactive/derivation pages (horizon distance, solar elevation, float physics, Kalman filtering) — mostly self-contained math with embedded code.
- `_sources/` holds per-topic source material (one subdirectory per hardware/topic area: `rm3100`, `lora`, `u4b`, `wspr`, `solar`, `power`, `python`, etc.), including the shared Python helpers imported by `.qmd` code cells (e.g. `_sources/python/qmd_display.py`, `hysplit.py`, `map_display.py`, `wsprtv.py`) and the standalone TikZ/LaTeX figure sources built by `_sources/Makefile`.
- `_external/` vendors third-party firmware/tracker repos used as reference (LightAPRS-W, u4b) — not built or linted as part of this project, see `_external/README.md` for provenance/links.
- `_extensions/pandoc-ext/` holds a small Lua Pandoc filter (`abstract-section`) used by the Quarto render.
- Bibliography sources live in `refs/*.bib` (general refs, datasheets, solar), aggregated on `refs/refs.qmd`; datasheet PDFs live in `_datasheets/`.
- `_freeze/` and `_site/`/`output/` are Quarto's render cache and build output — never hand-edit.

## `_agents/`

Working files that Claude Code (or other agents) generate during a session — plans, TODOs, scratch notes, etc. — belong in `_agents/`, not the project root. `CLAUDE.md` itself stays at the repo root per convention.
