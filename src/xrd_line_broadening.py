"""Core helpers for XRD line broadening calculations.

The utilities in this module are intentionally material-agnostic and keep
material constants parameterized so that zirconium-specific values can be
injected from external data sources.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

import numpy as np


@dataclass(frozen=True)
class PeakWidth:
    """Stores common line-width metrics for one diffraction peak."""

    fwhm_rad: float
    integral_breadth_rad: float



def two_theta_to_q(two_theta_rad: np.ndarray, wavelength: float) -> np.ndarray:
    """Convert 2θ values in radians to scattering vector magnitude q.

    q = 4π sin(θ) / λ, with θ = 2θ / 2.
    """

    theta = 0.5 * np.asarray(two_theta_rad)
    return (4.0 * np.pi / wavelength) * np.sin(theta)



def q_to_two_theta(q: np.ndarray, wavelength: float) -> np.ndarray:
    """Inverse of :func:`two_theta_to_q` for physically valid q, λ."""

    q = np.asarray(q)
    arg = np.clip(q * wavelength / (4.0 * np.pi), -1.0, 1.0)
    theta = np.arcsin(arg)
    return 2.0 * theta



def caglioti_fwhm(theta_rad: np.ndarray, u: float, v: float, w: float) -> np.ndarray:
    """Instrumental FWHM model.

    Returns FWHM in radians using H^2 = U tan^2 θ + V tan θ + W.
    """

    theta = np.asarray(theta_rad)
    h2 = u * np.tan(theta) ** 2 + v * np.tan(theta) + w
    return np.sqrt(np.clip(h2, 0.0, None))



def scherrer_fwhm(theta_rad: np.ndarray, wavelength: float, domain_size: float, k: float = 0.9) -> np.ndarray:
    """Size broadening term in radians: β_size = K λ / (L cos θ)."""

    theta = np.asarray(theta_rad)
    return (k * wavelength) / (domain_size * np.cos(theta))



def microstrain_fwhm(theta_rad: np.ndarray, microstrain_rms: float) -> np.ndarray:
    """Isotropic RMS microstrain broadening in radians: β_strain = 4 ε tan θ."""

    theta = np.asarray(theta_rad)
    return 4.0 * microstrain_rms * np.tan(theta)



def combine_fwhm_gaussian(*components: np.ndarray) -> np.ndarray:
    """Quadrature combination for approximately Gaussian line-width terms."""

    arr = np.array([np.asarray(c) for c in components])
    return np.sqrt(np.sum(arr**2, axis=0))



def combine_fwhm_lorentzian(*components: np.ndarray) -> np.ndarray:
    """Linear combination for approximately Lorentzian line-width terms."""

    arr = np.array([np.asarray(c) for c in components])
    return np.sum(arr, axis=0)



def williamson_hall_x(theta_rad: np.ndarray, wavelength: float) -> np.ndarray:
    """x-axis helper for Williamson-Hall plots: 4 sin θ / λ."""

    theta = np.asarray(theta_rad)
    return 4.0 * np.sin(theta) / wavelength



def williamson_hall_y(fwhm_rad: np.ndarray, wavelength: float, theta_rad: np.ndarray) -> np.ndarray:
    """y-axis helper for Williamson-Hall plots: β cos θ / λ."""

    beta = np.asarray(fwhm_rad)
    theta = np.asarray(theta_rad)
    return beta * np.cos(theta) / wavelength



def integral_breadth(two_theta_rad: np.ndarray, intensity: np.ndarray) -> float:
    """Compute integral breadth β_int = area / peak_height in radians."""

    x = np.asarray(two_theta_rad)
    y = np.asarray(intensity)
    peak_height = np.max(y)
    if peak_height <= 0:
        raise ValueError("Peak height must be positive.")
    area = np.trapz(y, x)
    return area / peak_height


def wa_size_fourier_coefficient(fourier_length: np.ndarray, area_weighted_domain_size: float) -> np.ndarray:
    """Warren-Averbach size Fourier coefficient.

    Uses the common exponential approximation:
    A_S(L) = exp(-L / D_A),
    where D_A is an area-weighted coherent domain size.
    """

    L = np.asarray(fourier_length, dtype=float)
    return np.exp(-L / area_weighted_domain_size)


def wa_strain_fourier_coefficient(reciprocal_lattice: np.ndarray, mean_square_strain: np.ndarray) -> np.ndarray:
    """Warren-Averbach strain Fourier coefficient.

    A_D(L, g) = exp(-2π² g² <ε²(L)>)
    """

    g = np.asarray(reciprocal_lattice, dtype=float)
    eps2 = np.asarray(mean_square_strain, dtype=float)
    return np.exp(-2.0 * np.pi**2 * g**2 * eps2)


def wa_total_fourier_coefficient(
    fourier_length: np.ndarray,
    reciprocal_lattice: np.ndarray,
    area_weighted_domain_size: float,
    mean_square_strain: np.ndarray,
) -> np.ndarray:
    """Total Warren-Averbach Fourier coefficient from size/strain factorization.

    A(L, g) = A_S(L) * A_D(L, g)
    """

    return wa_size_fourier_coefficient(
        fourier_length=fourier_length,
        area_weighted_domain_size=area_weighted_domain_size,
    ) * wa_strain_fourier_coefficient(
        reciprocal_lattice=reciprocal_lattice,
        mean_square_strain=mean_square_strain,
    )


def wilkens_mean_square_strain_asymptotic(
    fourier_length: np.ndarray,
    rho: float,
    burgers: float,
    contrast_factor: np.ndarray,
    outer_cutoff_radius: float,
) -> np.ndarray:
    """Asymptotic Krivoglaz-Wilkens-type mean square strain.

    <ε²(L)> ≈ (ρ b² C / 4π) * L² * ln(Re / L)

    This form is a reduced asymptotic representation intended for transparent
    derivation workflows when full Wilkens integral kernels are not supplied.
    """

    L = np.asarray(fourier_length, dtype=float)
    C = np.asarray(contrast_factor, dtype=float)
    ratio = np.clip(outer_cutoff_radius / np.clip(L, 1e-30, None), 1.0, None)
    return (rho * burgers**2 * C / (4.0 * np.pi)) * (L**2) * np.log(ratio)



def normalized_weights(values: Iterable[float]) -> np.ndarray:
    """Normalize non-negative weights to unit sum."""

    w = np.asarray(list(values), dtype=float)
    if np.any(w < 0):
        raise ValueError("Weights must be non-negative.")
    s = np.sum(w)
    if s <= 0:
        raise ValueError("At least one weight must be positive.")
    return w / s



def weighted_sum(mapping: Mapping[str, np.ndarray], weights: Mapping[str, float]) -> np.ndarray:
    """Weighted sum of component arrays keyed by phase/population labels."""

    keys = list(mapping)
    w = normalized_weights([weights[k] for k in keys])
    out = np.zeros_like(np.asarray(mapping[keys[0]]), dtype=float)
    for key, wk in zip(keys, w):
        out = out + wk * np.asarray(mapping[key])
    return out
