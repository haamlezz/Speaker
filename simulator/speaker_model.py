"""
Lumped-parameter loudspeaker + enclosure simulator.

Model (electro-mechano-acoustic, Thiele 1961 / Small 1972-73):

    V = (Re + jwLe) I + Bl u                        (voice coil)
    Bl I = (Zms + Sd^2 Zbox) u                      (moving mass + box back-pressure)
    Zms  = Rms + jwMms + 1/(jwCms)
    Zbox = Zc || Ral || Zport                       (box compliance, leakage, port)
    Zc   = 1/(jwCab) + Rab                          (air spring + absorption loss)
    Zport= Rap + jwMap                              (port air plug)

Radiated volume velocity  U = Sd*u + Uport + Uleak
Far-field pressure         p = j w rho U / (2 pi r)    (half space, i.e. on a big baffle)
A baffle-step filter then turns that into a real box of finite width.
"""
import numpy as np

RHO = 1.204      # kg/m^3 air @20C
C = 343.0        # m/s
P_REF = 20e-6


class Driver:
    """Thiele/Small driver. Units: Hz, ohm, H, m^2, m^3(Vas), m(Xmax)."""

    def __init__(self, name, fs, re, le, qms, qes, vas_l, sd_cm2, xmax_mm, pe_w=100):
        self.name = name
        self.fs, self.re, self.le = fs, re, le
        self.qms, self.qes = qms, qes
        self.qts = qms * qes / (qms + qes)
        self.vas = vas_l / 1000.0
        self.sd = sd_cm2 / 1e4
        self.xmax = xmax_mm / 1000.0
        self.pe = pe_w
        ws = 2 * np.pi * fs
        self.cms = self.vas / (RHO * C**2 * self.sd**2)
        self.mms = 1 / (ws**2 * self.cms)
        self.rms = ws * self.mms / qms
        self.bl = np.sqrt(ws * self.mms * re / qes)

    def sensitivity_db(self):
        """Half-space reference efficiency -> dB SPL @1W/1m (Small)."""
        eta0 = (4 * np.pi**2 / C**3) * self.fs**3 * self.vas / self.qes
        return 112.1 + 10 * np.log10(eta0)

    def __repr__(self):
        return (f"{self.name}: Fs={self.fs}Hz Qts={self.qts:.3f} Vas={self.vas*1e3:.1f}L "
                f"Bl={self.bl:.2f}Tm Mms={self.mms*1e3:.1f}g Sens~{self.sensitivity_db():.1f}dB")


class Box:
    """Enclosure. kind='sealed' or 'vented'. vb in litres, fb in Hz, port diameter in m."""

    def __init__(self, kind, vb_l, fb=None, port_d=0.0762, n_ports=1, ql=7.0, qa=100.0, qp=60.0):
        self.kind = kind
        self.vb = vb_l / 1000.0
        self.fb = fb
        self.port_d = port_d
        self.n_ports = n_ports
        self.ql, self.qa, self.qp = ql, qa, qp

    @property
    def cab(self):
        return self.vb / (RHO * C**2)

    @property
    def sp(self):
        return self.n_ports * np.pi * (self.port_d / 2) ** 2

    @property
    def map(self):
        return 1 / ((2 * np.pi * self.fb) ** 2 * self.cab)

    def port_length(self):
        """Physical length of each port (end correction 0.732*d: one flanged + one free end)."""
        if self.kind != "vented":
            return 0.0
        l_eff = self.map * self.sp / RHO
        return l_eff - 0.732 * self.port_d


def simulate(drv, box, f=None, volts=2.83, r=1.0, baffle_width=None):
    """Return dict with SPL, impedance, excursion, port velocity, group delay."""
    if f is None:
        f = np.logspace(np.log10(10), np.log10(20000), 800)
    w = 2 * np.pi * f
    s = 1j * w

    zms = drv.rms + s * drv.mms + 1 / (s * drv.cms)
    # reference frequency for loss resistances
    wb = 2 * np.pi * (box.fb if box.kind == "vented" else drv.fs * np.sqrt(1 + drv.vas / box.vb))
    rab = 1 / (box.qa * wb * box.cab)
    zc = 1 / (s * box.cab) + rab
    ral = box.ql / (wb * box.cab)
    ybox = 1 / zc + 1 / ral
    if box.kind == "vented":
        rap = wb * box.map / box.qp
        zport = rap + s * box.map
        ybox = ybox + 1 / zport
    zbox = 1 / ybox

    ze_coil = drv.re + s * drv.le
    zmech_total = zms + drv.sd**2 * zbox
    # current & velocity
    i = volts / (ze_coil + drv.bl**2 / zmech_total)
    u = drv.bl * i / zmech_total
    p_box = -drv.sd * u * zbox
    u_leak = p_box / ral
    u_port = p_box / zport if box.kind == "vented" else 0 * u
    u_tot = drv.sd * u + u_port + u_leak

    p = s * RHO * u_tot / (2 * np.pi * r)
    if baffle_width:
        p = p * baffle_step(f, baffle_width)
    spl = 20 * np.log10(np.abs(p) / P_REF + 1e-30)

    zin = volts / i
    x_peak = np.abs(u / s) * np.sqrt(2)        # volts are RMS -> peak
    v_port_peak = (np.abs(u_port) / box.sp * np.sqrt(2)) if box.kind == "vented" else 0 * f
    phase = np.unwrap(np.angle(p))
    gd = -np.gradient(phase, w)
    return dict(f=f, spl=spl, zin=zin, x=x_peak, vport=v_port_peak, gd=gd, p=p)


def baffle_step(f, width):
    """First-order shelf: -6 dB (full-space) at LF -> 0 dB (half-space) at HF.
    Corner f3 ~ 115/W (W in metres), the widely used Olson/Linkwitz estimate."""
    f3 = 115.0 / width
    s = 1j * f / f3
    return (1 + s) / (2 + s) * 1.0  # LF -> 0.5 (-6 dB), HF -> 1


def f3_db(res, ref_band=(200, 600)):
    f, spl = res["f"], res["spl"]
    m = (f > ref_band[0]) & (f < ref_band[1])
    ref = np.mean(spl[m])
    below = np.where((spl < ref - 3) & (f < ref_band[0]))[0]
    return f[below[-1]] if len(below) else f[0], ref


def max_spl(drv, box, f=None, baffle_width=None, port_vmax=17.0):
    """Max SPL per frequency limited by Xmax, thermal power, and port velocity."""
    res = simulate(drv, box, f, volts=1.0, baffle_width=baffle_width)
    v_thermal = np.sqrt(drv.pe * drv.re)
    v_x = drv.xmax / np.maximum(res["x"], 1e-12)
    lim = np.minimum(v_thermal, v_x)
    if box.kind == "vented":
        v_p = port_vmax / np.maximum(res["vport"], 1e-12)
        lim = np.minimum(lim, v_p)
    return res["f"], res["spl"] + 20 * np.log10(lim), lim


def optimise_vented(drv, vb_range=(20, 60), fb_range=(22, 50), tol=1.0, f=None):
    """Brute-force search for the lowest F3 whose response stays within +/-tol dB
    from 1.6*F3 up to 300 Hz (flat: no hump and no sag). Returns (vb, fb, f3, dev)."""
    best = None
    for vb in np.arange(vb_range[0], vb_range[1] + 0.1, 1.0):
        for fb in np.arange(fb_range[0], fb_range[1] + 0.1, 0.5):
            res = simulate(drv, Box("vented", vb, fb), f)
            f3, ref = f3_db(res)
            m = (res["f"] > 1.6 * f3) & (res["f"] < 300)
            dev = np.max(np.abs(res["spl"][m] - ref))
            if dev > tol:
                continue
            if best is None or f3 < best[2] - 0.3 or (abs(f3 - best[2]) <= 0.3 and vb < best[0]):
                best = (vb, fb, f3, dev)
    return best
