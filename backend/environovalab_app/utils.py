import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, Paragraph, SimpleDocTemplate, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Table
from .models import Proforma, Analysis, CompanySettings, Resultado, Informe

def generate_proforma_pdf(proforma_id, output_folder="media/proformas/"):
    proforma = Proforma.objects.get(id=proforma_id)
    analyses = Analysis.objects.filter(proforma=proforma)
    company = CompanySettings.objects.first()
    client = proforma.client

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    pdf_filename = f"{proforma.proforma_number}.pdf"
    pdf_path = os.path.join(output_folder, pdf_filename)

    doc = SimpleDocTemplate(pdf_path, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=40, bottomMargin=30)
    story = []
    styles = getSampleStyleSheet()
    styleN = styles['Normal']
    styleB = ParagraphStyle('Bold', parent=styleN, fontName='Helvetica-Bold')
    styleTitle = ParagraphStyle('title', parent=styles['Title'], alignment=1, fontSize=16, spaceAfter=10)
    styleRight = ParagraphStyle('rightAlign', parent=styles['Normal'], alignment=2)

    # Cabecera con logo a la derecha
    header_data = []
    logo_cell = ""
    if company and company.company_logo and os.path.exists(company.company_logo):
        logo = Image(company.company_logo, width=60 * mm, height=60 * mm)
        logo.hAlign = 'RIGHT'
        logo_cell = logo
    header_data.append([
        Paragraph(f"<b>{company.company_name}</b><br/>Dirección: {company.company_address}<br/>Tel: {company.company_phone} | Email: {company.company_email}", styleN),
        logo_cell
    ])
    header_table = Table(header_data, colWidths=[350, 130])
    story.append(header_table)
    story.append(Spacer(1, 12))

    # Título con número
    story.append(Paragraph(f"<b>PROFORMA N°: {proforma.proforma_number}</b>", styleTitle))
    story.append(Paragraph(f"<b>Fecha:</b> {proforma.date.strftime('%d/%m/%Y')}", styleN))
    story.append(Spacer(1, 10))

    # Datos del cliente como tabla 2x3
    client_data = [
        [Paragraph("<b>Cliente:</b>", styleB), client.name, Paragraph("<b>RUC:</b>", styleB), client.ruc],
        [Paragraph("<b>Teléfono:</b>", styleB), client.phone, Paragraph("<b>Email:</b>", styleB), client.email],
        [Paragraph("<b>Dirección:</b>", styleB), client.address, Paragraph("<b>Contacto:</b>", styleB), client.contact_person],
    ]
    client_table = Table(client_data, colWidths=[70, 180, 70, 180])
    client_table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story.append(client_table)
    story.append(Spacer(1, 12))

    # Mostrar ítems
    for i, a in enumerate(analyses, start=1):
        story.append(Paragraph(f"<b>Ítem #{i} - {a.parameter}</b>", styleB))
        item_data = [[
            "Parámetro", "Unidad", "Método", "Técnica", "Precio", "Cantidad", "Subtotal"
        ], [
            a.parameter, a.unit, a.method, a.technique,
            f"${a.unit_price:.2f}", str(a.quantity), f"${a.subtotal:.2f}"
        ]]
        item_table = Table(item_data, hAlign='CENTER', colWidths=[70, 50, 70, 70, 60, 50, 60])
        item_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2d6a4f")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 9)
        ]))
        story.append(item_table)
        story.append(Spacer(1, 10))

    # Totales alineados derecha
    story.append(Paragraph(f"<b>Subtotal:</b> ${proforma.subtotal:.2f}", styleRight))
    story.append(Paragraph(f"<b>IVA ({company.tax_rate * 100:.0f}%):</b> ${proforma.tax_amount:.2f}", styleRight))
    story.append(Paragraph(f"<b>Total:</b> ${proforma.total:.2f}", styleRight))

    story.append(Spacer(1, 20))
    story.append(Paragraph("Gracias por confiar en nuestros servicios.", styles['Italic']))
    doc.build(story)

    proforma.pdf_url = f"/{output_folder}{pdf_filename}".replace("\\", "/")
    proforma.save()
    return pdf_path


def generate_informe_pdf(proforma_id, output_folder="media/informes/"):
    from django.http import Http404
    import traceback

    proforma = Proforma.objects.get(id=proforma_id)
    informe = Informe.objects.filter(proforma=proforma).first()

    if not informe:
        raise Http404("No existe un informe asociado a esta proforma.")

    resultados = Resultado.objects.filter(informe=informe)
    company = CompanySettings.objects.first()
    client = proforma.client

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    filename = f"INF-{proforma.proforma_number}.pdf"
    pdf_path = os.path.join(output_folder, filename)

    try:
        doc = SimpleDocTemplate(pdf_path, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=40, bottomMargin=30)
        story = []
        styles = getSampleStyleSheet()
        styleN = styles['Normal']
        styleB = ParagraphStyle('Bold', parent=styleN, fontName='Helvetica-Bold')
        styleTitle = ParagraphStyle('title', parent=styles['Title'], alignment=1, fontSize=16, spaceAfter=10)

        # Cabecera con logo a la derecha
        header_data = []
        logo_cell = ""
        if company and company.company_logo and os.path.exists(company.company_logo):
            logo = Image(company.company_logo, width=60 * mm, height=60 * mm)
            logo.hAlign = 'RIGHT'
            logo_cell = logo
        header_data.append([
            Paragraph(f"<b>{company.company_name}</b><br/>Dirección: {company.company_address}<br/>Tel: {company.company_phone} | Email: {company.company_email}", styleN),
            logo_cell
        ])
        header_table = Table(header_data, colWidths=[350, 130])
        story.append(header_table)
        story.append(Spacer(1, 12))

        # Título con número
        story.append(Paragraph(f"<b>INFORME N°: INF-{proforma.proforma_number}</b>", styleTitle))
        story.append(Paragraph(f"<b>Fecha:</b> {informe.fecha_emision.strftime('%d/%m/%Y')}", styleN))
        story.append(Spacer(1, 10))

        # Cliente
        client_data = [
            [Paragraph("<b>Cliente:</b>", styleB), client.name, Paragraph("<b>RUC:</b>", styleB), client.ruc],
            [Paragraph("<b>Teléfono:</b>", styleB), client.phone, Paragraph("<b>Email:</b>", styleB), client.email],
            [Paragraph("<b>Dirección:</b>", styleB), client.address, Paragraph("<b>Contacto:</b>", styleB), client.contact_person],
        ]
        client_table = Table(client_data, colWidths=[70, 180, 70, 180])
        client_table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
        story.append(client_table)
        story.append(Spacer(1, 10))

        # Muestra tomada por y procedimiento
        story.append(Paragraph(f"<b>Muestra tomada por:</b> {informe.muestra_tomada_por}", styleN))
        story.append(Paragraph(f"<b>Procedimiento:</b> {informe.procedimiento}", styleN))
        story.append(Spacer(1, 10))

        # Tabla de resultados
        data = [["Parámetro", "Método", "Unidades", "Resultado", "Límite", "Incertidumbre"]]
        for r in resultados:
            data.append([
                r.parameter, r.method, r.unit, r.resultados, r.limite, r.incertidumbre
            ])
        table = Table(data, hAlign='CENTER', colWidths=[80, 70, 50, 60, 60, 80])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2d6a4f")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 9)
        ]))
        story.append(table)
        story.append(Spacer(1, 20))
        story.append(Paragraph("Gracias por confiar en nuestros servicios.", styles['Italic']))

        doc.build(story)
        informe.pdf_url = f"/{output_folder}{filename}".replace("\\", "/")
        informe.save()
        return pdf_path

    except Exception as e:
        traceback.print_exc()
        raise Http404("Error al generar el informe PDF.")