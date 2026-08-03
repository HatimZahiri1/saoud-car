import io, os, math
from django.conf import settings
from django.utils import timezone
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, Flowable, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from core.models import RentalContract, AgencyInfo

# Custom Flowables for diagrams
class FuelGauge(Flowable):
    def __init__(self, level):
        Flowable.__init__(self)
        self.width = 60
        self.height = 30
        self.level = level
    def draw(self):
        c = self.canv
        c.setStrokeColor(colors.black)
        c.setLineWidth(1)
        # dashed arc
        c.setDash([2, 2])
        c.arc(5, 5, 55, 55, 0, 180)
        c.setDash()
        angle = math.pi - (self.level * math.pi)
        x = 30 + 20 * math.cos(angle)
        y = 5 + 20 * math.sin(angle)
        c.setStrokeColor(colors.red)
        c.setLineWidth(2)
        c.line(30, 5, x, y)
        c.setStrokeColor(colors.black)
        c.circle(30, 5, 2, fill=1)
        c.setFont("Times-Bold", 8)
        c.setFillColor(colors.black)
        c.drawString(0, 0, "E")
        c.drawString(55, 0, "F")

class CarDiagram(Flowable):
    def __init__(self):
        Flowable.__init__(self)
        self.width = 100
        self.height = 50
    def draw(self):
        c = self.canv
        c.setStrokeColor(colors.black)
        c.setLineWidth(1.2)
        c.setFillColor(colors.white)
        # body
        c.roundRect(10, 10, 80, 30, 8, fill=1)
        # windows
        c.rect(25, 12, 15, 26)
        c.rect(60, 12, 15, 26)
        c.setFillColor(colors.black)
        # wheels
        c.rect(15, 7, 12, 3, fill=1)
        c.rect(70, 7, 12, 3, fill=1)
        c.rect(15, 40, 12, 3, fill=1)
        c.rect(70, 40, 12, 3, fill=1)
        c.setStrokeColor(colors.black)
        c.setLineWidth(0.5)
        # steering wheel approx
        c.circle(35, 33, 2)

class BigX(Flowable):
    def __init__(self, w, h):
        Flowable.__init__(self)
        self.width = w
        self.height = h
    def draw(self):
        c = self.canv
        c.setStrokeColor(colors.black)
        c.setLineWidth(2)
        c.line(0, 0, self.width, self.height)
        c.line(0, self.height, self.width, 0)

def generate_contract_pdf(request, contract_id):
    contract = get_object_or_404(RentalContract.objects.select_related('client', 'car'), id=contract_id)
    agency = AgencyInfo.objects.first()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=1*cm, rightMargin=1*cm, topMargin=0.8*cm, bottomMargin=0.8*cm)
    elements = []
    styles = getSampleStyleSheet()

    COLOR_BLACK = colors.black
    COLOR_DARK_GREY = colors.HexColor('#333333')
    COLOR_L_GREY = colors.HexColor('#F2F2F2')
    
    t_style_header = ParagraphStyle('TStyle', fontName='Times-Bold', fontSize=10, textColor=colors.white, alignment=TA_CENTER)
    label_style = ParagraphStyle('LStyle', fontName='Times-Roman', fontSize=9, leading=12)
    val_style = ParagraphStyle('VStyle', fontName='Times-Bold', fontSize=9, leading=12)

    def create_box(title, content_obj, width):
        p = Paragraph(title, t_style_header)
        t = Table([[p], [content_obj]], colWidths=[width])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,0), COLOR_DARK_GREY),
            ('ALIGN', (0,0), (0,0), 'CENTER'),
            ('VALIGN', (0,0), (0,0), 'MIDDLE'),
            ('ROUNDEDCORNERS', (0,0), (-1,-1), [6,6,6,6]),
            ('BOX', (0,0), (-1,-1), 1.5, COLOR_BLACK),
            ('LINEBELOW', (0,0), (0,0), 1.5, COLOR_BLACK),
            ('TOPPADDING', (0,0), (0,0), 2),
            ('BOTTOMPADDING', (0,0), (0,0), 2),
            ('LEFTPADDING', (0,1), (0,1), 4),
            ('RIGHTPADDING', (0,1), (0,1), 4),
            ('TOPPADDING', (0,1), (0,1), 4),
            ('BOTTOMPADDING', (0,1), (0,1), 4),
        ]))
        return t

    def cb(checked=False):
        t = Table([['X' if checked else '']], colWidths=[12], rowHeights=[12])
        t.setStyle(TableStyle([
            ('BOX', (0,0), (-1,-1), 1.5, COLOR_BLACK),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 1),
            ('TOPPADDING', (0,0), (-1,-1), 0),
        ]))
        return t

    # 1. HEADER
    logo_path = agency.logo.path if agency and agency.logo and os.path.exists(agency.logo.path) else None
    if not logo_path:
        fallback = os.path.join(settings.BASE_DIR, 'core', 'static', 'core', 'img', 'contlogo.png')
        if os.path.exists(fallback): logo_path = fallback
    left_elem = Image(logo_path, width=4*cm, height=2.5*cm) if logo_path else ''

    title_p = Paragraph("CONTRAT DE LOCATION", ParagraphStyle('TitleP', fontName='Times-Bold', fontSize=20, alignment=TA_RIGHT))
    num_p = Paragraph(f"N° #{contract.contract_number}", ParagraphStyle('NumP', fontName='Times-Bold', fontSize=12, alignment=TA_CENTER))
    num_t = Table([[num_p]], colWidths=[4*cm])
    num_t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_L_GREY),
        ('ROUNDEDCORNERS', (0,0), (-1,-1), [5,5,5,5]),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    
    right_t = Table([[title_p], [Spacer(1, 5)], [num_t]], colWidths=[10*cm])
    right_t.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'RIGHT')]))

    header_t = Table([[left_elem, right_t]], colWidths=[8*cm, 11*cm])
    header_t.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('ALIGN', (1,0), (1,0), 'RIGHT')]))
    elements.append(header_t)
    elements.append(Spacer(1, 10))

    # 2. DOTTED INFO ROW
    info_data = [
        [Paragraph("Fait le :", label_style), Paragraph(str(contract.created_at.strftime('%d/%m/%Y')), val_style), Paragraph("Marque :", label_style), Paragraph(contract.car.get_brand_display(), val_style)],
        [Paragraph("Lieu de livraison :", label_style), Paragraph(getattr(contract, 'delivery_location', '') or '—', val_style), Paragraph("Immatriculation :", label_style), Paragraph(contract.car.license_plate or '—', val_style)],
        [Paragraph("Lieu de reprise :", label_style), Paragraph(getattr(contract, 'return_location', '') or '—', val_style), Paragraph("Agent Commercial :", label_style), Paragraph(getattr(contract, 'agent_name', '') or '—', val_style)],
    ]
    info_t = Table(info_data, colWidths=[3*cm, 6.5*cm, 3*cm, 6.5*cm])
    info_t.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
        ('LINEBELOW', (1,0), (1,-1), 1, COLOR_BLACK, 'round', (1,2)), # dotted
        ('LINEBELOW', (3,0), (3,-1), 1, COLOR_BLACK, 'round', (1,2)),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('TOPPADDING', (0,0), (-1,-1), 2),
    ]))
    box_info = Table([[info_t]], colWidths=[19*cm])
    box_info.setStyle(TableStyle([('BOX', (0,0), (-1,-1), 1, COLOR_BLACK)]))
    elements.append(box_info)
    elements.append(Spacer(1, 10))

    # 3. MAIN BODY (LEFT & RIGHT)
    
    # --- LEFT COLUMN ---
    # DUREE
    duree_data = [
        [Paragraph("Date et Heure Départ :", label_style), Paragraph(f"{contract.start_date.strftime('%d/%m/%Y')} à {getattr(contract, 'start_time', '').strftime('%H:%M') if getattr(contract, 'start_time', '') else '' }", val_style)],
        [Paragraph("Date et Heure Retour :", label_style), Paragraph(f"{contract.end_date.strftime('%d/%m/%Y')} à {getattr(contract, 'end_time', '').strftime('%H:%M') if getattr(contract, 'end_time', '') else '' }", val_style)],
        [Paragraph("Durée de location :", label_style), Paragraph(f"{contract.duration_days} Jours", val_style)],
    ]
    t_duree = Table(duree_data, colWidths=[4*cm, 4.5*cm])
    t_duree.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('LEFTPADDING', (0,0), (-1,-1), 0), ('BOTTOMPADDING', (0,0), (-1,-1), 2)]))
    box_duree = create_box("DURÉE DE LOCATION", t_duree, 9*cm)

    # LOCATAIRE
    client = contract.client
    loc_data = [
        [Paragraph("Nom :", label_style), Paragraph(client.last_name or client.full_name, val_style)],
        [Paragraph("Prénom :", label_style), Paragraph(client.first_name or '', val_style)],
        [Paragraph("Date de naissance :", label_style), Paragraph(str(client.birth_date.strftime('%d/%m/%Y') if client.birth_date else '—'), val_style)],
        [Paragraph("Adresse :", label_style), Paragraph(client.address or '—', val_style)],
        [Paragraph("Tél :", label_style), Paragraph(client.phone, val_style)],
        [Paragraph("Permis N° :", label_style), Paragraph(client.drivers_license or '—', val_style)],
        [Paragraph("Délivré, le :", label_style), Paragraph(str(getattr(client, 'license_delivered', None).strftime('%d/%m/%Y') if getattr(client, 'license_delivered', None) else '—'), val_style)],
        [Paragraph("Nationalité :", label_style), Paragraph(client.nationality or '—', val_style)],
        [Paragraph("CIN N° :", label_style), Paragraph(client.cin, val_style)],
        [Paragraph("Valable Jusqu'au :", label_style), Paragraph(str(getattr(client, 'cin_expiry', None).strftime('%d/%m/%Y') if getattr(client, 'cin_expiry', None) else '—'), val_style)],
    ]
    t_loc = Table(loc_data, colWidths=[3.5*cm, 5*cm])
    t_loc.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('LEFTPADDING', (0,0), (-1,-1), 0), ('BOTTOMPADDING', (0,0), (-1,-1), 2)]))
    box_loc = create_box("LE LOCATAIRE", t_loc, 9*cm)

    # 2EME CONDUCTEUR
    # Just a big X since no data model for 2nd driver
    t_cond2 = Table([[BigX(8*cm, 3.5*cm)]], colWidths=[8.5*cm], rowHeights=[4*cm])
    t_cond2.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
    box_cond2 = create_box("2ème CONDUCTEUR", t_cond2, 9*cm)

    left_col = Table([[box_duree], [Spacer(1, 5)], [box_loc], [Spacer(1, 5)], [box_cond2]])
    left_col.setStyle(TableStyle([('LEFTPADDING', (0,0), (-1,-1), 0), ('RIGHTPADDING', (0,0), (-1,-1), 0)]))


    # --- RIGHT COLUMN ---
    # PROLONGATION
    prol_data = [[Paragraph("Du :", label_style)], [Paragraph("au :", label_style)], [Paragraph("Durée:", label_style)]]
    t_prol = Table(prol_data)
    t_prol.setStyle(TableStyle([('LEFTPADDING', (0,0), (-1,-1), 0)]))
    box_prol = create_box("PROLONGATION DE LOCATION", t_prol, 9.5*cm)

    # PAPIERS
    pap_data = [
        [cb(True), Paragraph("Carte grise", label_style), cb(True), Paragraph("Visite Technique", label_style)],
        [cb(True), Paragraph("Assurance", label_style), cb(True), Paragraph("Attestation vignette", label_style)],
        [cb(True), Paragraph("Autorisation de circulation", label_style), '', ''],
    ]
    t_pap = Table(pap_data, colWidths=[0.5*cm, 4*cm, 0.5*cm, 4*cm])
    t_pap.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('LEFTPADDING', (0,0), (-1,-1), 0)]))
    box_pap = create_box("PAPIERS DE VEHICULE", t_pap, 9.5*cm)

    # FRANCHISE
    fran_data = [
        [Paragraph("Assurance \"Tous risques\" :", val_style), '', '', ''],
        ['', cb(True), Paragraph("Oui", val_style), cb(False), Paragraph("Non", val_style)],
        [Paragraph(f"Franchise : {contract.deposit} DH", val_style), '', '', '']
    ]
    t_fran = Table(fran_data, colWidths=[3.5*cm, 0.5*cm, 1*cm, 0.5*cm, 3.5*cm])
    t_fran.setStyle(TableStyle([('ALIGN', (2,0), (-1,-1), 'LEFT'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('ALIGN', (0,2), (0,2), 'CENTER'), ('SPAN', (0,2), (-1,2))]))
    box_fran = create_box("FRANCHISE", t_fran, 9.5*cm)

    # ETAT VEHICULE
    etat_data = [
        [CarDiagram(), FuelGauge(0.75)],
        [Paragraph(f"KM Départ : {contract.km_start} km", val_style), ''],
        [Paragraph("Observations : ...........................................................", label_style), '']
    ]
    t_etat = Table(etat_data, colWidths=[5*cm, 4*cm])
    t_etat.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('SPAN', (0,1), (1,1)), ('SPAN', (0,2), (1,2))]))
    box_etat = create_box("ETAT DU VEHICULE", t_etat, 9.5*cm)

    # PRIX
    prix_data = [
        [Paragraph("Prix par jour :", label_style), Paragraph(f"{contract.price_per_day} DH", val_style)],
        [Paragraph("Sous Total :", val_style), Paragraph(f"{contract.total_amount} DH", val_style)],
        [Paragraph("Frais de livraison :", label_style), Paragraph("0.00 DH", val_style)],
        [Paragraph("Frais de Restitution :", label_style), Paragraph("0.00 DH", val_style)],
        [Paragraph("TOTAL GÉNÉRAL :", val_style), Paragraph(f"{contract.total_amount} DH", val_style)],
        [Paragraph("MONTANT PAYÉ :", val_style), Paragraph(f"{getattr(contract, 'advance_payment', 0)} DH" if getattr(contract, 'advance_payment', 0) else f"{contract.total_amount} DH", val_style)],
        [Paragraph("LE RESTE A PAYER:", val_style), Paragraph("0.00 DH", val_style)],
    ]
    t_prix = Table(prix_data, colWidths=[6*cm, 3*cm])
    t_prix.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, COLOR_BLACK, 'round', (1,2)),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('TOPPADDING', (0,0), (-1,-1), 2),
    ]))
    
    # MODE REGLEMENT
    reg_title = Table([[Paragraph("Mode de Réglement", t_style_header)]], colWidths=[5*cm], style=[('ROUNDEDCORNERS', (0,0), (-1,-1), [5,5,5,5]), ('BACKGROUND', (0,0), (-1,-1), COLOR_DARK_GREY), ('ALIGN', (0,0), (-1,-1), 'CENTER')])
    reg_data = [
        [cb(True), Paragraph("Espèce", label_style), cb(False), Paragraph("Chèque", label_style), cb(False), Paragraph("Carte bancaire", label_style), cb(False), Paragraph("Virement", label_style)]
    ]
    t_reg_checks = Table(reg_data, colWidths=[0.5*cm, 1.5*cm, 0.5*cm, 1.5*cm, 0.5*cm, 2.3*cm, 0.5*cm, 1.7*cm])
    t_reg = Table([[reg_title], [t_reg_checks]], style=[('ALIGN', (0,0), (0,0), 'CENTER'), ('BOX', (0,0), (-1,-1), 1.5, COLOR_BLACK), ('ROUNDEDCORNERS', (0,0), (-1,-1), [6,6,6,6]), ('TOPPADDING', (0,0), (-1,-1), 4)])

    right_col = Table([
        [box_prol], [Spacer(1, 5)], 
        [box_pap], [Spacer(1, 5)], 
        [box_fran], [Spacer(1, 5)], 
        [box_etat], [Spacer(1, 5)], 
        [t_prix], [Spacer(1, 5)],
        [t_reg]
    ])
    right_col.setStyle(TableStyle([('LEFTPADDING', (0,0), (-1,-1), 0), ('RIGHTPADDING', (0,0), (-1,-1), 0)]))

    # Assemble Body
    body = Table([[left_col, right_col]], colWidths=[9.5*cm, 10*cm])
    body.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('LEFTPADDING', (0,0), (-1,-1), 0)]))
    elements.append(body)
    elements.append(Spacer(1, 10))

    # 4. SIGNATURES
    sig_data = [
        [Paragraph("Le Locataire", val_style), Paragraph("2ème Conducteur", val_style), Paragraph("Le Loueur", val_style), Paragraph("Date et signature du retour", val_style)],
        ['', BigX(3*cm, 2*cm), Paragraph(agency.name if agency else "SAOUD CAR", val_style), Paragraph("Date et Heure :<br/>Lieu de retour :", label_style)]
    ]
    t_sig = Table(sig_data, colWidths=[4.7*cm, 4.7*cm, 4.7*cm, 4.9*cm], rowHeights=[1*cm, 3*cm])
    t_sig.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOX', (0,0), (-1,-1), 1.5, COLOR_BLACK),
        ('ROUNDEDCORNERS', (0,0), (-1,-1), [6,6,6,6]),
        ('INNERGRID', (0,0), (-1,-1), 1, COLOR_BLACK),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(t_sig)

    # 5. FOOTER
    elements.append(Spacer(1, 5))
    elements.append(Paragraph("J'ai lu et accepté les conditions stipulées ci-contre au verso de ce contrat. Le client est seul responsable des violations de la loi sur la circulation routière.", ParagraphStyle('Foot', fontSize=8)))
    elements.append(Spacer(1, 5))
    footer_data = [[Paragraph(f"<b>{agency.name if agency else 'SAOUD CAR'}</b><br/>{agency.address if agency else ''}<br/>Tél : {agency.phone_mobile if agency else ''}<br/>Patente: {agency.patente if agency else ''} - IF: {agency.if_tax if agency else ''} - RC: {agency.rc if agency else ''}", ParagraphStyle('F', alignment=TA_CENTER, fontSize=8, leading=10))]]
    t_foot = Table(footer_data, colWidths=[19*cm])
    t_foot.setStyle(TableStyle([('LINEABOVE', (0,0), (-1,-1), 1.5, colors.orange)]))
    elements.append(t_foot)

    # 6. CONDITIONS GENERALES (Page 2)
    if agency and agency.conditions_generales:
        elements.append(Spacer(1, 0)) # To force page break? No, let reportlab wrap automatically. Actually we should force PageBreak.
        from reportlab.platypus import PageBreak
        elements.append(PageBreak())
        elements.append(Paragraph("CONDITIONS GÉNÉRALES", ParagraphStyle('CondTitle', fontSize=12, fontName='Helvetica-Bold', spaceAfter=10)))
        terms_style = ParagraphStyle('TermsText', fontSize=9, leading=12)
        for line in agency.conditions_generales.split('\n'):
            line = line.strip()
            if line:
                elements.append(Paragraph(line, terms_style))

    doc.build(elements)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="contrat_{contract.contract_number}.pdf"'
    return response

