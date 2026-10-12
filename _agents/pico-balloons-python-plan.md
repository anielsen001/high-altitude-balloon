# PicoBalloons: Python as the canonical version, then Pyodide

Status as of 2026-10-12.

## Decisions

- Python (`_sources/filling/PicoBalloons.py`) is the version to use going forward. The Julia version (`PicoBalloons.jl`) was an experiment, developed against `float1g.xls`.
- Keep astropy units and pandas in the Python module for now.

## Done

- `PicoBalloons.py` validated against `PicoBalloons.jl` (108 cases, agreement to floating-point precision) and against `float1g.xls` (within 0.03%, 0.5% on differential pressure, explained by the spreadsheet's 97% helium density and coarser table lookup).
- Python fixes: Julia-style `float_*` attribute names, `np.interp` with out-of-range errors, file-relative `atmos.csv`, scalar results, clean units, `info()` fixed.
- `test_PicoBalloons.py` rewritten as a pytest suite (spreadsheet reference, Julia golden values, error paths).

## To do

1. Port the Julia users to Python:
   - `calculators/float2.qmd` (and `float.qmd`, `_sources/filling/float1g.qmd`)
   - historical launch pages `launches/2025-11-06-smore-002/balloon-filling.qmd` and `launches/2026-05-03-smore-003/_balloon-filling.qmd`. These record past results fitted with 0.15 m^3 per 32in balloon, so re-fit or leave as history. Decide when porting.
2. Retire `PicoBalloons.jl`, `float.jl` and `test_float1g.jl` once nothing uses them.
3. Pyodide / browser calculator (tracked in GitHub issue #61):
   - Check which of numpy, pandas and astropy the target Pyodide version provides, and what they cost to load.
   - Likely path: a unit-free core in plain SI floats, with explicit unit names, using numpy or the standard library only.
   - Embed the 8,000-row atmosphere table as data (thin or compress it) instead of reading `atmos.csv` at run time.
   - Keep the astropy-based API working for notebooks, or share the core between both.
   - Keep the pytest suite as the contract; run the same cases against the browser build.
   - Decide how the page is delivered from the Quarto site (Pyodide in a page, or a `quarto-live` style approach).
4. Update `_sources/u4b/u4b_008.qmd` note, which says the fill plan was calculated with `PicoBalloons.jl`, once the calculators move to Python.

## Open questions

- Balloon mass: calculators use 38 g per 32in balloon, the measurement says 36.4 g.
- CyMylar 60 volume (0.41 m^3) is a tape-measure ellipsoid estimate and is the main uncertainty in the 008 altitude prediction.

## GitHub issue text (Pyodide work, filed as #61)

Title: Make PicoBalloons calculator run in the browser with Pyodide

Body:

The balloon float calculator (`_sources/filling/PicoBalloons.py`) is now the canonical version, validated against `PicoBalloons.jl` and `float1g.xls` and covered by `test_PicoBalloons.py`. The goal is to run it in a browser with Pyodide so the calculations are easy to do from the website.

Tasks:

- [ ] Check what Pyodide provides (numpy, pandas, astropy) and the load cost
- [ ] Unit-free core in plain SI floats (numpy or standard library only), keeping the astropy API for notebooks
- [ ] Embed the atmosphere table (`atmos.csv`, 8,000 rows) as data instead of a file read
- [ ] Run `test_PicoBalloons.py` cases against the browser build
- [ ] Choose how to deliver it from the Quarto site and add it to the sidebar
- [ ] Port `calculators/float2.qmd` and related pages from Julia to Python first

See `_agents/pico-balloons-python-plan.md`.
