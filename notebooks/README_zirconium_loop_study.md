# README: Zirconium loop line broadening study

## Scope
This notebook (`zirconium_loop_line_broadening_derivation.ipynb`) provides a nine-section derivation and executable workflow for XRD line broadening in zirconium, with explicit treatment of:
- reciprocal-space transforms,
- instrumental broadening,
- Scherrer size broadening,
- microstrain and anisotropic contrast-factor broadening,
- two-population `a`/`c` loop contributions,
- synthetic peak-pattern construction.

## Modeling assumptions
1. Broadening terms are treated with either Gaussian quadrature or Lorentzian linear composition, depending on the profile assumption.
2. Hexagonal anisotropy is represented through reflection-wise contrast factors `C_hkl = C̄(1 - q η_hkl)`.
3. Zirconium-specific physical constants are *external inputs* and intentionally not fabricated in code.
4. Two defect populations (`a`-type and `c`-type) contribute as weighted components to composite widths.

## Required external inputs
| Input | Symbol | Meaning | Units | Typical source |
|---|---|---|---|---|
| X-ray wavelength | `λ` | Probe wavelength | m | Instrument/radiation configuration |
| Lattice constants | `a, c` | HCP zirconium lattice parameters | m | Refined or literature values |
| Mean contrast factor | `C̄` | Base dislocation contrast | – | Elastic-contrast calculation |
| Anisotropy coefficient | `q` | Reflection anisotropy coefficient | – | Elastic-contrast calculation |
| Burgers magnitude | `b` | Loop/dislocation Burgers vector | m | Defect model |
| Defect density | `ρ` | Loop/dislocation density | m⁻² | Fitted or independent characterization |
| Scherrer factor | `K` | Shape factor | – | Profile-model choice |
| Instrument coefficients | `U, V, W` | Caglioti coefficients | rad² | Instrument calibration |

## How to run
1. Open the notebook with JupyterLab/Notebook.
2. Run cells in order from Section 1 to Section 9.
3. Replace placeholder/example numeric values with your zirconium-specific external inputs.
4. If needed, import helpers from:
   - `src/xrd_line_broadening.py`
   - `src/contrast_factors.py`
   - `src/diffraction_simulation.py`

## Notes
- The notebook is derivation-first: each key equation is shown in rendered LaTeX and paired with executable Python in the same or next code cell.
- Keep all zirconium constants versioned with provenance (paper, calibration report, or metadata file) for reproducibility.
