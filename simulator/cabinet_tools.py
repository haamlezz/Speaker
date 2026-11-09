"""Cabinet physics: standing waves, panel resonances, port sizing, baffle step."""
import numpy as np
from speaker_model import C, RHO

# Typical material data (E in Pa, density kg/m^3, loss factor eta). Literature ranges.
MATERIALS = {
    "MDF 18mm":          dict(E=3.5e9, rho=750, nu=0.25, eta=0.025, h=0.018),
    "Birch ply 18mm":    dict(E=7.0e9, rho=680, nu=0.30, eta=0.015, h=0.018),
    "Particleboard 18mm":dict(E=2.5e9, rho=650, nu=0.25, eta=0.020, h=0.018),
    "Solid pine 18mm":   dict(E=8.0e9, rho=500, nu=0.35, eta=0.012, h=0.018),
}


def axial_modes(lx, ly, lz, fmax=1000):
    """Interior axial + tangential + oblique modes f = c/2 sqrt((nx/lx)^2+...)."""
    out = []
    for nx in range(0, 8):
        for ny in range(0, 8):
            for nz in range(0, 8):
                if nx == ny == nz == 0:
                    continue
                fr = C / 2 * np.sqrt((nx / lx) ** 2 + (ny / ly) ** 2 + (nz / lz) ** 2)
                if fr <= fmax:
                    out.append((round(fr, 1), (nx, ny, nz)))
    return sorted(out)


def panel_f11(a, b, mat, clamped=False):
    """First bending resonance of a rectangular plate (Kirchhoff).
    Simply supported: f = (pi/2) sqrt(D/(rho h)) (1/a^2 + 1/b^2); clamped edges ~1.8x higher (square)."""
    D = mat["E"] * mat["h"] ** 3 / (12 * (1 - mat["nu"] ** 2))
    f = (np.pi / 2) * np.sqrt(D / (mat["rho"] * mat["h"])) * (1 / a**2 + 1 / b**2)
    return f * (1.8 if clamped else 1.0)


def port_length(vb_l, fb, d, n=1):
    vb = vb_l / 1000
    sp = n * np.pi * (d / 2) ** 2
    return C**2 * sp / ((2 * np.pi * fb) ** 2 * vb) - 0.732 * d


def port_pipe_resonance(length_eff):
    """First organ-pipe (half-wave, open-open) resonance of the port tube."""
    return C / (2 * length_eff)


def baffle_step_f3(width):
    return 115.0 / width


def edge_diffraction_freq(dist_to_edge):
    """Frequency where edge re-radiation is half a wavelength late -> first dip region."""
    return C / (2 * dist_to_edge)
