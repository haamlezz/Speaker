# TMW-27 Floorstander

Research, simulators and build plans for a 3-way vented floor-standing loudspeaker
(tweeter, 4" midrange, 8" woofer) that covers about 31 Hz – 20 kHz.

**Open `web/index.html` in a browser.** It has the full build sheet: research notes,
a live box simulator, a live 2-D wave simulator, scale drawings, a cut list, a parts list,
the build order and the DSP tuning steps.

## Design at a glance

| | |
|---|---|
| Cabinet (W × D × H) | 270 × 340 × 1040 mm on a plinth with a 40 mm gap |
| Panels | 18 mm Baltic birch ply, 36 mm double front baffle, 25 mm front roundover |
| Woofer chamber | 45.9 L net, vented, tuned to 27 Hz, port Ø76 mm × 349 mm firing down into the plinth gap |
| Mid chamber | 15.7 L sealed, fully filled with wool or polyester |
| Bracing | Two window braces. Every panel bay resonates above 700 Hz |
| Crossover | Active DSP, LR4 at 350 Hz and 2600 Hz, baffle-step shelf, 20 Hz LR4 subsonic |
| Bass −3 dB | 27 Hz for the box alone, 31 Hz with the protective subsonic filter (anechoic) |

## Simulators (`simulator/`)

```
pip install numpy matplotlib
cd simulator && python3 run_design.py      # writes plots + summary.json to ../results
```

- `speaker_model.py` — Thiele/Small lumped electro-mechano-acoustic model (sealed and vented, with
  voice-coil inductance, leakage, absorption and port losses). Gives SPL, impedance, excursion,
  port air speed, group delay and maximum SPL, plus a box optimiser.
- `fdtd_wave.py` — 2-D finite-difference time-domain solver of the acoustic wave equation.
  Use it to compare baffle-edge shapes and driver positions (diffraction).
- `cabinet_tools.py` — interior standing waves, panel bending resonances (Kirchhoff plate),
  port length and pipe resonance, baffle-step frequency.
- `run_design.py` — runs every experiment behind the design.

## Key results (`results/`)

| Plot | Shows |
|---|---|
| `01_woofer_alignments.png` | Sealed vs vented boxes: response, impedance, excursion, group delay |
| `02_port_and_max_spl.png` | Port air speed for four diameters, maximum clean SPL |
| `03_fdtd_diffraction.png` | Baffle step and edge diffraction: sharp vs rounded vs chamfered, centred vs offset |
| `04_wavefield.png` | A 2 kHz wavefield around sharp and rounded cabinets |
| `05_system_response.png` | The full 3-way active sum |

The driver parameters are nominal values. Enter your actual drivers' datasheet values in the
web simulator (or in `run_design.py`) before cutting any wood.

## References

- R. H. Small, "Vented-Box Loudspeaker Systems", JAES 1973; N. Thiele, 1961/1971
- H. F. Olson, "Direct Radiator Loudspeaker Enclosures", 1951
- Salvatti, Devantier, Button, "Maximizing Performance from Loudspeaker Ports", AES
- Bezzola, "Optimal Bass Reflex Loudspeaker Port Design", COMSOL
- Harwood, "Factors in the design of loudspeaker cabinets"; Iverson, JAES 1973
