"""
Premium PDF Contract Generator for SAOUD CAR
Generates a professional, visually stunning rental contract.
Uses reportlab canvas for pixel-perfect layout control.
"""
import io
import os
import math
from decimal import Decimal

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.pdfgen import canvas
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import Paragraph, Frame
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from core.models import RentalContract, AgencyInfo

# ── Colour Palette ──────────────────────────────────────────────
PRIMARY = colors.HexColor('#1A1A2E')       # Deep navy
ACCENT = colors.HexColor('#D4A843')         # Elegant gold
ACCENT_LIGHT = colors.HexColor('#F5E6C8')   # Pale gold
SECTION_BG = colors.HexColor('#1A1A2E')     # Section header bg
TEXT_DARK = colors.HexColor('#1A1A2E')
TEXT_MID = colors.HexColor('#555555')
TEXT_LIGHT = colors.HexColor('#888888')
LINE_COLOR = colors.HexColor('#CCCCCC')
BG_LIGHT = colors.HexColor('#FAFAFA')
WHITE = colors.white
BLACK = colors.black
LIGHT_GOLD_BG = colors.HexColor('#FDF8EE')
CHECK_GREEN = colors.HexColor('#2E7D32')
DANGER_RED = colors.HexColor('#C62828')

PAGE_W, PAGE_H = A4
MARGIN_L = 1.2 * cm
MARGIN_R = 1.2 * cm
MARGIN_T = 1.0 * cm
MARGIN_B = 1.0 * cm
CONTENT_W = PAGE_W - MARGIN_L - MARGIN_R


# ── Helper: safe attribute access ───────────────────────────────
def _safe(obj, attr, default='—'):
    """Safely get an attribute, returning default if missing or None."""
    val = getattr(obj, attr, None)
    if val is None:
        return default
    return val


def _fmt_date(val):
    """Format a date object to dd/mm/yyyy string."""
    if val is None:
        return '—'
    try:
        return val.strftime('%d/%m/%Y')
    except Exception:
        return str(val) if val else '—'


def _fmt_amount(val):
    """Format a decimal/float to 2-decimal string."""
    try:
        return f"{float(val):,.2f}".replace(',', ' ')
    except (TypeError, ValueError):
        return '0.00'


# ── Drawing Primitives ──────────────────────────────────────────
def draw_rounded_rect(c, x, y, w, h, r=6, stroke=1, fill=0,
                      stroke_color=PRIMARY, fill_color=WHITE):
    """Draw a rounded rectangle."""
    c.saveState()
    c.setStrokeColor(stroke_color)
    c.setFillColor(fill_color)
    c.setLineWidth(0.8)
    p = c.beginPath()
    p.moveTo(x + r, y)
    p.lineTo(x + w - r, y)
    p.arcTo(x + w - r, y, x + w, y + r, -90, 90)
    p.lineTo(x + w, y + h - r)
    p.arcTo(x + w - r, y + h - r, x + w, y + h, 0, 90)
    p.lineTo(x + r, y + h)
    p.arcTo(x, y + h - r, x + r, y + h, 90, 90)
    p.lineTo(x, y + r)
    p.arcTo(x, y, x + r, y + r, 180, 90)
    p.close()
    c.drawPath(p, stroke=stroke, fill=fill)
    c.restoreState()


def draw_section_header(c, x, y, w, h, title):
    """Draw a premium section header with dark background and gold accent."""
    # Background
    draw_rounded_rect(c, x, y, w, h, r=4, stroke=0, fill=1,
                      fill_color=SECTION_BG)
    # Gold accent line at bottom
    c.saveState()
    c.setStrokeColor(ACCENT)
    c.setLineWidth(2)
    c.line(x + 8, y, x + w - 8, y)
    c.restoreState()
    # Title text
    c.saveState()
    c.setFillColor(WHITE)
    c.setFont('Helvetica-Bold', 8.5)
    c.drawString(x + 8, y + h / 2 - 3, title.upper())
    c.restoreState()


def draw_section_box(c, x, y, w, h, title, title_h=18):
    """Draw a complete section box with header and content area."""
    # Content area
    draw_rounded_rect(c, x, y, w, h, r=5, stroke=1, fill=1,
                      stroke_color=colors.HexColor('#E0E0E0'),
                      fill_color=WHITE)
    # Header
    draw_section_header(c, x, y + h - title_h, w, title_h, title)
    return y + h - title_h  # Return the y position below header


def draw_checkbox(c, x, y, size=9, checked=False):
    """Draw a styled checkbox."""
    c.saveState()
    c.setLineWidth(1)
    if checked:
        # Filled checkbox with check mark
        c.setFillColor(CHECK_GREEN)
        c.setStrokeColor(CHECK_GREEN)
        c.roundRect(x, y, size, size, 2, stroke=1, fill=1)
        # White checkmark
        c.setStrokeColor(WHITE)
        c.setLineWidth(1.5)
        c.line(x + 2, y + size / 2, x + size / 2 - 0.5, y + 2.5)
        c.line(x + size / 2 - 0.5, y + 2.5, x + size - 2, y + size - 2.5)
    else:
        c.setStrokeColor(LINE_COLOR)
        c.setFillColor(WHITE)
        c.roundRect(x, y, size, size, 2, stroke=1, fill=1)
    c.restoreState()


def draw_fuel_gauge(c, cx, cy, radius=18):
    """Draw a premium fuel gauge."""
    c.saveState()
    # Background arc
    c.setStrokeColor(colors.HexColor('#DDDDDD'))
    c.setLineWidth(3)
    c.arc(cx - radius, cy - radius, cx + radius, cy + radius, 0, 180)
    # Coloured arc segments (E=red, mid=yellow, F=green)
    segment_angle = 60
    c.setLineWidth(4)
    c.setStrokeColor(DANGER_RED)
    c.arc(cx - radius, cy - radius, cx + radius, cy + radius, 120, 60)
    c.setStrokeColor(colors.HexColor('#F9A825'))
    c.arc(cx - radius, cy - radius, cx + radius, cy + radius, 60, 60)
    c.setStrokeColor(CHECK_GREEN)
    c.arc(cx - radius, cy - radius, cx + radius, cy + radius, 0, 60)
    # Needle at 75% (135 degrees from right = 45 degrees from left)
    needle_angle = math.radians(45)
    nx = cx + (radius - 5) * math.cos(needle_angle)
    ny = cy + (radius - 5) * math.sin(needle_angle)
    c.setStrokeColor(DANGER_RED)
    c.setLineWidth(1.5)
    c.line(cx, cy, nx, ny)
    # Center dot
    c.setFillColor(PRIMARY)
    c.circle(cx, cy, 2.5, fill=1, stroke=0)
    # Labels
    c.setFont('Helvetica-Bold', 6)
    c.setFillColor(DANGER_RED)
    c.drawString(cx - radius - 3, cy - 3, 'E')
    c.setFillColor(CHECK_GREEN)
    c.drawString(cx + radius - 1, cy - 3, 'F')
    c.restoreState()


def draw_car_diagram(c, cx, cy, scale=1.0):
    """Draw a premium top-down car silhouette."""
    c.saveState()
    s = scale
    # Body outline
    c.setStrokeColor(PRIMARY)
    c.setFillColor(colors.HexColor('#F0F0F0'))
    c.setLineWidth(1.2)
    # Main body (rounded rectangle)
    bw, bh = 30 * s, 65 * s
    c.roundRect(cx - bw / 2, cy - bh / 2, bw, bh, 8 * s, stroke=1, fill=1)
    # Windshields
    c.setFillColor(colors.HexColor('#B3D4FC'))
    c.setStrokeColor(colors.HexColor('#7EABD4'))
    c.setLineWidth(0.8)
    # Front windshield
    c.roundRect(cx - 10 * s, cy + 14 * s, 20 * s, 10 * s, 3 * s, stroke=1, fill=1)
    # Rear windshield
    c.roundRect(cx - 9 * s, cy - 22 * s, 18 * s, 8 * s, 3 * s, stroke=1, fill=1)
    # Wheels
    c.setFillColor(colors.HexColor('#333333'))
    c.setStrokeColor(BLACK)
    ww, wh = 5 * s, 12 * s
    # Front left
    c.roundRect(cx - bw / 2 - ww / 2 - 1, cy + 12 * s, ww, wh, 2 * s, stroke=1, fill=1)
    # Front right
    c.roundRect(cx + bw / 2 - ww / 2 + 1, cy + 12 * s, ww, wh, 2 * s, stroke=1, fill=1)
    # Rear left
    c.roundRect(cx - bw / 2 - ww / 2 - 1, cy - 22 * s, ww, wh, 2 * s, stroke=1, fill=1)
    # Rear right
    c.roundRect(cx + bw / 2 - ww / 2 + 1, cy - 22 * s, ww, wh, 2 * s, stroke=1, fill=1)
    # Side mirrors
    c.setFillColor(colors.HexColor('#CCCCCC'))
    c.setLineWidth(0.6)
    c.roundRect(cx - bw / 2 - 4 * s, cy + 18 * s, 4 * s, 5 * s, 1.5 * s, stroke=1, fill=1)
    c.roundRect(cx + bw / 2, cy + 18 * s, 4 * s, 5 * s, 1.5 * s, stroke=1, fill=1)
    # Headlights
    c.setFillColor(colors.HexColor('#FFF176'))
    c.setLineWidth(0.5)
    c.roundRect(cx - 10 * s, cy + bh / 2 - 4 * s, 6 * s, 3 * s, 1 * s, stroke=1, fill=1)
    c.roundRect(cx + 4 * s, cy + bh / 2 - 4 * s, 6 * s, 3 * s, 1 * s, stroke=1, fill=1)
    # Taillights
    c.setFillColor(DANGER_RED)
    c.roundRect(cx - 10 * s, cy - bh / 2 + 1 * s, 5 * s, 2.5 * s, 1 * s, stroke=1, fill=1)
    c.roundRect(cx + 5 * s, cy - bh / 2 + 1 * s, 5 * s, 2.5 * s, 1 * s, stroke=1, fill=1)
    c.restoreState()


def draw_label_value(c, x, y, label, value, label_font='Helvetica', value_font='Helvetica-Bold',
                     label_size=7.5, value_size=8, label_color=TEXT_MID, value_color=TEXT_DARK,
                     label_w=None):
    """Draw a label: value pair."""
    c.saveState()
    c.setFont(label_font, label_size)
    c.setFillColor(label_color)
    c.drawString(x, y, str(label))
    if label_w is None:
        label_w = c.stringWidth(str(label), label_font, label_size) + 3
    c.setFont(value_font, value_size)
    c.setFillColor(value_color)
    c.drawString(x + label_w, y, str(value))
    c.restoreState()


def draw_dotted_line(c, x1, y, x2, dot_color=LINE_COLOR):
    """Draw a dotted line."""
    c.saveState()
    c.setStrokeColor(dot_color)
    c.setLineWidth(0.5)
    c.setDash([1, 2])
    c.line(x1, y, x2, y)
    c.setDash()
    c.restoreState()


def draw_big_x(c, x, y, w, h, color=colors.HexColor('#E0E0E0')):
    """Draw a large X across a rectangular area."""
    c.saveState()
    c.setStrokeColor(color)
    c.setLineWidth(1.5)
    c.line(x, y, x + w, y + h)
    c.line(x, y + h, x + w, y)
    c.restoreState()


# ── Main PDF Generation ─────────────────────────────────────────
def generate_contract_pdf(request, contract_id):
    """Generate a premium styled rental contract PDF."""
    contract = get_object_or_404(
        RentalContract.objects.select_related('client', 'car', 'car__brand_ref'),
        id=contract_id
    )
    agency = AgencyInfo.objects.first()
    client = contract.client
    car = contract.car

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    c.setTitle(f"Contrat {contract.contract_number}")
    c.setAuthor(agency.name if agency else "SAOUD CAR")

    # ────────────────────────────────────────────
    # PAGE 1: CONTRACT
    # ────────────────────────────────────────────
    y = PAGE_H - MARGIN_T

    # ── HEADER ──────────────────────────────────
    # Gold accent bar at very top
    c.saveState()
    c.setFillColor(ACCENT)
    c.rect(0, PAGE_H - 4, PAGE_W, 4, stroke=0, fill=1)
    c.restoreState()

    y -= 8  # Below gold bar

    # Logo
    logo_path = None
    if agency and agency.logo:
        try:
            if os.path.exists(agency.logo.path):
                logo_path = agency.logo.path
        except Exception:
            pass
    if not logo_path:
        fallback = os.path.join(settings.BASE_DIR, 'core', 'static', 'core', 'img', 'contlogo.png')
        if os.path.exists(fallback):
            logo_path = fallback

    logo_h = 2.2 * cm
    logo_w = 3.5 * cm
    if logo_path:
        try:
            from reportlab.lib.utils import ImageReader
            c.drawImage(logo_path, MARGIN_L, y - logo_h,
                        width=logo_w, height=logo_h,
                        preserveAspectRatio=True, mask='auto')
        except Exception:
            pass

    # Title block (right side)
    c.saveState()
    c.setFont('Helvetica-Bold', 22)
    c.setFillColor(PRIMARY)
    title_text = "CONTRAT DE LOCATION"
    title_w = c.stringWidth(title_text, 'Helvetica-Bold', 22)
    title_x = PAGE_W - MARGIN_R - title_w
    c.drawString(title_x, y - 18, title_text)

    # Gold underline for title
    c.setStrokeColor(ACCENT)
    c.setLineWidth(2.5)
    c.line(title_x, y - 22, PAGE_W - MARGIN_R, y - 22)
    c.restoreState()

    # Contract number badge
    num_text = f"N° {contract.contract_number}"
    c.saveState()
    badge_w = 4.5 * cm
    badge_h = 0.7 * cm
    badge_x = PAGE_W - MARGIN_R - badge_w
    badge_y = y - 42
    draw_rounded_rect(c, badge_x, badge_y, badge_w, badge_h, r=4,
                      stroke=1, fill=1,
                      stroke_color=ACCENT, fill_color=ACCENT_LIGHT)
    c.setFont('Helvetica-Bold', 10)
    c.setFillColor(PRIMARY)
    num_w = c.stringWidth(num_text, 'Helvetica-Bold', 10)
    c.drawString(badge_x + (badge_w - num_w) / 2, badge_y + badge_h / 2 - 3.5, num_text)
    c.restoreState()

    y -= logo_h + 12

    # ── INFO BAR ────────────────────────────────
    info_h = 3.2 * cm
    info_y = y - info_h
    draw_rounded_rect(c, MARGIN_L, info_y, CONTENT_W, info_h, r=5,
                      stroke=1, fill=1,
                      stroke_color=colors.HexColor('#E0E0E0'),
                      fill_color=BG_LIGHT)

    # Info rows
    row_y = y - 16
    left_x = MARGIN_L + 10
    mid_x = MARGIN_L + CONTENT_W / 2 + 10
    lbl_w = 3.2 * cm

    info_rows = [
        ("Fait le :", _fmt_date(contract.created_at),
         "Marque :", car.get_brand_display()),
        ("Lieu de livraison :", _safe(contract, 'delivery_location'),
         "Immatriculation :", car.license_plate or '—'),
        ("Lieu de reprise :", _safe(contract, 'return_location'),
         "Agent Commercial :", _safe(contract, 'agent_name')),
    ]

    for i, (lbl1, val1, lbl2, val2) in enumerate(info_rows):
        ry = row_y - i * 24
        draw_label_value(c, left_x, ry, lbl1, val1, label_w=lbl_w)
        draw_label_value(c, mid_x, ry, lbl2, val2, label_w=lbl_w)
        # Dotted underlines under values
        draw_dotted_line(c, left_x + lbl_w, ry - 3, mid_x - 15)
        draw_dotted_line(c, mid_x + lbl_w, ry - 3, MARGIN_L + CONTENT_W - 10)

    y = info_y - 8

    # ── TWO-COLUMN BODY ─────────────────────────
    col_gap = 8
    col_l_w = CONTENT_W * 0.48
    col_r_w = CONTENT_W * 0.52 - col_gap
    col_l_x = MARGIN_L
    col_r_x = MARGIN_L + col_l_w + col_gap

    body_y = y  # Track the starting y for both columns

    # ═══════════════════════════════════════════
    # LEFT COLUMN
    # ═══════════════════════════════════════════

    # ── DURÉE DE LOCATION ──
    sec_h = 2.8 * cm
    sec_y = body_y - sec_h
    header_bottom = draw_section_box(c, col_l_x, sec_y, col_l_w, sec_h, "DURÉE DE LOCATION")

    iy = header_bottom - 14
    ix = col_l_x + 8
    lw = 3.8 * cm

    start_str = f"{_fmt_date(contract.start_date)}"
    end_str = f"{_fmt_date(contract.end_date)}"

    draw_label_value(c, ix, iy, "Date de Départ :", start_str, label_w=lw)
    iy -= 16
    draw_label_value(c, ix, iy, "Date de Retour :", end_str, label_w=lw)
    iy -= 16
    draw_label_value(c, ix, iy, "Durée :", f"{contract.duration_days} Jour(s)",
                     value_color=ACCENT, label_w=lw)

    left_y = sec_y - 6

    # ── LE LOCATAIRE ──
    sec_h = 7.4 * cm
    sec_y = left_y - sec_h
    header_bottom = draw_section_box(c, col_l_x, sec_y, col_l_w, sec_h, "LE LOCATAIRE")

    iy = header_bottom - 13
    ix = col_l_x + 8
    lw = 3.2 * cm
    row_h = 14.5

    loc_fields = [
        ("Nom :", client.last_name or client.full_name or '—'),
        ("Prénom :", client.first_name or '—'),
        ("Date de naissance :", _fmt_date(client.birth_date)),
        ("Adresse :", (client.address or '—')[:40]),
        ("Tél :", client.phone or '—'),
        ("Permis N° :", client.drivers_license or '—'),
        ("Délivré le :", _fmt_date(_safe(client, 'license_delivered', None))),
        ("Nationalité :", client.nationality or '—'),
        ("CIN N° :", client.cin or '—'),
        ("Valable jusqu'au :", _fmt_date(_safe(client, 'cin_expiry', None))),
    ]

    for label, value in loc_fields:
        draw_label_value(c, ix, iy, label, value, label_w=lw)
        iy -= row_h

    left_y = sec_y - 6

    # ── 2ème CONDUCTEUR ──
    sec_h = 3.0 * cm
    sec_y = left_y - sec_h
    header_bottom = draw_section_box(c, col_l_x, sec_y, col_l_w, sec_h, "2ème CONDUCTEUR")
    # Draw X
    draw_big_x(c, col_l_x + 10, sec_y + 5, col_l_w - 20, sec_h - 28)

    left_y = sec_y - 6

    # ═══════════════════════════════════════════
    # RIGHT COLUMN
    # ═══════════════════════════════════════════
    right_y = body_y

    # ── PROLONGATION ──
    sec_h = 1.8 * cm
    sec_y = right_y - sec_h
    header_bottom = draw_section_box(c, col_r_x, sec_y, col_r_w, sec_h, "PROLONGATION DE LOCATION")
    iy = header_bottom - 14
    ix = col_r_x + 8
    draw_label_value(c, ix, iy, "Du : ...............................", "au : ...............................",
                     label_w=3.5 * cm)

    right_y = sec_y - 6

    # ── PAPIERS DU VÉHICULE ──
    sec_h = 2.4 * cm
    sec_y = right_y - sec_h
    header_bottom = draw_section_box(c, col_r_x, sec_y, col_r_w, sec_h, "PAPIERS DU VÉHICULE")

    iy = header_bottom - 14
    ix = col_r_x + 8
    papers = [
        ("Carte grise", True),
        ("Assurance", True),
        ("Autorisation", True),
        ("Visite technique", True),
        ("Att. vignette", True),
    ]
    px = ix
    for i, (name, checked) in enumerate(papers):
        col = i % 3
        row = i // 3
        px = ix + col * (col_r_w / 3 - 3)
        py = iy - row * 18
        draw_checkbox(c, px, py - 1, checked=checked)
        c.saveState()
        c.setFont('Helvetica', 7.5)
        c.setFillColor(TEXT_DARK)
        c.drawString(px + 12, py, name)
        c.restoreState()

    right_y = sec_y - 6

    # ── FRANCHISE ──
    sec_h = 2.2 * cm
    sec_y = right_y - sec_h
    header_bottom = draw_section_box(c, col_r_x, sec_y, col_r_w, sec_h, "FRANCHISE")
    iy = header_bottom - 14
    ix = col_r_x + 8

    c.saveState()
    c.setFont('Helvetica', 8)
    c.setFillColor(TEXT_DARK)
    c.drawString(ix, iy, 'Assurance "Tous risques" :')
    c.restoreState()
    draw_checkbox(c, ix + 4 * cm, iy - 1, checked=True)
    c.saveState()
    c.setFont('Helvetica-Bold', 8)
    c.setFillColor(TEXT_DARK)
    c.drawString(ix + 4 * cm + 12, iy, 'Oui')
    c.restoreState()
    draw_checkbox(c, ix + 5.3 * cm, iy - 1, checked=False)
    c.saveState()
    c.setFont('Helvetica-Bold', 8)
    c.setFillColor(TEXT_DARK)
    c.drawString(ix + 5.3 * cm + 12, iy, 'Non')
    c.restoreState()

    iy -= 18
    draw_label_value(c, ix, iy, "Franchise :", f"{_fmt_amount(contract.deposit)} DH",
                     value_color=ACCENT, label_w=2 * cm)

    right_y = sec_y - 6

    # ── ÉTAT DU VÉHICULE ──
    sec_h = 3.8 * cm
    sec_y = right_y - sec_h
    header_bottom = draw_section_box(c, col_r_x, sec_y, col_r_w, sec_h, "ÉTAT DU VÉHICULE")

    # Car diagram
    car_cx = col_r_x + col_r_w * 0.3
    car_cy = sec_y + sec_h / 2 - 6
    draw_car_diagram(c, car_cx, car_cy, scale=0.9)

    # Fuel gauge
    gauge_cx = col_r_x + col_r_w * 0.72
    gauge_cy = sec_y + sec_h / 2 + 6
    draw_fuel_gauge(c, gauge_cx, gauge_cy, radius=16)

    # KM info
    iy = sec_y + 10
    ix = col_r_x + 8
    draw_label_value(c, ix, iy, "KM Départ :", f"{contract.km_start or 0} km",
                     value_color=PRIMARY, label_w=2.2 * cm)
    km_end = _safe(contract, 'km_end', None)
    if km_end and km_end != '—':
        draw_label_value(c, ix + col_r_w / 2, iy, "KM Retour :",
                         f"{km_end} km", value_color=PRIMARY, label_w=2.2 * cm)

    right_y = sec_y - 6

    # ── TARIFICATION ──
    sec_h = 4.8 * cm
    sec_y = right_y - sec_h
    header_bottom = draw_section_box(c, col_r_x, sec_y, col_r_w, sec_h, "TARIFICATION")

    iy = header_bottom - 14
    ix = col_r_x + 8
    val_x = col_r_x + col_r_w - 10
    row_h = 15

    price_rows = [
        ("Prix par jour", f"{_fmt_amount(contract.price_per_day)} DH", False),
        ("Sous Total", f"{_fmt_amount(contract.total_amount)} DH", False),
        ("Frais de livraison", "0.00 DH", False),
        ("Frais de restitution", "0.00 DH", False),
    ]

    for label, value, is_bold in price_rows:
        c.saveState()
        c.setFont('Helvetica', 7.5)
        c.setFillColor(TEXT_MID)
        c.drawString(ix, iy, label)
        c.setFont('Helvetica-Bold' if is_bold else 'Helvetica', 7.5)
        c.setFillColor(TEXT_DARK)
        c.drawRightString(val_x, iy, value)
        c.restoreState()
        draw_dotted_line(c, ix, iy - 4, val_x)
        iy -= row_h

    # Total line (highlighted)
    iy -= 2
    c.saveState()
    draw_rounded_rect(c, ix - 4, iy - 5, col_r_w - 8, 16, r=3,
                      stroke=0, fill=1, fill_color=ACCENT_LIGHT)
    c.setFont('Helvetica-Bold', 9)
    c.setFillColor(PRIMARY)
    c.drawString(ix, iy, "TOTAL GÉNÉRAL")
    c.setFillColor(ACCENT)
    c.drawRightString(val_x, iy, f"{_fmt_amount(contract.total_amount)} DH")
    c.restoreState()

    iy -= 18
    advance = getattr(contract, 'advance_payment', None) or contract.total_amount
    draw_label_value(c, ix, iy, "Montant payé :", f"{_fmt_amount(advance)} DH",
                     label_w=2.5 * cm, value_color=CHECK_GREEN)
    iy -= row_h
    reste = float(contract.total_amount or 0) - float(advance or 0)
    draw_label_value(c, ix, iy, "Reste à payer :", f"{_fmt_amount(max(reste, 0))} DH",
                     label_w=2.5 * cm,
                     value_color=DANGER_RED if reste > 0 else CHECK_GREEN)

    right_y = sec_y - 6

    # ── MODE DE RÈGLEMENT ──
    sec_h = 1.4 * cm
    sec_y = right_y - sec_h
    header_bottom = draw_section_box(c, col_r_x, sec_y, col_r_w, sec_h, "MODE DE RÈGLEMENT")
    iy = header_bottom - 14
    ix = col_r_x + 8
    payments = [("Espèce", True), ("Chèque", False), ("Carte", False), ("Virement", False)]
    gap = col_r_w / 4 - 3
    for i, (name, checked) in enumerate(payments):
        px = ix + i * gap
        draw_checkbox(c, px, iy - 1, checked=checked)
        c.saveState()
        c.setFont('Helvetica', 7)
        c.setFillColor(TEXT_DARK)
        c.drawString(px + 12, iy, name)
        c.restoreState()

    right_y = sec_y

    # ── SIGNATURES ──────────────────────────────
    # Use the lowest of left_y or right_y
    sig_y_top = min(left_y, right_y) - 4
    sig_h = 2.8 * cm
    sig_y = sig_y_top - sig_h

    # Full width signature box
    draw_rounded_rect(c, MARGIN_L, sig_y, CONTENT_W, sig_h, r=5,
                      stroke=1, fill=1,
                      stroke_color=colors.HexColor('#E0E0E0'),
                      fill_color=WHITE)

    # 4 columns for signatures
    sig_cols = 4
    sig_col_w = CONTENT_W / sig_cols
    sig_titles = ["Le Locataire", "2ème Conducteur", "Le Loueur", "Retour du Véhicule"]

    for i, title in enumerate(sig_titles):
        sx = MARGIN_L + i * sig_col_w
        # Vertical separator
        if i > 0:
            c.saveState()
            c.setStrokeColor(colors.HexColor('#E0E0E0'))
            c.setLineWidth(0.5)
            c.line(sx, sig_y + 4, sx, sig_y + sig_h - 4)
            c.restoreState()
        # Title
        c.saveState()
        c.setFont('Helvetica-Bold', 7.5)
        c.setFillColor(PRIMARY)
        tw = c.stringWidth(title, 'Helvetica-Bold', 7.5)
        c.drawString(sx + (sig_col_w - tw) / 2, sig_y + sig_h - 14, title)
        c.restoreState()

    # X in 2nd conductor box
    draw_big_x(c, MARGIN_L + sig_col_w + 10, sig_y + 8,
               sig_col_w - 20, sig_h - 30)

    # Agency name in loueur box
    if agency:
        c.saveState()
        c.setFont('Helvetica', 7)
        c.setFillColor(TEXT_MID)
        loueur_x = MARGIN_L + 2 * sig_col_w + sig_col_w / 2
        c.drawCentredString(loueur_x, sig_y + sig_h / 2, agency.name)
        c.restoreState()

    # Stamp
    if agency and agency.stamp and agency.show_stamp_on_contract:
        try:
            stamp_path = agency.stamp.path
            if os.path.exists(stamp_path):
                stamp_x = MARGIN_L + 2 * sig_col_w + 8
                stamp_y = sig_y + 5
                c.drawImage(stamp_path, stamp_x, stamp_y,
                            width=sig_col_w - 16, height=sig_h - 25,
                            preserveAspectRatio=True, mask='auto')
        except Exception:
            pass

    # Return column info
    ret_x = MARGIN_L + 3 * sig_col_w + 8
    c.saveState()
    c.setFont('Helvetica', 6.5)
    c.setFillColor(TEXT_MID)
    c.drawString(ret_x, sig_y + sig_h - 28, "Date et Heure : .........................")
    c.drawString(ret_x, sig_y + sig_h - 40, "Lieu de retour : .........................")
    c.drawString(ret_x, sig_y + sig_h - 52, "KM retour : ...............................")
    c.restoreState()

    # ── FOOTER ──────────────────────────────────
    foot_y = sig_y - 8
    # Acceptance text
    c.saveState()
    c.setFont('Helvetica-Oblique', 6.5)
    c.setFillColor(TEXT_LIGHT)
    c.drawString(MARGIN_L, foot_y,
                 "J'ai lu et accepté les conditions stipulées au verso de ce contrat. "
                 "Le client est seul responsable des violations de la loi sur la circulation routière.")
    c.restoreState()

    foot_y -= 14

    # Gold separator
    c.saveState()
    c.setStrokeColor(ACCENT)
    c.setLineWidth(1.5)
    c.line(MARGIN_L, foot_y + 6, PAGE_W - MARGIN_R, foot_y + 6)
    c.restoreState()

    # Agency info footer
    if agency:
        c.saveState()
        c.setFont('Helvetica-Bold', 7.5)
        c.setFillColor(PRIMARY)
        c.drawCentredString(PAGE_W / 2, foot_y - 4, agency.name)
        c.setFont('Helvetica', 6.5)
        c.setFillColor(TEXT_MID)
        footer_line2 = f"{agency.address} - {agency.city} {agency.zip_code}"
        c.drawCentredString(PAGE_W / 2, foot_y - 14, footer_line2)
        footer_line3 = (f"Tél : {agency.phone_mobile}  |  "
                        f"Patente : {agency.patente}  |  "
                        f"IF : {agency.if_tax}  |  "
                        f"RC : {agency.rc}  |  "
                        f"ICE : {agency.ice}")
        c.drawCentredString(PAGE_W / 2, foot_y - 24, footer_line3)
        c.restoreState()

    # Bottom gold bar
    c.saveState()
    c.setFillColor(ACCENT)
    c.rect(0, 0, PAGE_W, 3, stroke=0, fill=1)
    c.restoreState()

    c.showPage()

    # ────────────────────────────────────────────
    # PAGE 2: CONDITIONS GÉNÉRALES
    # ────────────────────────────────────────────
    if agency and agency.conditions_generales:
        # Top gold bar
        c.saveState()
        c.setFillColor(ACCENT)
        c.rect(0, PAGE_H - 4, PAGE_W, 4, stroke=0, fill=1)
        c.restoreState()

        y = PAGE_H - MARGIN_T - 10

        # Title
        c.saveState()
        c.setFont('Helvetica-Bold', 16)
        c.setFillColor(PRIMARY)
        c.drawString(MARGIN_L, y, "CONDITIONS GÉNÉRALES")
        c.setStrokeColor(ACCENT)
        c.setLineWidth(2)
        c.line(MARGIN_L, y - 5, MARGIN_L + 6 * cm, y - 5)
        c.restoreState()

        y -= 22

        # Contract number subtitle
        c.saveState()
        c.setFont('Helvetica', 8)
        c.setFillColor(TEXT_MID)
        c.drawString(MARGIN_L, y, f"Contrat N° {contract.contract_number}")
        c.restoreState()

        y -= 18

        # Render conditions in a frame for proper text wrapping
        conditions_style = ParagraphStyle(
            'ConditionsText',
            fontName='Helvetica',
            fontSize=7.5,
            leading=11,
            textColor=TEXT_DARK,
            alignment=TA_JUSTIFY,
            spaceAfter=4,
        )
        conditions_title_style = ParagraphStyle(
            'ConditionsTitle',
            fontName='Helvetica-Bold',
            fontSize=8.5,
            leading=12,
            textColor=PRIMARY,
            spaceBefore=8,
            spaceAfter=3,
        )

        story = []
        for line in agency.conditions_generales.split('\n'):
            line = line.strip()
            if not line:
                story.append(Paragraph("<br/>", conditions_style))
                continue
            # Detect article headers (lines starting with "Article" or numbered)
            if line.lower().startswith('article') or (len(line) < 80 and line.endswith(':')):
                story.append(Paragraph(f"<b>{line}</b>", conditions_title_style))
            else:
                story.append(Paragraph(line, conditions_style))

        # Use a frame to render paragraphs
        frame_h = y - MARGIN_B - 30
        f = Frame(MARGIN_L, MARGIN_B + 30, CONTENT_W, frame_h,
                  leftPadding=0, bottomPadding=0,
                  rightPadding=0, topPadding=0)
        remaining = f.addFromList(story, c)

        # If there are remaining paragraphs, add more pages
        while remaining:
            c.showPage()
            # Top gold bar
            c.saveState()
            c.setFillColor(ACCENT)
            c.rect(0, PAGE_H - 4, PAGE_W, 4, stroke=0, fill=1)
            c.restoreState()
            # Bottom gold bar
            c.saveState()
            c.setFillColor(ACCENT)
            c.rect(0, 0, PAGE_W, 3, stroke=0, fill=1)
            c.restoreState()

            f = Frame(MARGIN_L, MARGIN_B + 10, CONTENT_W,
                      PAGE_H - MARGIN_T - MARGIN_B - 20,
                      leftPadding=0, bottomPadding=0,
                      rightPadding=0, topPadding=0)
            remaining = f.addFromList(remaining, c)

        # Bottom gold bar for conditions page
        c.saveState()
        c.setFillColor(ACCENT)
        c.rect(0, 0, PAGE_W, 3, stroke=0, fill=1)
        c.restoreState()

        # Footer on conditions page
        c.saveState()
        c.setFont('Helvetica', 6.5)
        c.setFillColor(TEXT_LIGHT)
        c.drawCentredString(PAGE_W / 2, 12,
                            f"{agency.name} — {agency.address}, {agency.city}")
        c.restoreState()

    c.save()
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="contrat_{contract.contract_number}.pdf"'
    )
    return response
