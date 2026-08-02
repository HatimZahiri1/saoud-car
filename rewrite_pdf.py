import re

with open("core/views.py", "r") as f:
    content = f.read()

# Find the start and end of the admin_contract_pdf function
# It starts with "def admin_contract_pdf(request, contract_id):"
# and ends right before "def admin_contracts_export_csv(request):"

start_str = "def admin_contract_pdf(request, contract_id):"
end_str = "def admin_contracts_export_csv(request):"

start_idx = content.find(start_str)
end_idx = content.find(end_str)

if start_idx == -1 or end_idx == -1:
    print("Could not find start or end index.")
    exit(1)

new_func = """def admin_contract_pdf(request, contract_id):
    \"\"\"Générer un PDF pour un contrat (Design Moderne & Épuré).\"\"\"
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm, mm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    import io, os
    from django.conf import settings
    from django.utils import timezone

    contract = get_object_or_404(
        RentalContract.objects.select_related('client', 'car'),
        id=contract_id
    )

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=1.2*cm, rightMargin=1.2*cm, topMargin=1.2*cm, bottomMargin=1.2*cm)
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom colors
    COLOR_DARK = colors.HexColor('#0F172A')
    COLOR_GRAY = colors.HexColor('#64748B')
    COLOR_ACCENT = colors.HexColor('#2563EB')
    COLOR_LIGHT_BG = colors.HexColor('#F8FAFC')
    COLOR_BORDER = colors.HexColor('#E2E8F0')

    # Custom styles
    title_style = ParagraphStyle('Title', parent=styles['Title'], fontSize=20, textColor=COLOR_ACCENT, spaceAfter=2, fontName='Helvetica-Bold', alignment=TA_RIGHT)
    subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=9, textColor=COLOR_GRAY, alignment=TA_RIGHT, spaceAfter=2)
    section_heading = ParagraphStyle('SectionHeading', fontSize=10, textColor=COLOR_DARK, fontName='Helvetica-Bold', spaceBefore=12, spaceAfter=6)
    terms_title = ParagraphStyle('TermsTitle', fontSize=8, textColor=COLOR_DARK, fontName='Helvetica-Bold', spaceBefore=10, spaceAfter=4)
    terms_style = ParagraphStyle('TermsText', fontSize=6.5, textColor=colors.HexColor('#334155'), leading=8)
    small_footer = ParagraphStyle('Footer', fontSize=7, textColor=COLOR_GRAY, alignment=TA_CENTER)

    agency = AgencyInfo.objects.first()
    
    # Header
    logo_path = None
    if agency and agency.logo and os.path.exists(agency.logo.path):
        logo_path = agency.logo.path
    else:
        fallback_logo = os.path.join(settings.BASE_DIR, 'core', 'static', 'core', 'img', 'contlogo.png')
        if os.path.exists(fallback_logo):
            logo_path = fallback_logo
            
    left_elem = ''
    if logo_path:
        left_elem = Image(logo_path, width=3.5*cm, height=3.5*cm)
        
    right_elem = [
        Paragraph(agency.name if agency else "SAOUD CAR", title_style),
        Paragraph(agency.address if agency else "Ben Slimane", subtitle_style),
        Paragraph(f"Tél: {agency.phone_mobile if agency else '+212 661 395 495'}", subtitle_style),
        Spacer(1, 10),
        Paragraph(f"CONTRAT DE LOCATION N° {contract.contract_number}", ParagraphStyle('CN', parent=styles['Normal'], fontSize=11, fontName='Helvetica-Bold', textColor=COLOR_DARK, alignment=TA_RIGHT))
    ]
    header_table = Table([[left_elem, right_elem]], colWidths=[6*cm, 12.6*cm])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (1,0), (1,0), 'RIGHT'),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 5))

    # Helper function for modern tables
    def make_modern_table(data, col_widths):
        t = Table(data, colWidths=col_widths)
        t_style = [
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LINEBELOW', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ]
        for col in [0, 2]:
            t_style.append(('FONTNAME', (col, 0), (col, -1), 'Helvetica'))
            t_style.append(('FONTSIZE', (col, 0), (col, -1), 7.5))
            t_style.append(('TEXTCOLOR', (col, 0), (col, -1), COLOR_GRAY))
        for col in [1, 3]:
            t_style.append(('FONTNAME', (col, 0), (col, -1), 'Helvetica-Bold'))
            t_style.append(('FONTSIZE', (col, 0), (col, -1), 9))
            t_style.append(('TEXTCOLOR', (col, 0), (col, -1), COLOR_DARK))
        t.setStyle(TableStyle(t_style))
        return t

    # Client Info
    elements.append(Paragraph("INFORMATIONS DU CLIENT", section_heading))
    client_data = [
        ['NOM COMPLET', contract.client.full_name.upper(), 'CIN / PASSEPORT', contract.client.cin],
        ['TÉLÉPHONE', contract.client.phone, 'PERMIS DE CONDUIRE', contract.client.drivers_license or '—'],
        ['ADRESSE', contract.client.address or '—', 'VILLE', contract.client.city or '—'],
    ]
    elements.append(make_modern_table(client_data, [3.8*cm, 5.5*cm, 3.8*cm, 5.5*cm]))

    # Vehicle Info
    elements.append(Paragraph("DÉTAILS DU VÉHICULE & LOCATION", section_heading))
    car = contract.car
    vehicle_rental_data = [
        ['VÉHICULE', f"{car.get_brand_display()} {car.name}", 'IMMATRICULATION', car.license_plate or '—'],
        ['CATÉGORIE / CARBURANT', f"{car.get_category_display()} / {car.get_fuel_type_display()}", 'KILOMÉTRAGE DÉPART', f"{contract.km_start} km"],
        ['DATE DÉBUT', str(contract.start_date.strftime('%d/%m/%Y')), 'DATE FIN', str(contract.end_date.strftime('%d/%m/%Y'))],
    ]
    elements.append(make_modern_table(vehicle_rental_data, [3.8*cm, 5.5*cm, 3.8*cm, 5.5*cm]))

    # Pricing
    elements.append(Paragraph("TARIFICATION", section_heading))
    price_data = [
        ['PRIX PAR JOUR', f"{contract.price_per_day} MAD", 'CAUTION', f"{contract.deposit} MAD"],
        ['DURÉE', f"{contract.duration_days} jour(s)", 'MONTANT TOTAL', f"{contract.total_amount} MAD"]
    ]
    price_table = Table(price_data, colWidths=[3.8*cm, 5.5*cm, 3.8*cm, 5.5*cm])
    pt_style = [
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('BACKGROUND', (0,0), (-1,-1), COLOR_LIGHT_BG),
        ('LINEABOVE', (0,0), (-1,0), 1, COLOR_ACCENT),
        ('LINEBELOW', (0,-1), (-1,-1), 1, COLOR_ACCENT),
    ]
    for col in [0, 2]:
        pt_style.append(('FONTNAME', (col, 0), (col, -1), 'Helvetica'))
        pt_style.append(('FONTSIZE', (col, 0), (col, -1), 7.5))
        pt_style.append(('TEXTCOLOR', (col, 0), (col, -1), COLOR_GRAY))
    for col in [1, 3]:
        pt_style.append(('FONTNAME', (col, 0), (col, -1), 'Helvetica-Bold'))
        pt_style.append(('FONTSIZE', (col, 0), (col, -1), 9))
        pt_style.append(('TEXTCOLOR', (col, 0), (col, -1), COLOR_DARK))
    pt_style.append(('FONTSIZE', (3, 1), (3, 1), 11))
    pt_style.append(('TEXTCOLOR', (3, 1), (3, 1), COLOR_ACCENT))
    price_table.setStyle(TableStyle(pt_style))
    elements.append(price_table)

    # Terms
    if agency and agency.conditions_generales:
        elements.append(Paragraph("CONDITIONS GÉNÉRALES DE LOCATION", terms_title))
        for line in agency.conditions_generales.split('\\n'):
            line = line.strip()
            if line:
                elements.append(Paragraph(line, terms_style))

    # Signatures
    elements.append(Spacer(1, 10))
    dir_sig = ''
    if contract.director_signature and os.path.exists(contract.director_signature.path):
        dir_sig = Image(contract.director_signature.path, width=3.5*cm, height=1.2*cm)
            
    client_sig = ''
    if contract.client_signature and os.path.exists(contract.client_signature.path):
        client_sig = Image(contract.client_signature.path, width=3.5*cm, height=1.2*cm)

    stamp_path = None
    if agency and getattr(agency, 'stamp', None) and os.path.exists(agency.stamp.path) and agency.show_stamp_on_contract:
        stamp_path = agency.stamp.path
    else:
        fallback_stamp = os.path.join(settings.BASE_DIR, 'core', 'static', 'core', 'img', 'cachet.png')
        if os.path.exists(fallback_stamp) and (not agency or agency.show_stamp_on_contract):
            stamp_path = fallback_stamp
            
    stamp_img = ''
    if stamp_path:
        stamp_img = Image(stamp_path, width=3.5*cm, height=3.5*cm)

    sig_data = [
        ['LA SOCIÉTÉ (CACHET & SIGNATURE)', 'LE LOCATAIRE (SIGNATURE)'],
        [stamp_img, client_sig if client_sig else '\\n\\n\\n'],
        [dir_sig if dir_sig else '', contract.client.full_name]
    ]

    sig_table = Table(sig_data, colWidths=[9.3*cm, 9.3*cm])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 8),
        ('TEXTCOLOR', (0,0), (-1,0), COLOR_DARK),
        ('BACKGROUND', (0,0), (-1,0), COLOR_LIGHT_BG),
        ('TOPPADDING', (0,0), (-1,0), 4),
        ('BOTTOMPADDING', (0,0), (-1,0), 4),
        ('LINEABOVE', (0,0), (-1,0), 0.5, COLOR_BORDER),
        ('LINEBELOW', (0,0), (-1,0), 0.5, COLOR_BORDER),
    ]))
    elements.append(sig_table)

    # Footer
    elements.append(Spacer(1, 5))
    elements.append(Paragraph(
        f"Généré le {timezone.now().strftime('%d/%m/%Y %H:%M')} — {agency.name if agency else 'SAOUD CAR'} — ICE: {agency.ice if agency else 'N/A'}",
        small_footer
    ))

    doc.build(elements)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="contrat_{contract.contract_number}.pdf"'
    return response

"""

new_content = content[:start_idx] + new_func + content[end_idx:]

with open("core/views.py", "w") as f:
    f.write(new_content)

print("Replacement successful.")
