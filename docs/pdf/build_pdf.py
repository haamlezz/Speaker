"""Build docs/TMW-27_Build_Guide.pdf from the drawings in web/index.html. Run: python3 build_pdf.py"""
import re, base64, os, subprocess, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]
web = (ROOT / "web/index.html").read_text()
svgs = re.findall(r"<svg viewBox.*?</svg>", web, re.S)
front, side = svgs[0], svgs[1]
side = side.replace('id="dots"', 'id="dots"').replace('<text class="lbls" x="-8" y="-62">36 baffle</text>', '<text class="lbls" x="-8" y="-62">36 double baffle</text>')

def img(p):
    return "data:image/png;base64," + base64.b64encode((ROOT / p).read_bytes()).decode()

# ---------- plan section through a window brace ----------
plan = '''<svg viewBox="-110 -80 500 530" role="img" aria-label="Plan section through window brace">
 <defs><pattern id="dots2" width="14" height="14" patternUnits="userSpaceOnUse"><circle class="dotc" cx="4" cy="4" r="1.6"/></pattern></defs>
 <path class="pnw" d="M0 304 H270 V315 A25 25 0 0 1 245 340 H25 A25 25 0 0 1 0 315 Z"/>
 <line class="ol" x1="0" y1="322" x2="270" y2="322" style="stroke-width:1"/>
 <rect class="pnw" x="0" y="0" width="18" height="304"/><rect class="pnw" x="252" y="0" width="18" height="304"/>
 <rect class="pnw" x="18" y="0" width="234" height="18"/>
 <path class="pnw" fill-rule="evenodd" style="fill-opacity:.45" d="M18 18 H252 V304 H18 Z M50 61 V261 H220 V61 Z"/>
 <circle class="pn" cx="135" cy="134" r="41"/><circle class="drv" cx="135" cy="134" r="38"/>
 <line class="hid" x1="135" y1="80" x2="135" y2="188"/><line class="hid" x1="81" y1="134" x2="189" y2="134"/>
 <!-- dims -->
 <g class="dim">
  <line x1="0" y1="-40" x2="270" y2="-40"/><line x1="0" y1="-52" x2="0" y2="-28"/><line x1="270" y1="-52" x2="270" y2="-28"/>
  <line x1="-45" y1="0" x2="-45" y2="340"/><line x1="-57" y1="0" x2="-33" y2="0"/><line x1="-57" y1="340" x2="-33" y2="340"/>
  <line x1="50" y1="-12" x2="220" y2="-12"/><line x1="50" y1="-20" x2="50" y2="61"/><line x1="220" y1="-20" x2="220" y2="61"/>
  <line x1="300" y1="61" x2="300" y2="261"/><line x1="220" y1="61" x2="310" y2="61"/><line x1="220" y1="261" x2="310" y2="261"/>
  <line x1="340" y1="134" x2="340" y2="304"/><line x1="176" y1="134" x2="350" y2="134"/><line x1="270" y1="304" x2="350" y2="304"/>
  <line x1="18" y1="400" x2="135" y2="400"/><line x1="18" y1="390" x2="18" y2="410"/><line x1="135" y1="175" x2="135" y2="410"/>
 </g>
 <text class="dimt" x="135" y="-50" text-anchor="middle">270</text>
 <text class="dimt" transform="translate(-55 170) rotate(-90)" text-anchor="middle">340</text>
 <text class="dimt" x="135" y="-18" text-anchor="middle" style="font-size:18px">window 170</text>
 <text class="dimt" x="306" y="168" style="font-size:18px">200</text>
 <text class="dimt" x="346" y="226" style="font-size:18px">170</text>
 <text class="dimt" x="76" y="428" text-anchor="middle" style="font-size:18px">117</text>
 <text class="lbls" x="135" y="44" text-anchor="middle">back member 43</text>
 <text class="lbls" x="135" y="290" text-anchor="middle">front member 43</text>
 <text class="lbls" x="34" y="160" text-anchor="middle" transform="rotate(-90 34 160)">side 32</text>
 <text class="lbl" x="135" y="200" text-anchor="middle">port Ø76 ID</text>
 <text class="lbls" x="210" y="370" text-anchor="middle">FRONT · 25 mm roundover</text>
</svg>'''

plinth = '''<svg viewBox="-80 -70 470 500" role="img" aria-label="Plinth plan">
 <rect class="pnw" x="-15" y="-20" width="300" height="380"/>
 <rect class="hid" x="0" y="0" width="270" height="340"/>
 <rect class="pn" x="12" y="12" width="34" height="34"/><rect class="pn" x="224" y="12" width="34" height="34"/>
 <rect class="pn" x="12" y="294" width="34" height="34"/><rect class="pn" x="224" y="294" width="34" height="34"/>
 <circle class="hid" cx="135" cy="134" r="41"/>
 <g class="dim">
  <line x1="-15" y1="-45" x2="285" y2="-45"/><line x1="-15" y1="-55" x2="-15" y2="-35"/><line x1="285" y1="-55" x2="285" y2="-35"/>
  <line x1="-45" y1="-20" x2="-45" y2="360"/><line x1="-55" y1="-20" x2="-35" y2="-20"/><line x1="-55" y1="360" x2="-35" y2="360"/>
  <line x1="320" y1="0" x2="320" y2="134"/><line x1="276" y1="0" x2="330" y2="0"/><line x1="176" y1="134" x2="330" y2="134"/>
 </g>
 <text class="dimt" x="135" y="-53" text-anchor="middle">300</text>
 <text class="dimt" transform="translate(-55 170) rotate(-90)" text-anchor="middle">380</text>
 <text class="dimt" x="326" y="74" style="font-size:18px">134</text>
 <text class="lbls" x="135" y="210" text-anchor="middle">port above (open gap)</text>
 <text class="lbls" x="135" y="250" text-anchor="middle">dashed = cabinet footprint</text>
 <text class="lbls" x="52" y="72">← spacer 34×34×40 (×4)</text>
 <text class="lbls" x="135" y="395" text-anchor="middle">BACK at top · FRONT at bottom</text>
</svg>'''
# plinth: back at top means y=0 is back; port is 134 mm from the back outer face (340-206)

# ---------- sheet layout 2440 x 1220 ----------
parts = [  # x, y, w, h, label
 (0, 0, 1040, 270, "Baffle outer 270×1040"), (0, 274, 1040, 270, "Baffle inner 270×1040"),
 (0, 548, 1040, 304, "Side 304×1040"), (0, 856, 1040, 304, "Side 304×1040"),
 (1044, 0, 1040, 234, "Back 234×1040"),
 (1044, 238, 286, 234, "Top"), (1334, 238, 286, 234, "Bottom"), (1624, 238, 286, 234, "Divider"),
 (1044, 476, 286, 234, "Brace"), (1334, 476, 286, 234, "Brace"),
]
r = ['<svg viewBox="-40 -60 2520 1330" role="img" aria-label="Cutting layout on one 1220 by 2440 sheet">',
     '<rect x="0" y="0" width="2440" height="1220" class="sheetr"/>']
for x, y, w, h, t in parts:
    r.append(f'<rect class="pnw" x="{x}" y="{y}" width="{w}" height="{h}"/>')
    fs = 34 if w > 500 else 30
    r.append(f'<text class="lbl" style="font-size:{fs}px" x="{x+w/2}" y="{y+h/2+10}" text-anchor="middle">{t}</text>')
r.append('<text class="lbls" style="font-size:32px" x="1500" y="900" text-anchor="middle">offcut: spare for repairs or test pieces</text>')
r.append('<g class="dim"><line x1="0" y1="-25" x2="2440" y2="-25"/><line x1="0" y1="-38" x2="0" y2="-12"/><line x1="2440" y1="-38" x2="2440" y2="-12"/></g>')
r.append('<text class="dimt" style="font-size:34px" x="1220" y="-34" text-anchor="middle">2440 (face grain direction)</text>')
r.append('<text class="dimt" style="font-size:34px" x="-12" y="610" text-anchor="middle" transform="rotate(-90 -12 610)">1220</text>')
r.append('</svg>')
sheet = "\n".join(r)

css = '''
@page{size:A4;margin:14mm 14mm 16mm 14mm}
*{box-sizing:border-box}
:root{--ink:#1B2126;--muted:#56616A;--line:#C7CED1;--accent:#1D5BC9;--wood:#9A5D12;--fill:#EEF2F3;--sheet:#FFFFFF;--warn:#B4231B}
body{margin:0;font:10pt/1.5 Inter,"Liberation Sans",sans-serif;color:var(--ink);background:#fff}
h1,h2,h3{font-family:"Inter Display",Inter,sans-serif;margin:0;line-height:1.15}
h1{font-size:34pt;font-weight:700;letter-spacing:-.01em}
h2{font-size:17pt;font-weight:600}
h3{font-size:11.5pt;font-weight:600}
p{margin:0}
.page{page-break-after:always;display:flex;flex-direction:column;gap:5mm}
.page:last-child{page-break-after:auto}
.label{font:500 7.5pt "JetBrains Mono",monospace;letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}
.head{display:flex;align-items:baseline;gap:4mm;border-bottom:1.2pt solid var(--ink);padding-bottom:2mm}
.head .label{color:var(--accent)}
.box{border:0.8pt solid var(--line);padding:4mm}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:5mm}
table{border-collapse:collapse;width:100%;font-size:9pt}
th,td{text-align:left;padding:1.6mm 2mm;border-bottom:.6pt solid var(--line);vertical-align:top}
th{font:500 7pt "JetBrains Mono",monospace;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
td.n{font-family:"JetBrains Mono",monospace;white-space:nowrap}
.blank{display:inline-block;min-width:22mm;border-bottom:.8pt solid var(--ink)}
ul,ol{margin:0;padding-left:5mm;display:flex;flex-direction:column;gap:1.4mm}
ol.check{list-style:none;padding-left:0;counter-reset:s}
ol.check li{counter-increment:s;display:grid;grid-template-columns:7mm 7mm 1fr;gap:1mm;align-items:start;padding:1.6mm 0;border-bottom:.6pt solid var(--line)}
ol.check li::before{content:"";width:4mm;height:4mm;border:1pt solid var(--ink);margin-top:.6mm}
ol.check li span.k{font:600 9pt "JetBrains Mono",monospace;color:var(--accent)}
.note{border-left:2.4pt solid var(--wood);padding:1mm 0 1mm 3mm}
.note.warn{border-color:var(--warn)}
.titleblock{border:1.4pt solid var(--ink);display:grid;grid-template-columns:1fr 1fr 1fr 1fr}
.titleblock div{padding:2.5mm 3mm;border-right:.6pt solid var(--line);border-bottom:.6pt solid var(--line);display:flex;flex-direction:column;gap:.5mm}
.titleblock b{font:600 12pt "JetBrains Mono",monospace}
.drawing{border:.8pt solid var(--line);padding:3mm;background-image:linear-gradient(#EDF0F0 .5pt,transparent .5pt),linear-gradient(90deg,#EDF0F0 .5pt,transparent .5pt);background-size:5mm 5mm;display:flex;flex-direction:column;gap:2mm}
.drawing svg{width:100%;height:auto;display:block}
svg .pn{fill:var(--fill);stroke:var(--ink);stroke-width:2}
svg .pnw{fill:#E9D6BC;stroke:var(--ink);stroke-width:2}
svg .sheetr{fill:#fff;stroke:var(--ink);stroke-width:3;stroke-dasharray:14 8}
svg .ol{fill:none;stroke:var(--ink);stroke-width:2}
svg .hid{fill:none;stroke:var(--muted);stroke-width:1.5;stroke-dasharray:8 6}
svg .drv{fill:#fff;stroke:var(--ink);stroke-width:2}
svg .cone{fill:var(--fill);stroke:var(--ink);stroke-width:1.2}
svg .dim{stroke:var(--accent);stroke-width:1.4;fill:none}
svg .dimt{fill:var(--accent);font:600 22px "JetBrains Mono",monospace}
svg .lbl{fill:var(--ink);font:500 20px Inter,sans-serif;stroke:#fff;stroke-width:5px;paint-order:stroke;stroke-linejoin:round}
svg .lbls{fill:var(--muted);font:500 17px Inter,sans-serif;stroke:#fff;stroke-width:5px;paint-order:stroke;stroke-linejoin:round}
svg .air{stroke:var(--accent);stroke-width:2.5;fill:none}
svg .stuff{fill:url(#dots)}
svg .hatch{fill:url(#hatch)}
svg .dotc{fill:var(--muted)}
svg .hatchl{stroke:var(--muted);stroke-width:1.5}
img.plot{width:100%;border:.6pt solid var(--line)}
'''

html = f'''<!doctype html><html><head><meta charset="utf-8"><title>TMW-27 Floorstander Build Guide</title><style>{css}</style></head><body>

<!-- 1 COVER -->
<section class="page">
  <span class="label">Build guide · 3-way vented floorstander · rev A · one speaker shown, build a mirrored pair</span>
  <h1>TMW-27 Floorstander</h1>
  <p style="font-size:11.5pt;max-width:160mm">Follow this guide to build the cabinet: tweeter, 4-inch midrange and 8-inch woofer, with a separate sealed chamber for the midrange and a 46-litre vented chamber for the woofer. All dimensions are in millimetres. The drawings are to scale but not to a fixed print scale, so always work from the written numbers.</p>
  <div class="titleblock">
    <div><span class="label">Size W×D×H</span><b>270×340×1040</b></div>
    <div><span class="label">Panels</span><b>18 mm birch ply</b></div>
    <div><span class="label">Woofer chamber</span><b>45.9 L net</b></div>
    <div><span class="label">Mid chamber</span><b>15.7 L sealed</b></div>
    <div><span class="label">Port</span><b>Ø76 × 349</b></div>
    <div><span class="label">Port tuning</span><b>27 Hz</b></div>
    <div><span class="label">Bass −3 dB</span><b>31 Hz*</b></div>
    <div><span class="label">Crossovers</span><b>350 / 2600 Hz</b></div>
  </div>
  <p class="label" style="text-transform:none;letter-spacing:0">* With the 20 Hz protective filter, measured in free space. The box alone reaches 27 Hz, and a room usually adds bass below 60 Hz.</p>

  <div class="grid2">
    <div class="box" style="display:flex;flex-direction:column;gap:2mm">
      <h3>What is inside</h3>
      <table>
        <tr><th>Zone</th><th>From top (mm)</th><th>Contents</th></tr>
        <tr><td>Top panel</td><td class="n">0 – 18</td><td>Solid</td></tr>
        <tr><td>Mid chamber</td><td class="n">18 – 252</td><td>Tweeter, midrange, filled with wool</td></tr>
        <tr><td>Divider</td><td class="n">252 – 270</td><td>Airtight panel</td></tr>
        <tr><td>Woofer chamber</td><td class="n">270 – 1022</td><td>Woofer, 2 braces, port, wall lining</td></tr>
        <tr><td>Bottom panel</td><td class="n">1022 – 1040</td><td>Port exits here</td></tr>
        <tr><td>Gap + plinth</td><td class="n">1040 – 1105</td><td>40 mm gap, 25 mm plinth</td></tr>
      </table>
    </div>
    <div class="box" style="display:flex;flex-direction:column;gap:2mm">
      <h3>Before you cut</h3>
      <ul>
        <li>Buy the drivers first. Check their real cut-out diameter, flange size and depth against pages 2 and 3.</li>
        <li>Enter the woofer's real datasheet values in the box simulator (web/index.html). If it gives a different volume or port length, change the woofer chamber height or the port length to match.</li>
        <li>Build the second speaker as a mirror image: the tweeter offset goes toward the inner edge on both.</li>
        <li>Cut a test piece to check your saw and router settings before cutting the baffles.</li>
        <li>Wear eye and ear protection and use a dust mask. MDF and ply dust is harmful.</li>
      </ul>
    </div>
  </div>
  <div class="note warn"><b>Airtight matters.</b> A leak in the woofer chamber or the divider ruins the bass tuning. Seal every inside joint and every wire hole.</div>
  <div class="box" style="display:flex;flex-direction:column;gap:2mm">
    <h3>Contents</h3>
    <table>
      <tr><td class="n">2</td><td>Drawing A · Front view and driver positions</td><td class="n">6</td><td>Parts and materials</td></tr>
      <tr><td class="n">3</td><td>Drawing B · Side section, chamber heights</td><td class="n">7</td><td>Build steps (checklist)</td></tr>
      <tr><td class="n">4</td><td>Drawing C · Brace, port position, plinth</td><td class="n">8</td><td>Tuning and setup</td></tr>
      <tr><td class="n">5</td><td>Cut list and sheet layout</td><td class="n">9</td><td>Why it is designed this way</td></tr>
    </table>
  </div>
</section>

<!-- 2 FRONT -->
<section class="page">
  <div class="head"><span class="label">Drawing A</span><h2>Front view and driver positions</h2></div>
  <div style="display:grid;grid-template-columns:92mm 1fr;gap:5mm">
    <div class="drawing">{front}</div>
    <div style="display:flex;flex-direction:column;gap:4mm">
      <table>
        <tr><th>Driver</th><th>Centre from top</th><th>Across</th></tr>
        <tr><td>Tweeter</td><td class="n">80</td><td class="n">170 from left*</td></tr>
        <tr><td>Midrange</td><td class="n">195</td><td class="n">135 (centre)</td></tr>
        <tr><td>Woofer</td><td class="n">385</td><td class="n">135 (centre)</td></tr>
      </table>
      <p class="label" style="text-transform:none;letter-spacing:0">* Left speaker as seen from the front. On the mirrored speaker the tweeter is 100 from the left (35 mm off-centre toward the inner edge).</p>
      <h3>Write in your driver sizes</h3>
      <table>
        <tr><th>Driver</th><th>Cut-out Ø</th><th>Flange Ø</th><th>Flange depth</th></tr>
        <tr><td>Tweeter</td><td><span class="blank"></span></td><td><span class="blank"></span></td><td><span class="blank"></span></td></tr>
        <tr><td>Midrange</td><td><span class="blank"></span></td><td><span class="blank"></span></td><td><span class="blank"></span></td></tr>
        <tr><td>Woofer</td><td><span class="blank"></span></td><td><span class="blank"></span></td><td><span class="blank"></span></td></tr>
      </table>
      <div class="box" style="display:flex;flex-direction:column;gap:2mm">
        <h3>Baffle routing</h3>
        <ul>
          <li><b>Outer layer:</b> cut-out hole, plus a recess the size of the flange Ø and as deep as the flange, so each driver sits flush.</li>
          <li><b>Inner layer:</b> cut-out hole only, then chamfer its back edge at 45° for the woofer and midrange so air can move freely behind the cone.</li>
          <li>The tweeter only needs its cut-out through both layers.</li>
          <li>After gluing the two layers, rout a <b>25 mm roundover</b> on the two vertical front edges and the top front edge.</li>
          <li>Mount the drivers with M5 T-nuts and bolts, not wood screws.</li>
        </ul>
      </div>
      <div class="note">Driver spacing check: tweeter bottom edge to mid top edge ≈ 10 mm, mid bottom edge to woofer top edge ≈ 22 mm (with a 104 mm tweeter, 106 mm mid and 230 mm woofer flange). If your flanges are bigger, move the woofer down, not the tweeter.</div>
    </div>
  </div>
</section>

<!-- 3 SIDE -->
<section class="page">
  <div class="head"><span class="label">Drawing B</span><h2>Side section, chambers and port</h2></div>
  <div style="display:grid;grid-template-columns:112mm 1fr;gap:5mm">
    <div class="drawing">{side}</div>
    <div style="display:flex;flex-direction:column;gap:4mm">
      <table>
        <tr><th>Part</th><th>Height from top</th></tr>
        <tr><td>Top panel</td><td class="n">0 – 18</td></tr>
        <tr><td>Divider</td><td class="n">252 – 270</td></tr>
        <tr><td>Upper brace</td><td class="n">540 – 558</td></tr>
        <tr><td>Lower brace</td><td class="n">780 – 798</td></tr>
        <tr><td>Bottom panel</td><td class="n">1022 – 1040</td></tr>
        <tr><td>Port top end</td><td class="n">691</td></tr>
      </table>
      <div class="box" style="display:flex;flex-direction:column;gap:2mm">
        <h3>Inside dimensions</h3>
        <table>
          <tr><td>Width</td><td class="n">234</td></tr>
          <tr><td>Depth</td><td class="n">286</td></tr>
          <tr><td>Mid chamber height</td><td class="n">234</td></tr>
          <tr><td>Woofer chamber height</td><td class="n">752</td></tr>
        </table>
      </div>
      <div class="box" style="display:flex;flex-direction:column;gap:2mm">
        <h3>Port</h3>
        <ul>
          <li>Ø76 mm inside, flared tube. Total length 349 mm, measured from the underside of the bottom panel.</li>
          <li>Cut it 360 mm long and trim to tune (page 8).</li>
          <li>Keep at least 76 mm of open space around its top end.</li>
          <li>Round the hole on the underside of the bottom panel with about an 18 mm radius.</li>
        </ul>
      </div>
      <div class="box" style="display:flex;flex-direction:column;gap:2mm">
        <h3>Damping</h3>
        <ul>
          <li><b>Woofer chamber:</b> butyl or bitumen pads on the sides and back, then 25 mm felt on the sides, back and floor. Leave the middle open.</li>
          <li><b>Mid chamber:</b> fill it loosely with wool or polyester, about 3/4 full.</li>
        </ul>
      </div>
    </div>
  </div>
</section>

<!-- 4 PLAN + PLINTH -->
<section class="page">
  <div class="head"><span class="label">Drawing C</span><h2>Brace, port position and plinth</h2></div>
  <div class="grid2">
    <div class="drawing"><span class="label">C1 · Plan section through a window brace (looking down)</span>{plan}</div>
    <div class="drawing"><span class="label">C2 · Plinth, top view, spacer positions</span>{plinth}</div>
  </div>
  <div class="grid2">
    <div class="box" style="display:flex;flex-direction:column;gap:2mm">
      <h3>Window braces (×2)</h3>
      <ul>
        <li>Outer size 234 × 286, the same as the inside of the box.</li>
        <li>Window 170 wide × 200 deep, leaving 32 mm side members and 43 mm front and back members.</li>
        <li>Glue all four edges to the baffle, sides and back. The brace only stiffens the walls if it is glued on every side.</li>
        <li>The port tube passes through the lower brace window. Its centre is 135 mm from either outer side and 170 mm behind the inner face of the baffle (206 mm from the front of the speaker).</li>
      </ul>
    </div>
    <div class="box" style="display:flex;flex-direction:column;gap:2mm">
      <h3>Plinth and gap</h3>
      <ul>
        <li>Plinth 300 × 380 × 25 mm, overhanging the cabinet by 15 mm each side and 20 mm front and back.</li>
        <li>Four hardwood spacers, 34 × 34 × 40 mm, inset 12 mm from the cabinet corners. Glue or screw them to the cabinet and screw the plinth on.</li>
        <li>The 40 mm gap must stay open on all four sides, because the port breathes through it. Never stand the speaker on carpet without the plinth.</li>
        <li>Fit spikes or rubber feet under the plinth.</li>
      </ul>
    </div>
  </div>
</section>

<!-- 5 CUT LIST -->
<section class="page">
  <div class="head"><span class="label">Stage 1</span><h2>Cut list and sheet layout (one speaker)</h2></div>
  <table>
    <tr><th>#</th><th>Part</th><th>Qty</th><th>Size (mm)</th><th>Notes</th></tr>
    <tr><td class="n">1</td><td>Baffle, outer layer</td><td class="n">1</td><td class="n">270 × 1040 × 18</td><td>Holes and flange recesses, roundover after gluing</td></tr>
    <tr><td class="n">2</td><td>Baffle, inner layer</td><td class="n">1</td><td class="n">270 × 1040 × 18</td><td>Holes, chamfered on the back</td></tr>
    <tr><td class="n">3</td><td>Sides</td><td class="n">2</td><td class="n">304 × 1040 × 18</td><td>Glued behind the baffle</td></tr>
    <tr><td class="n">4</td><td>Back</td><td class="n">1</td><td class="n">234 × 1040 × 18</td><td>Between the sides. Terminal holes in the woofer chamber</td></tr>
    <tr><td class="n">5</td><td>Top, bottom, divider</td><td class="n">3</td><td class="n">234 × 286 × 18</td><td>The bottom has a Ø82 hole for the port (check your tube's outer Ø)</td></tr>
    <tr><td class="n">6</td><td>Window braces</td><td class="n">2</td><td class="n">234 × 286 × 18</td><td>170 × 200 window</td></tr>
    <tr><td class="n">7</td><td>Plinth</td><td class="n">1</td><td class="n">300 × 380 × 25</td><td>From a separate board</td></tr>
    <tr><td class="n">8</td><td>Spacers</td><td class="n">4</td><td class="n">34 × 34 × 40</td><td>Hardwood</td></tr>
    <tr><td class="n">9</td><td>Port tube</td><td class="n">1</td><td class="n">Ø76 ID × 360</td><td>Trim to 349</td></tr>
  </table>
  <div class="drawing"><span class="label">One 1220 × 2440 × 18 mm sheet per speaker · 4 mm saw kerf allowed between parts</span>{sheet}</div>
  <div class="note">Cut the long parts along the 2440 direction so the face grain runs vertically on the finished speaker. Check that the sheet is square first, then cut every panel of the same size at one fence setting so all matching panels come out identical.</div>
</section>

<!-- 6 PARTS -->
<section class="page">
  <div class="head"><span class="label">Stage 2</span><h2>Parts and materials (for the pair)</h2></div>
  <table>
    <tr><th>Item</th><th>Qty (pair)</th><th>Recommended</th><th>Alternatives / notes</th></tr>
    <tr><td>Plywood 18 mm</td><td class="n">2 sheets</td><td>Baltic birch, void-free, 1220×2440</td><td>MDF 18–19 mm on a budget. Seal the edges in humid rooms</td></tr>
    <tr><td>Board 25 mm</td><td class="n">2 pcs</td><td>300×380 ply or MDF</td><td>For the plinths</td></tr>
    <tr><td>Hardwood block</td><td class="n">8 pcs</td><td>34×34×40</td><td>Spacers</td></tr>
    <tr><td>Woofer 8"</td><td class="n">2</td><td>Dayton Audio RS225-8</td><td>SB Acoustics SB23 series, Scan-Speak 22W. Re-check the box size</td></tr>
    <tr><td>Midrange 4"</td><td class="n">2</td><td>Dayton Audio RS100-8</td><td>SB Acoustics SB12 midrange</td></tr>
    <tr><td>Tweeter 1"</td><td class="n">2</td><td>SB Acoustics SB26STAC-C000-4</td><td>Dayton Audio RST28F-4. Fs under 800 Hz</td></tr>
    <tr><td>Port tube</td><td class="n">2</td><td>Ø76 mm (3") flared, ≥ 360 long</td><td>PVC pipe with routed flares</td></tr>
    <tr><td>DSP + amplifier</td><td class="n">2 or 1</td><td>Hypex FusionAmp FA253, one per speaker</td><td>Dayton DSP-408 plus a 6-channel class-D amp, or ADAU1701 4-ch DSP amp boards</td></tr>
    <tr><td>Measurement mic</td><td class="n">1</td><td>miniDSP UMIK-1 with REW (free)</td><td>Dayton DATS V3 for impedance (optional)</td></tr>
    <tr><td>Terminals</td><td class="n">6 pairs</td><td>Binding posts, or 1 Speakon each</td><td>3 pairs per speaker for active drive</td></tr>
    <tr><td>Wire</td><td class="n">~6 m</td><td>1.5 mm² (16 AWG) copper</td><td>Label each pair</td></tr>
    <tr><td>Damping pads</td><td class="n">~1.2 m²</td><td>Butyl or bitumen, 2–3 mm, self-adhesive</td><td>On the woofer chamber sides and back</td></tr>
    <tr><td>Felt lining</td><td class="n">~1.6 m²</td><td>25 mm polyester or wool felt</td><td>Woofer chamber walls</td></tr>
    <tr><td>Fill</td><td class="n">~0.5 kg</td><td>Sheep's wool or polyester fibre</td><td>Mid chambers</td></tr>
    <tr><td>Fixings</td><td class="n">~40</td><td>M5 T-nuts and hex bolts</td><td>Count your driver holes</td></tr>
    <tr><td>Glue and sealant</td><td class="n">—</td><td>PVA (Titebond II/III), acrylic sealant, hot glue</td><td>Gasket tape under every driver</td></tr>
    <tr><td>Tools</td><td class="n">—</td><td>Table or track saw, router + circle jig, 25 mm and 18 mm roundover bits, clamps</td><td>Many timber shops will cut panels to size for you</td></tr>
  </table>
</section>

<!-- 7 BUILD -->
<section class="page">
  <div class="head"><span class="label">Stage 3</span><h2>Build steps</h2></div>
  <ol class="check">
    <li><span class="k">01</span><span>Cut all panels (page 5). Label each one and mark which speaker it belongs to, left or right.</span></li>
    <li><span class="k">02</span><span>Clamp the two baffle layers together. Drill pilot holes at the driver centres: 80, 195 and 385 mm from the top, with the tweeter 35 mm off-centre (mirrored on the second speaker).</span></li>
    <li><span class="k">03</span><span>Rout the cut-outs through both layers with the circle jig. Rout the flange recesses in the outer layer only.</span></li>
    <li><span class="k">04</span><span>Chamfer the back of the woofer and mid holes 45° in the inner layer. Fit the T-nuts from the back.</span></li>
    <li><span class="k">05</span><span>Glue the two baffle layers together (spread glue thinly and evenly). Clamp flat and leave overnight.</span></li>
    <li><span class="k">06</span><span>Cut the windows in the two braces and the port hole in the bottom panel. Round the underside of the port hole.</span></li>
    <li><span class="k">07</span><span>Glue one side to the baffle, square it up, then glue in the top, divider, braces and bottom at the heights on page 3. Then the second side.</span></li>
    <li><span class="k">08</span><span>Glue the port tube through the bottom panel and the lower brace window. Its top end should be 349 mm above the underside of the bottom panel, or longer for now.</span></li>
    <li><span class="k">09</span><span>Drill the terminal holes in the back panel (woofer chamber, about 150 mm above the bottom) and a wire hole in the divider.</span></li>
    <li><span class="k">10</span><span>Glue on the back. Once dry, run sealant along every inside joint you can reach through the driver holes, especially around the divider.</span></li>
    <li><span class="k">11</span><span>Rout the 25 mm roundover on the front edges. Sand, then finish (veneer, oil or paint). Mask the driver recesses.</span></li>
    <li><span class="k">12</span><span>Fit the damping pads and the 25 mm felt in the woofer chamber. Keep the area above the port clear.</span></li>
    <li><span class="k">13</span><span>Run the wires: woofer, mid and tweeter pairs to the terminals. Seal the divider hole and the terminal holes with hot glue.</span></li>
    <li><span class="k">14</span><span>Fill the mid chamber with wool. Put gasket tape on each driver flange and mount the drivers with bolts. Tighten evenly in a star pattern, finger-tight plus a quarter turn.</span></li>
    <li><span class="k">15</span><span>Leak test: play a 20–30 Hz tone at low level and listen or feel around the joints, terminals and drivers. Air should only come out of the port.</span></li>
    <li><span class="k">16</span><span>Fix the spacers and the plinth. Check that the 40 mm gap is open all round.</span></li>
  </ol>
</section>

<!-- 8 TUNING -->
<section class="page">
  <div class="head"><span class="label">Stage 4</span><h2>Tuning and setup</h2></div>
  <table>
    <tr><th>DSP channel</th><th>Filters</th><th>Start gain</th></tr>
    <tr><td>Woofer</td><td>High-pass 20 Hz LR 24 dB/oct (protection) · low-pass 350 Hz LR 24 dB/oct · low shelf +3 to +6 dB at ~425 Hz (baffle step)</td><td class="n">0 dB</td></tr>
    <tr><td>Midrange</td><td>High-pass 350 Hz LR 24 dB/oct · low-pass 2600 Hz LR 24 dB/oct · same low shelf</td><td class="n">0 dB</td></tr>
    <tr><td>Tweeter</td><td>High-pass 2600 Hz LR 24 dB/oct</td><td class="n">−5 dB</td></tr>
    <tr><td>All</td><td>All drivers in the same polarity. Measure the delays (tweeter usually 0.1–0.3 ms)</td><td class="n">—</td></tr>
  </table>
  <ol class="check">
    <li><span class="k">T1</span><span><b>Check the port tuning before any other step.</b> Measure the woofer's impedance. The dip between the two bass peaks should be at <b>27 Hz</b>. If it is higher, the port is too short, so fit a longer tube. If it is lower, trim 5 mm at a time. Write the result here: <span class="blank"></span> Hz</span></li>
    <li><span class="k">T2</span><span>Check the polarity of each driver with a 1.5 V battery: the cone moves forward when + is on the red terminal.</span></li>
    <li><span class="k">T3</span><span>Put the mic 1 m away at tweeter height. Measure each driver alone and set the gains so all three bands are level.</span></li>
    <li><span class="k">T4</span><span>Use REW's impulse alignment to set the mid and tweeter delays. Check for a smooth sum through 350 Hz and 2600 Hz, with no dip.</span></li>
    <li><span class="k">T5</span><span>Set the baffle-step shelf: +6 dB far from walls, +3 to +4 dB if the speakers stand 30–60 cm from the back wall.</span></li>
    <li><span class="k">T6</span><span>At your listening seat, only cut room peaks below 300 Hz. Don't boost dips, and leave the treble alone.</span></li>
    <li><span class="k">T7</span><span>Place the speakers 50–80 cm from the back wall in an equilateral triangle with your seat, toed in toward you, tweeters near ear height (≈ 1025 mm with the plinth).</span></li>
  </ol>
  <div class="note warn">Never run the woofer without the 20 Hz protection filter. Below the port tuning, the cone is no longer held back by the air in the box, and the simulation shows it passing its 7.3 mm limit at 60 W.</div>
</section>

<!-- 9 WHY -->
<section class="page">
  <div class="head"><span class="label">Background</span><h2>Why it is designed this way</h2></div>
  <div class="grid2">
    <div style="display:flex;flex-direction:column;gap:2mm"><img class="plot" src="{img('results/01_woofer_alignments.png')}"><p class="label" style="text-transform:none;letter-spacing:0">Sealed boxes stop at 54 Hz. The vented 46 L box reaches 27 Hz without a hump.</p></div>
    <div style="display:flex;flex-direction:column;gap:2mm"><img class="plot" src="{img('results/02_port_and_max_spl.png')}"><p class="label" style="text-transform:none;letter-spacing:0">Smaller ports blow air too fast and chuff. Ø76 mm is the largest that still fits in the box.</p></div>
    <div style="display:flex;flex-direction:column;gap:2mm"><img class="plot" src="{img('results/03_fdtd_diffraction.png')}"><p class="label" style="text-transform:none;letter-spacing:0">Wave simulation: rounded edges and an off-centre tweeter halve the edge-diffraction ripple.</p></div>
    <div style="display:flex;flex-direction:column;gap:2mm"><img class="plot" src="{img('results/05_system_response.png')}"><p class="label" style="text-transform:none;letter-spacing:0">The full active 3-way system after DSP correction, flat within about ±0.6 dB.</p></div>
  </div>
  <p style="font-size:8.5pt;color:var(--muted)">Based on Thiele (1961) and Small (1973) for vented boxes, Olson (1951) for cabinet edge diffraction, Harwood and Iverson for panel resonance, and Salvatti/Devantier/Button and Bezzola for port design. The simulation code is in the repository under simulator/. Driver values are nominal, so measure your finished speakers.</p>
</section>
</body></html>'''
(pathlib.Path(__file__).parent / "guide.html").write_text(html)
print("html written")
