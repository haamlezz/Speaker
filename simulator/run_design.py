"""Run every experiment and write plots to ../results. python3 run_design.py"""
import json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from speaker_model import Driver, Box, simulate, max_spl, f3_db, optimise_vented, baffle_step
from cabinet_tools import (MATERIALS, axial_modes, panel_f11, port_length,
                           port_pipe_resonance, baffle_step_f3, edge_diffraction_freq)
import fdtd_wave

OUT = os.path.join(os.path.dirname(__file__), "..", "results")
os.makedirs(OUT, exist_ok=True)
plt.rcParams.update({"figure.dpi": 130, "axes.grid": True, "grid.alpha": .3, "font.size": 9})
summary = {}

# ---------------------------------------------------------------- drivers
# Nominal datasheet-style values. ALWAYS re-check against the datasheet of the unit you buy.
WOOFER = Driver("8in woofer (Dayton RS225-8 class)", fs=28, re=7.2, le=0.7e-3, qms=2.45, qes=0.47,
                vas_l=42.5, sd_cm2=214, xmax_mm=7.3, pe_w=80)
summary["woofer"] = repr(WOOFER)
print(WOOFER)

# ---------------------------------------------------------------- 1. sealed vs vented
f = np.logspace(1, np.log10(2000), 600)
best = optimise_vented(WOOFER, vb_range=(25, 55), f=f)
vb_opt, fb_opt, f3_opt, dev = best
print("optimum vented:", best)
VB, FB, PORT_D = 46.0, 27.0, 0.0762    # chosen design (rounded, fits the cabinet)
designs = {
    "Sealed 30 L": Box("sealed", 30),
    "Sealed 46 L": Box("sealed", 46),
    f"Vented {VB:.0f} L @ {FB:.0f} Hz (chosen)": Box("vented", VB, FB, PORT_D),
    "Vented 25 L @ 40 Hz (too small)": Box("vented", 25, 40, PORT_D),
}
fig, ax = plt.subplots(2, 2, figsize=(10, 7))
for name, bx in designs.items():
    r = simulate(WOOFER, bx, f)
    f3, ref = f3_db(r)
    summary.setdefault("alignments", {})[name] = round(float(f3), 1)
    ax[0, 0].semilogx(f, r["spl"], label=f"{name}  F3={f3:.0f} Hz")
    ax[0, 1].semilogx(f, np.abs(r["zin"]), label=name)
    ax[1, 0].semilogx(f, r["x"] * 1000 * np.sqrt(60 * WOOFER.re) / 2.83, label=name)
    ax[1, 1].semilogx(f, r["gd"] * 1000, label=name)
ax[0, 0].set(title="Frequency response, 2.83 V / 1 m (half space)", ylabel="dB SPL", xlim=(10, 2000), ylim=(60, 95))
ax[0, 1].set(title="Electrical impedance", ylabel="ohm", xlim=(10, 2000))
ax[1, 0].axhline(WOOFER.xmax * 1000, color="r", ls="--", label="Xmax")
ax[1, 0].set(title="Cone excursion at 60 W", ylabel="mm peak", xlim=(10, 300), ylim=(0, 25))
ax[1, 1].set(title="Group delay", ylabel="ms", xlim=(10, 300), ylim=(0, 40))
for a in ax.flat:
    a.legend(fontsize=6.5); a.set_xlabel("Hz")
fig.tight_layout(); fig.savefig(f"{OUT}/01_woofer_alignments.png"); plt.close(fig)

# ---------------------------------------------------------------- 2. port size study
fig, ax = plt.subplots(1, 2, figsize=(10, 3.6))
port_rows = []
for d in (0.0508, 0.0635, 0.0762, 0.1016):
    bx = Box("vented", VB, FB, d)
    r = simulate(WOOFER, bx, f, volts=np.sqrt(60 * WOOFER.re))
    L = port_length(VB, FB, d)
    port_rows.append(dict(d_mm=round(d * 1000), length_cm=round(L * 100, 1),
                          vmax_60W=round(float(r["vport"].max()), 1),
                          pipe_res_hz=round(port_pipe_resonance(L + 0.732 * d))))
    ax[0].semilogx(f, r["vport"], label=f"Ø{d*1000:.0f} mm, L={L*100:.0f} cm")
ax[0].axhline(17, color="r", ls="--", label="~17 m/s noise limit (flared)")
ax[0].set(title=f"Port air speed at 60 W ({VB:.0f} L, fb={FB:.0f} Hz)", ylabel="m/s peak", xlim=(10, 200), xlabel="Hz")
ax[0].legend(fontsize=7)
fm, smax, lim = max_spl(WOOFER, Box("vented", VB, FB, PORT_D), f, baffle_width=0.27)
fs_, ss, _ = max_spl(WOOFER, Box("sealed", 46), f, baffle_width=0.27)
ax[1].semilogx(fm, smax, label="Vented 46 L (chosen)")
ax[1].semilogx(fs_, ss, label="Sealed 46 L")
ax[1].set(title="Max clean SPL @1 m (Xmax / power / port limited)", ylabel="dB", xlim=(15, 300), ylim=(70, 115), xlabel="Hz")
ax[1].legend(fontsize=7)
fig.tight_layout(); fig.savefig(f"{OUT}/02_port_and_max_spl.png"); plt.close(fig)
summary["ports"] = port_rows

# ---------------------------------------------------------------- 3. cabinet: modes & panels
W_IN, D_IN = 0.234, 0.286
H_WOOF = 0.68      # internal height of woofer chamber
modes = axial_modes(W_IN, D_IN, H_WOOF, 800)[:8]
summary["woofer_chamber_modes"] = modes
panels = {}
for k, m in MATERIALS.items():
    panels[k] = dict(side_unbraced=round(panel_f11(H_WOOF, D_IN, m)),
                     side_braced_3_bays=round(panel_f11(H_WOOF / 3, D_IN, m)),
                     baffle_double_36mm=round(panel_f11(H_WOOF / 3, W_IN, dict(m, h=0.036))))
summary["panel_first_resonance_hz"] = panels

# ---------------------------------------------------------------- 4. FDTD diffraction study
print("FDTD runs ...")
ref = fdtd_wave.run(no_cab=True)
cases = {
    "Sharp edges, 26 cm": dict(width=0.26, radius=0.0),
    "20 mm roundover, 26 cm": dict(width=0.26, radius=0.02),
    "40 mm roundover, 26 cm": dict(width=0.26, radius=0.04),
    "40 mm chamfer, 26 cm": dict(width=0.26, radius=0.04, chamfer=True),
    "Sharp, tweeter 4 cm off-centre": dict(width=0.26, radius=0.0, src_offset=0.04),
}
fig, ax = plt.subplots(figsize=(8, 4))
fd = {}
for name, kw in cases.items():
    r = fdtd_wave.run(**kw)
    F, H = fdtd_wave.response(r, ref)
    hi = (F > 1200)
    fd[name] = round(float(np.std(H[hi])), 2)
    ax.semilogx(F, H, label=f"{name}  (ripple σ>1.2k = {fd[name]} dB)")
ax.set(title="2-D FDTD: on-axis response of a cabinet vs. free source (shows baffle step + edge diffraction)",
       xlabel="Hz", ylabel="dB re free field", xlim=(150, 4500))
ax.legend(fontsize=7); fig.tight_layout(); fig.savefig(f"{OUT}/03_fdtd_diffraction.png"); plt.close(fig)
summary["fdtd_ripple_std_db"] = fd

# wavefield pictures
fig, ax = plt.subplots(1, 2, figsize=(10, 4.6))
for a, (nm, kw) in zip(ax, [("Sharp edges", dict(radius=0.0)), ("40 mm roundover", dict(radius=0.04))]):
    r = fdtd_wave.run(width=0.26, snapshot_freq=2000, snap_time=0.0040, t_end=0.0041, size=2.4, **kw)
    P = r["snap"].T
    v = np.percentile(np.abs(P), 99.5)
    ext = r["extent"]
    a.imshow(P, origin="lower", cmap="RdBu_r", vmin=-v, vmax=v, extent=ext)
    a.contour(r["solid"].T, [0.5], colors="k", extent=ext, linewidths=1)
    a.set(title=f"2 kHz wave, {nm}", xlim=(-0.8, 0.8), ylim=(-0.5, 1.0), xlabel="m", ylabel="m")
fig.tight_layout(); fig.savefig(f"{OUT}/04_wavefield.png"); plt.close(fig)

# ---------------------------------------------------------------- 5. full 3-way system (DSP, LR4)
def lr4(f, fc, kind):
    s = 1j * f / fc
    bw = 1 / (s**2 + np.sqrt(2) * s + 1)
    return (bw**2) if kind == "lp" else ((s**2 * bw) ** 2)

fx = np.logspace(1, np.log10(20000), 900)
wo = simulate(WOOFER, Box("vented", VB, FB, PORT_D), fx)["p"]          # half-space woofer
wo = wo / np.abs(wo[(fx > 150) & (fx < 250)]).mean()
def hp2(f, fc, q):
    s = 1j * f / fc
    return s**2 / (s**2 + s / q + 1)
mid = hp2(fx, 90, 0.7) / (1 + 1j * fx / 9000)        # 4" mid in sealed chamber, rolls off high
twt = hp2(fx, 750, 0.8) / (1 + 1j * fx / 40000)       # 1" dome, Fs ~750 Hz
FC1, FC2 = 350, 2600
BW = 0.27
bs = baffle_step(fx, BW)                             # what the real cabinet does to every driver
bsc = 1 / bs                                         # DSP shelf: +6 dB LF -> 0 dB HF (use ~+3-4 dB near a wall)
w_ = wo * lr4(fx, FC1, "lp") * bs
m_ = mid * lr4(fx, FC1, "hp") * lr4(fx, FC2, "lp") * bs
t_ = twt * lr4(fx, FC2, "hp") * bs
tot = (w_ + m_ + t_) * bsc
hpf = lr4(fx, 20, "hp")                               # LR4 subsonic filter: keeps cone within Xmax and port < 17 m/s at 60 W
fig, ax = plt.subplots(figsize=(9, 4))
for y, nm in [(w_ * bsc, "Woofer"), (m_ * bsc, "Mid"), (t_ * bsc, "Tweeter"), (tot * hpf, "Sum (with 20 Hz LR4 subsonic)")]:
    ax.semilogx(fx, 20 * np.log10(np.abs(y) + 1e-9), label=nm, lw=2 if nm.startswith("Sum") else 1)
ax.set(title=f"3-way active system: LR4 @ {FC1} Hz and {FC2} Hz, baffle-step comp., 27 cm baffle",
       xlabel="Hz", ylabel="dB (relative)", xlim=(15, 20000), ylim=(-30, 6))
ax.legend(fontsize=8); fig.tight_layout(); fig.savefig(f"{OUT}/05_system_response.png"); plt.close(fig)
tot_db = 20 * np.log10(np.abs(tot * hpf))
band = (fx > 40) & (fx < 18000)
summary["system"] = dict(xover=[FC1, FC2], ripple_40_18k_db=round(float(tot_db[band].max() - tot_db[band].min()), 2))
summary["chosen_box"] = dict(vb_l=VB, fb_hz=FB, port_d_mm=PORT_D * 1000,
                             port_len_cm=round(port_length(VB, FB, PORT_D) * 100, 1),
                             optimiser=dict(vb=float(vb_opt), fb=float(fb_opt), f3=round(float(f3_opt), 1)))
summary["baffle"] = dict(width_m=0.27, baffle_step_f3_hz=round(baffle_step_f3(0.27)),
                         tweeter_edge_dip_hz=round(edge_diffraction_freq(0.135)))
with open(f"{OUT}/summary.json", "w") as fh:
    json.dump(summary, fh, indent=2, default=str)
print(json.dumps(summary, indent=2, default=str))
