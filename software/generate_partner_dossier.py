#!/usr/bin/env python3
"""Build the public SCILLA PASSIVE partner-validation dossier.

The dossier is intentionally generated from declared constants that are also
present in the corrected-model audit. It is a decision document, not a new
scientific result.
"""

from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "SCILLA_PASSIVE_PARTNER_VALIDATION_DOSSIER_2026-09-02.pdf"

W, H = A4
M = 18 * mm
CONTENT_W = W - 2 * M

INK = colors.HexColor("#102C3A")
MUTED = colors.HexColor("#55707C")
LIGHT = colors.HexColor("#EAF2F4")
PAPER = colors.HexColor("#F7F8F6")
TEAL = colors.HexColor("#008C95")
TEAL_DARK = colors.HexColor("#006B73")
AMBER = colors.HexColor("#DC9318")
RED = colors.HexColor("#B44646")
WHITE = colors.white
RULE = colors.HexColor("#C8D5D9")


def register_fonts() -> None:
    regular = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    bold = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
    serif = Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf")
    serif_bold = Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf")
    if all(p.exists() for p in (regular, bold, serif, serif_bold)):
        pdfmetrics.registerFont(TTFont("DV Sans", str(regular)))
        pdfmetrics.registerFont(TTFont("DV Sans Bold", str(bold)))
        pdfmetrics.registerFont(TTFont("DV Serif", str(serif)))
        pdfmetrics.registerFont(TTFont("DV Serif Bold", str(serif_bold)))
    else:
        pdfmetrics.registerFont(TTFont("DV Sans", str(regular)))


SANS = "DV Sans"
SANS_B = "DV Sans Bold"
SERIF = "DV Serif"
SERIF_B = "DV Serif Bold"


def draw_para(c: canvas.Canvas, text: str, x: float, y_top: float, width: float,
              size: float = 9.0, leading: float | None = None,
              color=INK, font: str = SANS, bold: bool = False,
              space_after: float = 0) -> float:
    """Draw a paragraph from its top edge and return the next y coordinate."""
    leading = leading or size * 1.38
    style = ParagraphStyle(
        "inline",
        fontName=SANS_B if bold else font,
        fontSize=size,
        leading=leading,
        textColor=color,
        alignment=TA_LEFT,
        allowWidows=0,
        allowOrphans=0,
    )
    p = Paragraph(text, style)
    _, ph = p.wrap(width, H)
    p.drawOn(c, x, y_top - ph)
    return y_top - ph - space_after


def pill(c: canvas.Canvas, text: str, x: float, y: float, fill=TEAL,
         color=WHITE, font_size: float = 7.5, pad_x: float = 7) -> float:
    tw = pdfmetrics.stringWidth(text, SANS_B, font_size)
    pw = tw + 2 * pad_x
    c.setFillColor(fill)
    c.roundRect(x, y - 4, pw, 15, 7.5, fill=1, stroke=0)
    c.setFillColor(color)
    c.setFont(SANS_B, font_size)
    c.drawString(x + pad_x, y, text)
    return pw


def section_label(c: canvas.Canvas, text: str, y: float) -> None:
    c.setFillColor(TEAL)
    c.setFont(SANS_B, 8)
    c.drawString(M, y, text.upper())
    c.setStrokeColor(TEAL)
    c.setLineWidth(1.4)
    c.line(M, y - 5, M + 23, y - 5)


def page_header(c: canvas.Canvas, page_no: int, title: str) -> None:
    c.setFillColor(PAPER)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(MUTED)
    c.setFont(SANS_B, 7.3)
    c.drawString(M, H - 11 * mm, "SCILLA PASSIVE")
    c.setFont(SANS, 7.3)
    c.drawRightString(W - M, H - 11 * mm, title)
    c.setStrokeColor(RULE)
    c.setLineWidth(0.6)
    c.line(M, H - 14 * mm, W - M, H - 14 * mm)
    c.setFillColor(MUTED)
    c.setFont(SANS, 6.8)
    c.drawString(M, 10 * mm, "DOI 10.5281/zenodo.22229086")
    c.drawRightString(W - M, 10 * mm, f"{page_no:02d}")


def metric_card(c: canvas.Canvas, x: float, y_top: float, w: float, h: float,
                number: str, label: str, accent=TEAL, note: str | None = None) -> None:
    c.setFillColor(WHITE)
    c.setStrokeColor(RULE)
    c.setLineWidth(0.7)
    c.roundRect(x, y_top - h, w, h, 8, fill=1, stroke=1)
    c.setFillColor(accent)
    c.roundRect(x, y_top - h, 4, h, 2, fill=1, stroke=0)
    c.setFont(SERIF_B, 22)
    c.drawString(x + 14, y_top - 29, number)
    draw_para(c, label, x + 14, y_top - 38, w - 26, size=7.7, leading=10,
              color=MUTED, bold=True)
    if note:
        draw_para(c, note, x + 14, y_top - h + 25, w - 26, size=6.8,
                  leading=8.4, color=MUTED)


def footer_note(c: canvas.Canvas, text: str, y: float) -> None:
    c.setFillColor(LIGHT)
    c.roundRect(M, y - 24, CONTENT_W, 32, 6, fill=1, stroke=0)
    draw_para(c, text, M + 10, y, CONTENT_W - 20, size=7.1, leading=9,
              color=INK)


def cover(c: canvas.Canvas) -> None:
    c.setFillColor(PAPER)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(TEAL)
    c.rect(0, H - 9, W, 9, fill=1, stroke=0)
    y = H - 26 * mm
    pill(c, "PARTNER VALIDATION DOSSIER", M, y, fill=INK)
    y -= 26
    c.setFillColor(INK)
    c.setFont(SERIF_B, 31)
    c.drawString(M, y, "A second observation")
    c.drawString(M, y - 39, "worth measuring")
    y -= 73
    y = draw_para(
        c,
        "SCILLA PASSIVE asks a narrow industrial question: can an existing maritime "
        "track use one uncertainty-bearing observation derived from non-cooperative "
        "merchant-radar illumination?",
        M, y, CONTENT_W * 0.76, size=12.2, leading=17.5, color=INK, font=SERIF,
    )
    y -= 12
    c.setStrokeColor(TEAL)
    c.setLineWidth(3)
    c.line(M, y, M + 42, y)
    y -= 19
    y = draw_para(
        c,
        "The corrected process-model audit preserves the architecture result across "
        "all 81 frozen stress gates. The next claim cannot come from another simulation. "
        "It must come from a partner-controlled capture or replay.",
        M, y, CONTENT_W * 0.78, size=9.2, leading=13.2, color=MUTED,
    )

    card_y = 420
    gap = 9
    cw = (CONTENT_W - 2 * gap) / 3
    metric_card(c, M, card_y, cw, 92, "81", "stress gates rerun", TEAL,
                "No architecture-gate reversal after process correction.")
    metric_card(c, M + cw + gap, card_y, cw, 92, "94.4%", "physics cells favourable", TEAL,
                "51 of 54 simulated cells beat propagation only.")
    metric_card(c, M + 2 * (cw + gap), card_y, cw, 92, "49.0%", "EIG beats shortest pulse", AMBER,
                "No robust optimizer advantage is claimed.")

    c.setFillColor(INK)
    c.roundRect(M, 171, CONTENT_W, 104, 10, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont(SANS_B, 8)
    c.drawString(M + 16, 251, "THE PARTNER ASK")
    c.setFont(SERIF_B, 16)
    c.drawString(M + 16, 225, "Run one bounded falsification test.")
    draw_para(
        c,
        "Use partner-owned RF hardware or frozen maritime data. Preserve the existing "
        "baseline. Predeclare the gates. Stop if the observation is not repeatable, "
        "integrity-safe or economically useful.",
        M + 16, 210, CONTENT_W - 32, size=8.5, leading=11.8, color=WHITE,
    )
    c.setFillColor(MUTED)
    c.setFont(SANS, 7.2)
    c.drawString(M, 119, "Prepared 2 September 2026 · Michele Giletto · michele.giletto@gmail.com")
    c.drawString(M, 105, "Public evidence: github.com/michelegiletto-beep/scilla-passive-evidence")
    c.drawString(M, 91, "Scientific record: doi.org/10.5281/zenodo.22229086")
    c.setFont(SANS_B, 7)
    c.drawRightString(W - M, 25, "DECISION DOCUMENT · SIMULATION EVIDENCE · NO MEASURED RF CLAIM")


def evidence_page(c: canvas.Canvas) -> None:
    page_header(c, 2, "What survived the correction")
    section_label(c, "Evidence audit", H - 29 * mm)
    c.setFillColor(INK)
    c.setFont(SERIF_B, 22)
    c.drawString(M, H - 43 * mm, "The architecture signal survived.")
    y = draw_para(
        c,
        "The immutable 1.0.0 release contained a partition-dependent process-noise "
        "formulation. Maintained main discloses it, implements a continuous-white-noise-"
        "acceleration candidate, and reruns the complete evidence ladder.",
        M, H - 51 * mm, CONTENT_W, size=8.6, leading=12, color=MUTED,
    )

    c.setFillColor(WHITE)
    c.setStrokeColor(RULE)
    c.roundRect(M, y - 188, CONTENT_W, 174, 8, fill=1, stroke=1)
    c.setFont(SANS_B, 8)
    c.setFillColor(INK)
    c.drawString(M + 14, y - 30, "MEDIAN FINAL POSITION ERROR · 300 PAIRED SIMULATED WORLDS")

    policies = [
        ("Highest SNR", 24.94, MUTED),
        ("Random donor", 21.96, colors.HexColor("#6D8790")),
        ("Shortest pulse", 19.46, AMBER),
        ("Metrology EIG", 19.21, TEAL),
    ]
    chart_x = M + 132
    chart_w = CONTENT_W - 166
    chart_top = y - 56
    scale = chart_w / 30.0
    c.setFont(SANS, 7.2)
    for i, (name, val, col) in enumerate(policies):
        yy = chart_top - i * 27
        c.setFillColor(INK)
        c.drawRightString(chart_x - 9, yy + 3, name)
        c.setFillColor(LIGHT)
        c.roundRect(chart_x, yy - 3, chart_w, 10, 5, fill=1, stroke=0)
        c.setFillColor(col)
        c.roundRect(chart_x, yy - 3, val * scale, 10, 5, fill=1, stroke=0)
        c.setFillColor(INK)
        c.setFont(SANS_B, 7.2)
        c.drawString(chart_x + val * scale + 5, yy + 1, f"{val:.2f} m")
        c.setFont(SANS, 7.2)

    c.setFillColor(INK)
    c.roundRect(M + 14, y - 174, CONTENT_W - 28, 34, 5, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont(SANS_B, 8.3)
    c.drawString(M + 25, y - 157, "Propagation only")
    c.setFont(SERIF_B, 15)
    c.drawRightString(W - M - 25, y - 160, "351.50 m")

    y2 = y - 210
    gap = 9
    cw = (CONTENT_W - 2 * gap) / 3
    metric_card(c, M, y2, cw, 86, "51 of 54", "physics gates favourable", TEAL,
                "Zero gate changes versus the legacy model.")
    metric_card(c, M + cw + gap, y2, cw, 86, "27 of 27", "integrity gates favourable", TEAL,
                "Zero gate changes versus the legacy model.")
    metric_card(c, M + 2 * (cw + gap), y2, cw, 86, "0.0 m", "paired median EIG difference", AMBER,
                "The interval spans zero; optimizer moat not supported.")

    y3 = y2 - 114
    c.setFillColor(INK)
    c.setFont(SERIF_B, 15)
    c.drawString(M, y3, "Decision boundary")
    left_w = (CONTENT_W - 12) / 2
    c.setFillColor(colors.HexColor("#E4F3F2"))
    c.roundRect(M, y3 - 103, left_w, 87, 7, fill=1, stroke=0)
    c.setFillColor(TEAL_DARK)
    c.setFont(SANS_B, 8)
    c.drawString(M + 12, y3 - 37, "SUPPORTED IN DECLARED SIMULATION")
    draw_para(c, "A valid second observation can sharply reduce uncertainty in the "
              "declared cue-driven fixtures.", M + 12, y3 - 47, left_w - 24,
              size=8.1, leading=11, color=INK)
    c.setFillColor(colors.HexColor("#F7EEDB"))
    c.roundRect(M + left_w + 12, y3 - 103, left_w, 87, 7, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#8B5B00"))
    c.setFont(SANS_B, 8)
    c.drawString(M + left_w + 24, y3 - 37, "NOT YET DEMONSTRATED")
    draw_para(c, "RF feasibility, sea clutter, association integrity, operational "
              "value and integration economics.", M + left_w + 24, y3 - 47,
              left_w - 24, size=8.1, leading=11, color=INK)
    footer_note(c, "Candidate status: PASS_CANDIDATE_NOT_PROMOTED. Numbers on this page are "
                "simulation outputs, not measured range or detection performance.", 66)


def architecture_page(c: canvas.Canvas) -> None:
    page_header(c, 3, "Architecture and measurement")
    section_label(c, "Measurement architecture", H - 29 * mm)
    c.setFillColor(INK)
    c.setFont(SERIF_B, 22)
    c.drawString(M, H - 43 * mm, "One cue. One excess path. One decision.")
    draw_para(c, "The receiver does not control the donor radar and does not perform blind "
              "search. It asks whether a donor, target and receiver geometry supports one "
              "bounded second observation.", M, H - 51 * mm, CONTENT_W,
              size=8.6, leading=12, color=MUTED)

    box_y = 583
    c.setFillColor(colors.HexColor("#E8F1F3"))
    c.roundRect(M, box_y - 202, CONTENT_W, 202, 9, fill=1, stroke=0)
    donor = (M + 68, box_y - 112)
    target = (M + CONTENT_W / 2, box_y - 160)
    receiver = (W - M - 68, box_y - 80)
    c.setDash(5, 4)
    c.setStrokeColor(MUTED)
    c.setLineWidth(1.2)
    c.line(donor[0], donor[1], receiver[0], receiver[1])
    c.setDash()
    c.setStrokeColor(AMBER)
    c.setLineWidth(2.4)
    c.line(donor[0], donor[1], target[0], target[1])
    c.setStrokeColor(TEAL)
    c.line(target[0], target[1], receiver[0], receiver[1])
    for (x, yy), label, sub, col in [
        (donor, "T  DONOR", "merchant radar", AMBER),
        (target, "X  TARGET", "external cue", INK),
        (receiver, "R  RECEIVER", "receive only", TEAL),
    ]:
        c.setFillColor(WHITE)
        c.setStrokeColor(col)
        c.setLineWidth(2)
        c.circle(x, yy, 11, fill=1, stroke=1)
        c.setFillColor(col)
        c.circle(x, yy, 3, fill=1, stroke=0)
        c.setFont(SANS_B, 7.5)
        c.drawCentredString(x, yy + 23, label)
        c.setFillColor(MUTED)
        c.setFont(SANS, 6.8)
        c.drawCentredString(x, yy + 13, sub)
    c.setFillColor(WHITE)
    c.setStrokeColor(RULE)
    c.roundRect(M + 70, box_y - 49, CONTENT_W - 140, 33, 7, fill=1, stroke=1)
    c.setFillColor(INK)
    c.setFont(SERIF, 11.5)
    c.drawCentredString(W / 2, box_y - 37,
                        "rho(t) = |X - T| + |X - R| - |T - R|")
    c.setFont(SANS, 6.6)
    c.setFillColor(MUTED)
    c.drawCentredString(W / 2, box_y - 192,
                        "Solid paths form the bistatic excess path; dashed path is the direct baseline.")

    y = 352
    c.setFillColor(INK)
    c.setFont(SERIF_B, 15)
    c.drawString(M, y, "Minimum useful evidence")
    items = [
        ("01", "Same known target", "The cue exists before passive admission."),
        ("02", "At least 10 independent sweeps", "Rejected sweeps remain visible."),
        ("03", "Geometry-compatible delay", "Uncertainty includes donor metrology."),
        ("04", "Incremental track value", "Compared with a frozen operational baseline."),
    ]
    y -= 22
    for idx, title, desc in items:
        c.setFillColor(TEAL)
        c.circle(M + 12, y - 6, 11, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont(SANS_B, 6.7)
        c.drawCentredString(M + 12, y - 8.5, idx)
        c.setFillColor(INK)
        c.setFont(SANS_B, 8.2)
        c.drawString(M + 31, y, title)
        c.setFillColor(MUTED)
        c.setFont(SANS, 7.4)
        c.drawString(M + 31, y - 12, desc)
        y -= 43

    footer_note(c, "A positive result is not “we detected a ship.” It is a repeatable, "
                "uncertainty-bearing observation that changes a predeclared tracking decision.", 66)


def validation_page(c: canvas.Canvas) -> None:
    page_header(c, 4, "Bounded partner validation")
    section_label(c, "Validation design", H - 29 * mm)
    c.setFillColor(INK)
    c.setFont(SERIF_B, 22)
    c.drawString(M, H - 43 * mm, "Two ways to answer the next question.")
    draw_para(c, "A partner may contribute coherent RF access or a frozen maritime replay. "
              "Neither path requires the partner to buy a new surveillance programme.",
              M, H - 51 * mm, CONTENT_W, size=8.6, leading=12, color=MUTED)

    y = 610
    colw = (CONTENT_W - 12) / 2
    for x, title, badge, body, bullets in [
        (M, "Coherent capture", "TRACK A", "Partner-owned dual-channel receive chain, known "
         "donor and truth-referenced target.", ["Reference and surveillance channels",
         "Timing and cable-delay calibration", "Ten-sweep excess-path test"]),
        (M + colw + 12, "Frozen maritime replay", "TRACK B", "Partner-controlled cues, donor "
         "metadata and retained measurements or signal data.", ["Metrics frozen before replay",
         "Existing baseline preserved", "Truth withheld from the algorithm"]),
    ]:
        c.setFillColor(WHITE)
        c.setStrokeColor(RULE)
        c.roundRect(x, y - 154, colw, 154, 8, fill=1, stroke=1)
        pill(c, badge, x + 13, y - 22, fill=TEAL)
        c.setFillColor(INK)
        c.setFont(SERIF_B, 14)
        c.drawString(x + 13, y - 55, title)
        draw_para(c, body, x + 13, y - 65, colw - 26, size=7.6, leading=10.3, color=MUTED)
        yy = y - 105
        c.setFont(SANS, 7.2)
        for b in bullets:
            c.setFillColor(TEAL)
            c.circle(x + 17, yy + 2, 2, fill=1, stroke=0)
            c.setFillColor(INK)
            c.drawString(x + 25, yy, b)
            yy -= 15

    c.setFillColor(INK)
    c.setFont(SERIF_B, 15)
    c.drawString(M, 424, "Acceptance ladder")
    gates = [
        ("0", "Calibration", "Coherence, timing, saturation and receive-only state."),
        ("1", "Association", "Donor identity and propagated position uncertainty."),
        ("2", "Repeatability", "Ten independent sweeps without post-hoc thresholds."),
        ("3", "Track value", "Improvement against the partner's frozen baseline."),
        ("4", "Economics", "Integration cost remains below plausible operational value."),
    ]
    start_y = 391
    for i, (num, title, desc) in enumerate(gates):
        yy = start_y - i * 52
        c.setFillColor(TEAL if i < 4 else AMBER)
        c.roundRect(M, yy - 33, 37, 37, 6, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont(SERIF_B, 15)
        c.drawCentredString(M + 18.5, yy - 21, num)
        c.setFillColor(INK)
        c.setFont(SANS_B, 8.2)
        c.drawString(M + 50, yy - 7, title)
        c.setFillColor(MUTED)
        c.setFont(SANS, 7.3)
        c.drawString(M + 50, yy - 21, desc)
        if i < len(gates) - 1:
            c.setStrokeColor(RULE)
            c.setLineWidth(1)
            c.line(M + 18.5, yy - 33, M + 18.5, yy - 48)

    footer_note(c, "Final outcomes are PASS, REDESIGN, KILL or INSUFFICIENT EVIDENCE. "
                "A failed gate is a useful result when it prevents unbounded integration spend.", 66)


def integration_page(c: canvas.Canvas) -> None:
    page_header(c, 5, "Integration contract")
    section_label(c, "System boundary", H - 29 * mm)
    c.setFillColor(INK)
    c.setFont(SERIF_B, 20)
    c.drawString(M, H - 42 * mm, "A measurement service,")
    c.drawString(M, H - 50 * mm, "not a replacement radar.")
    draw_para(c, "SCILLA PASSIVE receives an external cue and one candidate illumination "
              "opportunity. It returns one bounded observation or an explicit rejection reason.",
              M, H - 58 * mm, CONTENT_W, size=8.6, leading=12, color=MUTED)

    y = 596
    boxw = 132
    boxh = 98
    gap = (CONTENT_W - 3 * boxw) / 2
    boxes = [
        (M, "INPUT", "Cue and covariance\nReceiver state\nDonor state\nCandidate delay", LIGHT, INK),
        (M + boxw + gap, "DECISION", "Geometry\nMetrology\nAssociation\nIntegrity gate", colors.HexColor("#DDF0EF"), TEAL_DARK),
        (M + 2 * (boxw + gap), "OUTPUT", "Admit or reject\nEffective variance\nNIS and reason codes\nVersion and hashes", colors.HexColor("#E8EDF0"), INK),
    ]
    for x, label, body, fill, col in boxes:
        c.setFillColor(fill)
        c.roundRect(x, y - boxh, boxw, boxh, 8, fill=1, stroke=0)
        c.setFillColor(col)
        c.setFont(SANS_B, 7.5)
        c.drawString(x + 12, y - 20, label)
        yy = y - 42
        c.setFont(SANS, 7.2)
        for line in body.split("\n"):
            c.drawString(x + 12, yy, line)
            yy -= 14
    c.setStrokeColor(TEAL)
    c.setLineWidth(1.8)
    c.line(M + boxw + 3, y - boxh / 2, M + boxw + gap - 3, y - boxh / 2)
    c.line(M + 2 * boxw + gap + 3, y - boxh / 2,
           M + 2 * (boxw + gap) - 3, y - boxh / 2)

    c.setFillColor(INK)
    c.setFont(SERIF_B, 15)
    c.drawString(M, 474, "Required rejection vocabulary")
    codes = ["NO USABLE DONOR", "ASSOCIATION AMBIGUOUS", "GEOMETRY DEGENERATE",
             "TIMING UNBOUNDED", "REFERENCE SATURATED", "SNR INSUFFICIENT",
             "CLUTTER DOMINANT", "NIS OUTLIER", "CALIBRATION INVALID"]
    xx, yy = M, 445
    for code in codes:
        pw = pill(c, code, xx, yy, fill=WHITE, color=INK, font_size=6.2, pad_x=6)
        c.setStrokeColor(RULE)
        c.roundRect(xx, yy - 4, pw, 15, 7.5, fill=0, stroke=1)
        xx += pw + 6
        if xx > W - M - 100:
            xx = M
            yy -= 24

    c.setFillColor(INK)
    c.setFont(SERIF_B, 15)
    c.drawString(M, 348, "Insertion points")
    rows = [
        ("Track manager", "Supplies cue and covariance", "No silent state overwrite"),
        ("Signal processor", "Produces delay and uncertainty", "Calibration retained"),
        ("Fusion engine", "Admits bounded observation", "Baseline replay preserved"),
        ("Operator view", "Shows evidence and reasons", "Simulation and measurement distinct"),
        ("Evidence store", "Preserves inputs and hashes", "Deterministic audit trail"),
    ]
    x0, table_top = M, 324
    widths = [112, 177, CONTENT_W - 289]
    headers = ["SYSTEM", "ROLE", "NON-NEGOTIABLE BOUNDARY"]
    c.setFillColor(INK)
    c.rect(x0, table_top - 25, CONTENT_W, 25, fill=1, stroke=0)
    x = x0
    c.setFillColor(WHITE)
    c.setFont(SANS_B, 6.7)
    for h, ww in zip(headers, widths):
        c.drawString(x + 7, table_top - 16, h)
        x += ww
    for r, row in enumerate(rows):
        ry = table_top - 25 - (r + 1) * 33
        c.setFillColor(WHITE if r % 2 == 0 else colors.HexColor("#F0F4F4"))
        c.rect(x0, ry, CONTENT_W, 33, fill=1, stroke=0)
        x = x0
        for cell, ww in zip(row, widths):
            draw_para(c, cell, x + 7, ry + 23, ww - 12, size=6.7, leading=8.3,
                      color=INK)
            x += ww
    footer_note(c, "Every output carries its software commit, model version, calibration ID "
                "and input hash. Missing covariance, timing or association must fail safe.", 66)


def partner_page(c: canvas.Canvas) -> None:
    page_header(c, 6, "Industrial decision")
    section_label(c, "Partner decision", H - 29 * mm)
    c.setFillColor(INK)
    c.setFont(SERIF_B, 22)
    c.drawString(M, H - 43 * mm, "The acquisition thesis must be earned.")
    draw_para(c, "A public simulation package is not a product and not an exit. It can, "
              "however, make a low-cost diligence decision possible for an organisation "
              "that already controls the missing hardware, data or integration context.",
              M, H - 51 * mm, CONTENT_W, size=8.6, leading=12, color=MUTED)

    c.setFillColor(INK)
    c.setFont(SERIF_B, 15)
    c.drawString(M, 622, "A useful partner contributes one missing asset")
    assets = [
        ("RADAR OEM", "Reference channel and emitter expertise"),
        ("SURVEILLANCE INTEGRATOR", "Frozen tracks, truth and baseline workflow"),
        ("MARITIME OPERATOR", "Operational decision and economics"),
        ("RESEARCH LAB", "Coherent SDR capture and independent reproduction"),
    ]
    y = 592
    for i, (title, desc) in enumerate(assets):
        x = M + (i % 2) * (CONTENT_W / 2 + 5)
        yy = y - (i // 2) * 73
        w = CONTENT_W / 2 - 5
        c.setFillColor(WHITE)
        c.setStrokeColor(RULE)
        c.roundRect(x, yy - 57, w, 57, 7, fill=1, stroke=1)
        c.setFillColor(TEAL)
        c.setFont(SANS_B, 7.1)
        c.drawString(x + 11, yy - 18, title)
        draw_para(c, desc, x + 11, yy - 26, w - 22, size=7.2, leading=9.5,
                  color=INK)

    c.setFillColor(INK)
    c.setFont(SERIF_B, 15)
    c.drawString(M, 428, "Before licensing or acquisition, answer six questions")
    questions = [
        "Which existing decision becomes materially better?",
        "What active dwell, revisit or operator action can be deferred?",
        "What does one accepted observation cost, including rejects?",
        "What false-association cost is operationally tolerable?",
        "Can integration avoid a safety-critical control-loop change?",
        "Is licensing the evidence and know-how cheaper than rebuilding it?",
    ]
    yq = 395
    for i, q in enumerate(questions, 1):
        c.setFillColor(TEAL)
        c.setFont(SERIF_B, 10)
        c.drawString(M, yq, f"{i:02d}")
        c.setFillColor(INK)
        c.setFont(SANS, 8)
        c.drawString(M + 29, yq, q)
        c.setStrokeColor(RULE)
        c.line(M + 29, yq - 8, W - M, yq - 8)
        yq -= 35

    c.setFillColor(INK)
    c.roundRect(M, 113, CONTENT_W, 72, 9, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont(SANS_B, 8)
    c.drawString(M + 15, 164, "PROPOSED FIRST CONTACT")
    c.setFont(SERIF_B, 13.5)
    c.drawString(M + 15, 139, "A 30-minute technical screen, then a bounded data gate.")
    c.setFont(SANS, 7.3)
    c.drawString(M + 15, 123, "Michele Giletto · michele.giletto@gmail.com")
    c.setFillColor(MUTED)
    c.setFont(SANS, 6.8)
    c.drawString(M, 88, "Public package: github.com/michelegiletto-beep/scilla-passive-evidence")
    c.drawString(M, 75, "Canonical archive: doi.org/10.5281/zenodo.22229086")
    c.setFont(SANS_B, 6.8)
    c.drawRightString(W - M, 75, "RECEIVE ONLY · SIMULATION EVIDENCE · PHYSICAL GATE OPEN")


def build() -> Path:
    register_fonts()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUT), pagesize=A4, pageCompression=1)
    c.setTitle("SCILLA PASSIVE — Partner Validation Dossier")
    c.setAuthor("Michele Giletto")
    c.setSubject("Partner-controlled falsification and integration dossier")
    cover(c)
    c.showPage()
    evidence_page(c)
    c.showPage()
    architecture_page(c)
    c.showPage()
    validation_page(c)
    c.showPage()
    integration_page(c)
    c.showPage()
    partner_page(c)
    c.save()
    return OUT


if __name__ == "__main__":
    print(build())
