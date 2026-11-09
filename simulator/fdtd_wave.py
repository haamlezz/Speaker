"""
2-D FDTD acoustic wave simulator (Yee staggered grid, linear acoustics).

    dp/dt  = -rho c^2 (dvx/dx + dvy/dy)
    dv/dt  = -(1/rho) grad p

The cabinet is a rigid solid (velocity forced to 0 on its faces). A driver is a
small soft source on the front baffle. A graded absorbing sponge at the domain edge
removes reflections. Used to compare baffle-edge shapes (diffraction) and to make
pictures of the wavefield.

2-D is a horizontal slice through an infinitely tall box, so the baffle step and
ripple show up a little stronger than in 3-D. Use it to compare shapes, not for
absolute numbers.
"""
import numpy as np

C, RHO = 343.0, 1.204


def cabinet_mask(nx, ny, dx, width, depth, radius, cx, cy, chamfer=False):
    """Boolean solid mask of a rectangular cabinet seen from above, front face at +y."""
    x = (np.arange(nx) - cx) * dx
    y = (np.arange(ny) - cy) * dx
    X, Y = np.meshgrid(x, y, indexing="ij")
    hw = width / 2
    inside = (np.abs(X) <= hw) & (Y <= 0) & (Y >= -depth)
    if radius > 0:
        # round/chamfer the two FRONT vertical edges only
        for sx in (-1, 1):
            ox, oy = sx * (hw - radius), -radius
            region = (sx * X > hw - radius) & (Y > -radius)
            if chamfer:
                cut = (sx * X - (hw - radius)) + (Y + radius) > radius
            else:
                cut = (X - ox) ** 2 + (Y - oy) ** 2 > radius**2
            inside &= ~(region & cut)
    return inside


def run(width=0.26, depth=0.32, radius=0.0, chamfer=False, src_offset=0.0, dx=0.005,
        size=3.6, mic_dist=1.0, t_end=0.010, snapshot_freq=None, snap_time=None, no_cab=False):
    nx = ny = int(size / dx)
    cx, cy = nx // 2, int(ny * 0.40)
    dt = 0.98 * dx / (C * np.sqrt(2))
    nt = int(t_end / dt)
    p = np.zeros((nx, ny))
    vx = np.zeros((nx + 1, ny))
    vy = np.zeros((nx, ny + 1))

    solid = np.zeros((nx, ny), bool) if no_cab else cabinet_mask(nx, ny, dx, width, depth, radius, cx, cy, chamfer)
    # velocity nodes touching solid are zeroed
    sx_mask = np.zeros((nx + 1, ny), bool)
    sx_mask[1:-1] = solid[1:] | solid[:-1]
    sy_mask = np.zeros((nx, ny + 1), bool)
    sy_mask[:, 1:-1] = solid[:, 1:] | solid[:, :-1]

    # sponge
    npml = int(0.3 / dx)
    prof = np.zeros(nx)
    ramp = (np.arange(npml)[::-1] / npml) ** 2 * 0.35
    prof[:npml] = ramp
    prof[-npml:] = ramp[::-1]
    sig = np.maximum(prof[:, None], prof[None, :])
    damp = 1 - sig

    sxi = cx + int(round(src_offset / dx))
    syi = cy + 1                       # first air cell in front of baffle
    mic = (cx, cy + int(mic_dist / dx))

    # source: differentiated Gaussian pulse (broadband to ~ 6 kHz) or tone burst
    t = np.arange(nt) * dt
    if snapshot_freq:
        f0 = snapshot_freq
        env = np.clip(t * f0 / 3, 0, 1)
        src = env * np.sin(2 * np.pi * f0 * t)
    else:
        tau, t0 = 1 / (np.pi * 5000), 6 / (np.pi * 5000)
        src = -(t - t0) / tau**2 * np.exp(-((t - t0) / tau) ** 2 / 2)
        src /= np.max(np.abs(src))

    k1 = RHO * C**2 * dt / dx
    k2 = dt / (RHO * dx)
    rec = np.zeros(nt)
    snap = None
    for n in range(nt):
        vx[1:-1] -= k2 * (p[1:] - p[:-1])
        vy[:, 1:-1] -= k2 * (p[:, 1:] - p[:, :-1])
        vx[sx_mask] = 0
        vy[sy_mask] = 0
        p -= k1 * ((vx[1:] - vx[:-1]) + (vy[:, 1:] - vy[:, :-1]))
        p[sxi, syi] += src[n]
        p *= damp
        p[solid] = 0
        rec[n] = p[mic]
        if snap_time and snap is None and t[n] >= snap_time:
            snap = p.copy()
    return dict(t=t, rec=rec, dt=dt, solid=solid, snap=snap, dx=dx,
                extent=[-cx * dx, (nx - cx) * dx, -cy * dx, (ny - cy) * dx])


def response(res, ref, fmin=150, fmax=4500):
    """Magnitude of cabinet response relative to the same source with no cabinet (dB)."""
    n = len(res["rec"]) * 4
    win = np.ones(len(res["rec"]))
    k = len(win) // 4
    win[-k:] = np.hanning(2 * k)[k:]          # taper the tail to suppress truncation ripple
    F = np.fft.rfftfreq(n, res["dt"])
    H = np.fft.rfft(res["rec"] * win, n) / (np.fft.rfft(ref["rec"] * win, n) + 1e-20)
    m = (F >= fmin) & (F <= fmax)
    return F[m], 20 * np.log10(np.abs(H[m]))
