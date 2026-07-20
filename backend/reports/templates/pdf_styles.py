"""
PDF Templates & Styles for Cryptanium Security Reports.
Provides custom ReportLab styles, color palettes, and header/footer handlers.
"""

from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas

# Cryptanium Theme Palette
PRIMARY_DARK = colors.HexColor("#0F172A")    # Deep Navy
SECONDARY_ACCENT = colors.HexColor("#38BDF8") # Cyan Accent
BG_LIGHT = colors.HexColor("#F8FAFC")        # Off-white
TEXT_PRIMARY = colors.HexColor("#1E293B")    # Slate
TEXT_MUTED = colors.HexColor("#64748B")      # Muted Slate
BORDER_COLOR = colors.HexColor("#E2E8F0")    # Soft border

# Severity Colors
SEV_COLORS = {
    "Critical": colors.HexColor("#DC2626"),
    "High": colors.HexColor("#EA580C"),
    "Medium": colors.HexColor("#D97706"),
    "Low": colors.HexColor("#2563EB"),
    "Info": colors.HexColor("#6B7280"),
}

# Risk Level Colors
RISK_COLORS = {
    "Excellent": colors.HexColor("#10B981"),
    "Good": colors.HexColor("#3B82F6"),
    "Moderate": colors.HexColor("#F59E0B"),
    "Risky": colors.HexColor("#F97316"),
    "Critical": colors.HexColor("#EF4444"),
}


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas for adding total page numbers and header/footer."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count: int):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(TEXT_MUTED)

        # Header (on pages after page 1)
        if self._pageNumber > 1:
            self.drawString(36, 762, "Cryptanium Security Scan Report")
            self.setStrokeColor(BORDER_COLOR)
            self.setLineWidth(0.5)
            self.line(36, 754, 576, 754)

        # Footer (on all pages)
        self.setStrokeColor(BORDER_COLOR)
        self.setLineWidth(0.5)
        self.line(36, 45, 576, 45)

        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(576, 30, page_str)
        self.drawString(36, 30, "CONFIDENTIAL - Cryptanium Security Engine")
        self.restoreState()


def get_cryptanium_stylesheet():
    """Generates standard ReportLab stylesheet with Cryptanium branding."""
    styles = getSampleStyleSheet()

    # Document Title
    styles.add(ParagraphStyle(
        name="ReportTitle",
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=28,
        textColor=PRIMARY_DARK,
        spaceAfter=6,
    ))

    # Subtitle / Metadata
    styles.add(ParagraphStyle(
        name="ReportSubtitle",
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=TEXT_MUTED,
        spaceAfter=15,
    ))

    # H1 Section Headers
    styles.add(ParagraphStyle(
        name="SectionHeader",
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=PRIMARY_DARK,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True,
    ))

    # H2 Sub-headers
    styles.add(ParagraphStyle(
        name="SubSectionHeader",
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=TEXT_PRIMARY,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True,
    ))

    # Regular Body Text
    styles.add(ParagraphStyle(
        name="ReportBody",
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=TEXT_PRIMARY,
        spaceAfter=6,
    ))

    # Table Cell Text
    styles.add(ParagraphStyle(
        name="TableCell",
        fontName="Helvetica",
        fontSize=8.5,
        leading=11.5,
        textColor=TEXT_PRIMARY,
    ))

    # Table Header Cell Text
    styles.add(ParagraphStyle(
        name="TableHeader",
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11.5,
        textColor=colors.white,
    ))

    return styles
