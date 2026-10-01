"""Write the warrant diagram from Figure 1 of the paper as SVG, in light and dark variants.

Run from the repository root:

    python figures/make_warrant_diagram.py
"""

from pathlib import Path

OUT = Path(__file__).resolve().parent

FONT = "Georgia, 'Times New Roman', Times, serif"


def svg(ink: str) -> str:
    def box(x, y, w, h, lines, dashed=False, bold_first=False):
        dash = ' stroke-dasharray="6 4"' if dashed else ""
        rect = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" ry="5" fill="none" stroke="{ink}" stroke-width="1.3"{dash}/>'
        n = len(lines)
        lh = 17
        y0 = y + h / 2 - (n - 1) * lh / 2 + 5
        texts = []
        for i, line in enumerate(lines):
            weight = ' font-weight="bold"' if (bold_first and i < (2 if lines[0].startswith("Test 2") else 1)) else ""
            texts.append(f'<text x="{x + w / 2}" y="{y0 + i * lh}" text-anchor="middle"{weight}>{line}</text>')
        return rect + "".join(texts)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 335" width="760" height="335" font-family="{FONT}" font-size="15" fill="{ink}">',
        '<defs>',
        f'<marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="{ink}"/></marker>',
        '</defs>',
        # Data and claim
        box(50, 20, 210, 72, ["Item-level pass/fail", 'responses <tspan font-style="italic">Y</tspan><tspan font-style="italic" font-size="11" dy="4">ij</tspan><tspan dy="-4"> </tspan>', "on HarmBench"]),
        box(500, 14, 210, 84, ["A model with a", "higher score refuses", "harmful requests", "more consistently"]),
        f'<line x1="260" y1="56" x2="498" y2="56" stroke="{ink}" stroke-width="1.3" marker-end="url(#arrow)"/>',
        f'<text x="380" y="48" text-anchor="middle" font-style="italic" font-size="12">licenses</text>',
        # Warrant
        box(235, 128, 290, 62, ["Warrant", "A single <tspan font-style=\"italic\">harmful refusal</tspan> construct", "organizes the responses"], bold_first=True),
        f'<line x1="380" y1="128" x2="380" y2="58" stroke="{ink}" stroke-width="1.3" marker-end="url(#arrow)"/>',
        # Tests
        box(30, 232, 230, 72, ["Test 1: Dimensionality", "Does one latent dimension", "organize the responses?"], dashed=True, bold_first=True),
        box(500, 232, 230, 92, ["Test 2: Differential", "Item Functioning", "Do equally capable", "models from different", "developers respond alike?"], dashed=True, bold_first=True),
        f'<line x1="145" y1="232" x2="300" y2="192" stroke="{ink}" stroke-width="1.1" stroke-dasharray="5 4" marker-end="url(#arrow)"/>',
        f'<line x1="615" y1="232" x2="460" y2="192" stroke="{ink}" stroke-width="1.1" stroke-dasharray="5 4" marker-end="url(#arrow)"/>',
        '</svg>',
    ]
    return "\n".join(parts)


(OUT / "warrant_diagram.svg").write_text(svg("#1a1a1a"))
(OUT / "warrant_diagram_dark.svg").write_text(svg("#e6edf3"))
print("wrote warrant_diagram.svg and warrant_diagram_dark.svg")
