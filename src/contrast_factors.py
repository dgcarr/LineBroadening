"""Reflection-wise contrast factor helpers for hexagonal crystals.

All coefficients remain explicit function parameters so zirconium-specific
elastic/contrast constants can be supplied from external calibration.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np


@dataclass(frozen=True)
class HKL:
    h: int
    k: int
    l: int



def hkl_to_h2(h: int, k: int, l: int) -> float:
    """Invariant H^2 often used in hexagonal contrast-factor parameterization.

    H^2 = (4/3) * (h^2 + hk + k^2) / [(4/3)(h^2 + hk + k^2) + (a/c)^2 l^2]
    """

    basal = (4.0 / 3.0) * (h * h + h * k + k * k)
    # Ratio term deliberately left external in final contrast expression.
    return basal



def hexagonal_h2_parameter(h: int, k: int, l: int, c_over_a: float) -> float:
    """Dimensionless orientation parameter η_hkl for hexagonal reflections."""

    basal = (4.0 / 3.0) * (h * h + h * k + k * k)
    axial = (l * c_over_a) ** 2
    denom = basal + axial
    if denom == 0:
        raise ValueError("(h, k, l) = (0,0,0) is not a physical reflection.")
    return basal / denom



def contrast_factor_hex(h: int, k: int, l: int, c_over_a: float, c_bar: float, q: float) -> float:
    """Simple anisotropic contrast model.

    C_hkl = C̄ (1 - q * η_hkl), where η_hkl is the hexagonal orientation
    parameter. Parameters C̄ and q must be supplied from external data.
    """

    eta = hexagonal_h2_parameter(h, k, l, c_over_a)
    return c_bar * (1.0 - q * eta)



def reflection_contrast_factors(hkls: Iterable[HKL], c_over_a: float, c_bar: float, q: float) -> np.ndarray:
    """Vectorized wrapper returning C_hkl for many reflections."""

    return np.array([
        contrast_factor_hex(hkl.h, hkl.k, hkl.l, c_over_a=c_over_a, c_bar=c_bar, q=q)
        for hkl in hkls
    ])



def dislocation_broadening_term(rho: float, burgers: float, contrast: np.ndarray, k_factor: float = 1.0) -> np.ndarray:
    """Dimensionless strain-amplitude contribution from dislocation density.

    ε_hkl ∝ k * b * sqrt(ρ * C_hkl)
    """

    return k_factor * burgers * np.sqrt(rho * np.asarray(contrast))
