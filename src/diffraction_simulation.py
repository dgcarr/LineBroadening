"""Synthetic diffraction pattern builders for line-broadening studies."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from .xrd_line_broadening import combine_fwhm_gaussian


@dataclass(frozen=True)
class PeakSpec:
    two_theta0_rad: float
    intensity: float
    fwhm_rad: float


@dataclass(frozen=True)
class PopulationContribution:
    label: str
    weight: float
    domain_size: float
    microstrain: float



def gaussian_peak(two_theta_rad: np.ndarray, center_rad: float, fwhm_rad: float, amplitude: float) -> np.ndarray:
    """Gaussian peak profile with given center, FWHM, and amplitude."""

    sigma = fwhm_rad / (2.0 * np.sqrt(2.0 * np.log(2.0)))
    x = np.asarray(two_theta_rad)
    return amplitude * np.exp(-0.5 * ((x - center_rad) / sigma) ** 2)



def lorentzian_peak(two_theta_rad: np.ndarray, center_rad: float, fwhm_rad: float, amplitude: float) -> np.ndarray:
    """Lorentzian (Cauchy) peak profile."""

    gamma = 0.5 * fwhm_rad
    x = np.asarray(two_theta_rad)
    return amplitude * (gamma**2) / ((x - center_rad) ** 2 + gamma**2)



def pseudo_voigt_peak(
    two_theta_rad: np.ndarray,
    center_rad: float,
    fwhm_rad: float,
    amplitude: float,
    eta: float,
) -> np.ndarray:
    """Pseudo-Voigt peak = η L + (1-η) G."""

    eta = float(np.clip(eta, 0.0, 1.0))
    g = gaussian_peak(two_theta_rad, center_rad, fwhm_rad, amplitude)
    l = lorentzian_peak(two_theta_rad, center_rad, fwhm_rad, amplitude)
    return eta * l + (1.0 - eta) * g



def synthetic_pattern(two_theta_rad: np.ndarray, peaks: Iterable[PeakSpec], background: float = 0.0) -> np.ndarray:
    """Build synthetic intensity from many peaks and a flat background."""

    y = np.full_like(np.asarray(two_theta_rad), fill_value=background, dtype=float)
    for peak in peaks:
        y += gaussian_peak(two_theta_rad, peak.two_theta0_rad, peak.fwhm_rad, peak.intensity)
    return y



def two_population_ac_broadening(
    theta_rad: np.ndarray,
    instrument_fwhm_rad: np.ndarray,
    size_a: np.ndarray,
    strain_a: np.ndarray,
    size_c: np.ndarray,
    strain_c: np.ndarray,
    weight_a: float,
    weight_c: float,
) -> np.ndarray:
    """Mixture model for two populations with distinct a/c broadening channels."""

    if weight_a < 0 or weight_c < 0 or (weight_a + weight_c) == 0:
        raise ValueError("Population weights must be non-negative and not both zero.")

    wa = weight_a / (weight_a + weight_c)
    wc = weight_c / (weight_a + weight_c)

    fwhm_a = combine_fwhm_gaussian(instrument_fwhm_rad, size_a, strain_a)
    fwhm_c = combine_fwhm_gaussian(instrument_fwhm_rad, size_c, strain_c)

    return wa * fwhm_a + wc * fwhm_c



def build_population_peaks(
    centers_rad: np.ndarray,
    amplitudes: np.ndarray,
    fwhm_population_rad: np.ndarray,
) -> list[PeakSpec]:
    """Convenience constructor for PeakSpec lists from vector inputs."""

    centers = np.asarray(centers_rad)
    amps = np.asarray(amplitudes)
    widths = np.asarray(fwhm_population_rad)

    if not (centers.shape == amps.shape == widths.shape):
        raise ValueError("centers, amplitudes, and widths must share the same shape.")

    return [
        PeakSpec(two_theta0_rad=float(c), intensity=float(a), fwhm_rad=float(w))
        for c, a, w in zip(centers, amps, widths)
    ]
