"""
PDF Report Generator for Cryptanium Member 4.
Builds executive security PDF reports using ReportLab Platypus flowables.
"""

from typing import Dict, Any, List
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
)
from reportlab.lib import colors

from backend.utils.parser import ScanPayload
from backend.trust.trust_engine import TrustScoreResult
from backend.utils.formatter import get_current_date_formatted, format_owasp_category, truncate_text
from backend.reports.templates.pdf_styles import (
    get_cryptanium_stylesheet,
    NumberedCanvas,
    PRIMARY_DARK,
    SECONDARY_ACCENT,
    BG_LIGHT,
    BORDER_COLOR,
    TEXT_PRIMARY,
    TEXT_MUTED,
    SEV_COLORS,
    RISK_COLORS,
)


class PDFReportGenerator:
    """Generates publication-ready PDF security reports."""

    def __init__(self):
        self.styles = get_cryptanium_stylesheet()

    def generate_pdf(
        self,
        payload: ScanPayload,
        trust_result: TrustScoreResult,
        summary: Dict[str, str],
        recommendations: List[Dict[str, Any]],
        output_filepath: str,
    ) -> str:
        """Generates a complete PDF report and saves it to output_filepath."""
        doc = SimpleDocTemplate(
            output_filepath,
            pagesize=letter,
            leftMargin=36,
            rightMargin=36,
            topMargin=45,
            bottomMargin=55,
        )

        story = []

        # 1. Header Section
        story.extend(self._build_header(payload, trust_result))
        story.append(Spacer(1, 10))

        # 2. Executive Summary Card
        story.extend(self._build_summary_section(summary))
        story.append(Spacer(1, 12))

        # 3. Trust Score & Risk Level Breakdown
        story.extend(self._build_score_breakdown_section(trust_result))
        story.append(Spacer(1, 12))

        # 4. OWASP Top 10 Mapping Section
        story.extend(self._build_owasp_mapping_section(payload.findings))
        story.append(Spacer(1, 12))

        # 5. Finding Table
        story.extend(self._build_findings_table(payload.findings))
        story.append(Spacer(1, 12))

        # 6. Prioritized Recommendations
        story.extend(self._build_recommendations_section(recommendations))

        doc.build(story, canvasmaker=NumberedCanvas)
        return output_filepath

    def _build_header(self, payload: ScanPayload, trust_result: TrustScoreResult) -> List[Any]:
        elements = []
        title_p = Paragraph("Cryptanium Security Audit Report", self.styles["ReportTitle"])
        elements.append(title_p)

        scan_date = payload.scan_date or get_current_date_formatted()
        meta_str = f"<b>Repository:</b> {payload.repository} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Branch:</b> {payload.branch} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Language:</b> {payload.language} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Scan Date:</b> {scan_date}"
        elements.append(Paragraph(meta_str, self.styles["ReportSubtitle"]))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY_DARK, spaceBefore=0, spaceAfter=10))
        return elements

    def _build_summary_section(self, summary: Dict[str, str]) -> List[Any]:
        elements = [Paragraph("1. Executive Summary", self.styles["SectionHeader"])]

        overview = summary.get("repository_overview", "")
        posture = summary.get("security_posture", "")
        severe = summary.get("most_severe_findings", "")
        readiness = summary.get("deployment_readiness", "")

        card_content = [
            [Paragraph("<b>Repository Overview:</b>", self.styles["ReportBody"]), Paragraph(overview, self.styles["ReportBody"])],
            [Paragraph("<b>Security Posture:</b>", self.styles["ReportBody"]), Paragraph(posture, self.styles["ReportBody"])],
            [Paragraph("<b>Key Security Findings:</b>", self.styles["ReportBody"]), Paragraph(severe, self.styles["ReportBody"])],
            [Paragraph("<b>Deployment Readiness:</b>", self.styles["ReportBody"]), Paragraph(f"<b>{readiness}</b>", self.styles["ReportBody"])],
        ]

        t = Table(card_content, colWidths=[130, 410])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), BG_LIGHT),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ("BOX", (0, 0), (-1, -1), 1, BORDER_COLOR),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ]))
        elements.append(t)
        return elements

    def _build_score_breakdown_section(self, trust_result: TrustScoreResult) -> List[Any]:
        elements = [Paragraph("2. Trust Score & Risk Level Analysis", self.styles["SectionHeader"])]

        risk_color = RISK_COLORS.get(trust_result.risk_level, colors.HexColor("#6B7280"))
        score_text = f"<font size=18 color='{risk_color.hexval()}'><b>{trust_result.final_score} / 100</b></font><br/><font size=11 color='{risk_color.hexval()}'><b>{trust_result.risk_level} Risk</b></font>"

        # Summary box table
        score_p = Paragraph(score_text, self.styles["ReportBody"])

        breakdown_rows = [["Rule Applied", "Deduction", "Details / Reason"]]
        for item in trust_result.breakdown:
            ded_str = f"-{item.deduction:.1f} pts" if item.deduction > 0 else "0.0 pts"
            breakdown_rows.append([
                Paragraph(f"<b>{item.rule_name}</b>", self.styles["TableCell"]),
                Paragraph(ded_str, self.styles["TableCell"]),
                Paragraph(item.reason, self.styles["TableCell"]),
            ])

        b_table = Table(breakdown_rows, colWidths=[140, 60, 240])
        b_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), PRIMARY_DARK),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ("BOX", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]))

        main_box = Table([[score_p, b_table]], colWidths=[100, 440])
        main_box.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 0), (0, 0), "CENTER"),
            ("BACKGROUND", (0, 0), (0, 0), BG_LIGHT),
            ("BOX", (0, 0), (-1, -1), 1, BORDER_COLOR),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))

        elements.append(main_box)
        return elements

    def _build_owasp_mapping_section(self, findings: List[Any]) -> List[Any]:
        elements = [Paragraph("3. OWASP Top 10 Category Mapping", self.styles["SectionHeader"])]

        counts: Dict[str, int] = {}
        for f in findings:
            cat = format_owasp_category(f.owasp)
            counts[cat] = counts.get(cat, 0) + 1

        if not counts:
            elements.append(Paragraph("No OWASP-mapped vulnerabilities detected.", self.styles["ReportBody"]))
            return elements

        table_data = [["OWASP Category", "Findings Count"]]
        for cat, cnt in sorted(counts.items(), key=lambda x: x[1], reverse=True):
            table_data.append([
                Paragraph(cat, self.styles["TableCell"]),
                Paragraph(str(cnt), self.styles["TableCell"]),
            ])

        t = Table(table_data, colWidths=[400, 140])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), PRIMARY_DARK),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ("BOX", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]))
        elements.append(t)
        return elements

    def _build_findings_table(self, findings: List[Any]) -> List[Any]:
        elements = [Paragraph("4. Security Findings Matrix", self.styles["SectionHeader"])]

        if not findings:
            elements.append(Paragraph("Zero security findings reported. Scan passed cleanly.", self.styles["ReportBody"]))
            return elements

        table_data = [["Sev", "Tool", "Location", "Description", "OWASP"]]
        for f in findings:
            sev_color = SEV_COLORS.get(f.severity, colors.HexColor("#6B7280"))
            sev_p = Paragraph(f"<font color='{sev_color.hexval()}'><b>{f.severity}</b></font>", self.styles["TableCell"])
            tool_p = Paragraph(f.tool, self.styles["TableCell"])
            loc_str = f"{f.file}:{f.line}" if f.line else f.file
            loc_p = Paragraph(truncate_text(loc_str, 25), self.styles["TableCell"])
            desc_p = Paragraph(f.description, self.styles["TableCell"])
            owasp_p = Paragraph(f.owasp or "N/A", self.styles["TableCell"])

            table_data.append([sev_p, tool_p, loc_p, desc_p, owasp_p])

        t = Table(table_data, colWidths=[55, 65, 110, 255, 55])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), PRIMARY_DARK),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ("BOX", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ]))
        elements.append(t)
        return elements

    def _build_recommendations_section(self, recommendations: List[Dict[str, Any]]) -> List[Any]:
        elements = [Paragraph("5. Prioritized Remediation Action Plan", self.styles["SectionHeader"])]

        if not recommendations:
            elements.append(Paragraph("No remediation actions required.", self.styles["ReportBody"]))
            return elements

        table_data = [["Priority", "Issue", "Recommended Fix", "Security Reason"]]
        for r in recommendations:
            prio = r.get("priority", "Low")
            prio_color = "#DC2626" if prio in ("Urgent", "Critical") else ("#EA580C" if prio == "High" else "#2563EB")
            prio_p = Paragraph(f"<font color='{prio_color}'><b>{prio}</b></font>", self.styles["TableCell"])
            issue_p = Paragraph(f"<b>{r.get('issue', '')}</b>", self.styles["TableCell"])
            fix_p = Paragraph(r.get("recommended_fix", ""), self.styles["TableCell"])
            reason_p = Paragraph(r.get("reason", ""), self.styles["TableCell"])

            table_data.append([prio_p, issue_p, fix_p, reason_p])

        t = Table(table_data, colWidths=[55, 125, 180, 180])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), PRIMARY_DARK),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ("BOX", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ]))
        elements.append(t)
        return elements
