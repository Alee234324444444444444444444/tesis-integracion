import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, Paragraph, SimpleDocTemplate, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
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
    styleH = styles['Heading1']

    if company and company.company_logo and os.path.exists(company.company_logo):
        logo = Image(company.company_logo, width=40*mm, height=40*mm)
        story.append(logo)
    story.append(Paragraph(f"<b>{company.company_name}</b>", styleH))
    story.append(Paragraph(f"Dirección: {company.company_address}", styleN))
    story.append(Paragraph(f"Tel: {company.company_phone} | Email: {company.company_email}", styleN))
    story.append(Spacer(1, 10))

    story.append(Paragraph(f"<b>PROFORMA N°:</b> {proforma.proforma_number}", styleN))
    story.append(Paragraph(f"<b>Fecha:</b> {proforma.date.strftime('%d/%m/%Y')}", styleN))
    story.append(Spacer(1, 8))
    story.append(Paragraph(f"<b>Cliente:</b> {client.name}", styleN))
    story.append(Paragraph(f"<b>RUC:</b> {client.ruc}", styleN))
    story.append(Paragraph(f"<b>Dirección:</b> {client.address}", styleN))
    story.append(Paragraph(f"<b>Teléfono:</b> {client.phone}", styleN))
    story.append(Paragraph(f"<b>Email:</b> {client.email}", styleN))
    story.append(Paragraph(f"<b>Contacto:</b> {client.contact_person}", styleN))
    story.append(Spacer(1, 10))

    data = [["#", "Parámetro", "Unidad", "Método", "Técnica", "Precio Unitario", "Cantidad", "Subtotal"]]
    for i, a in enumerate(analyses, start=1):
        data.append([
            str(i), a.parameter, a.unit, a.method, a.technique,
            f"${a.unit_price:.2f}", str(a.quantity), f"${a.subtotal:.2f}"
        ])
    table = Table(data, hAlign='LEFT')
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#d0efb1")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
    ]))
    story.append(table)
    story.append(Spacer(1, 12))

    story.append(Paragraph(f"<b>Subtotal:</b> ${proforma.subtotal:.2f}", styleN))
    story.append(Paragraph(f"<b>IVA ({company.tax_rate*100:.0f}%):</b> ${proforma.tax_amount:.2f}", styleN))
    story.append(Paragraph(f"<b>Total:</b> ${proforma.total:.2f}", styleN))

    story.append(Spacer(1, 24))
    story.append(Paragraph("Gracias por confiar en nuestros servicios.", styleN))

    doc.build(story)
    proforma.pdf_url = pdf_path
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
        styleH = styles['Heading1']

        if company and company.company_logo and os.path.exists(company.company_logo):
            logo = Image(company.company_logo, width=40 * mm, height=40 * mm)
            story.append(logo)
        story.append(Paragraph(f"<b>{company.company_name}</b>", styleH))
        story.append(Paragraph(f"Dirección: {company.company_address}", styleN))
        story.append(Paragraph(f"Tel: {company.company_phone} | Email: {company.company_email}", styleN))
        story.append(Spacer(1, 10))

        story.append(Paragraph(f"<b>INFORME TÉCNICO N°:</b> INF-{proforma.proforma_number}", styleN))
        story.append(Paragraph(f"<b>Fecha:</b> {informe.fecha_emision.strftime('%d/%m/%Y')}", styleN))
        story.append(Spacer(1, 8))
        story.append(Paragraph(f"<b>Cliente:</b> {client.name}", styleN))
        story.append(Paragraph(f"<b>RUC:</b> {client.ruc}", styleN))
        story.append(Paragraph(f"<b>Dirección:</b> {client.address}", styleN))
        story.append(Paragraph(f"<b>Teléfono:</b> {client.phone}", styleN))
        story.append(Paragraph(f"<b>Email:</b> {client.email}", styleN))
        story.append(Paragraph(f"<b>Contacto:</b> {client.contact_person}", styleN))
        story.append(Spacer(1, 10))

        data = [["#", "Parámetro", "Unidad", "Método", "Técnica", "Resultado", "Límite", "Incertidumbre"]]
        for i, r in enumerate(resultados, start=1):
            tecnica = "-"
            try:
                tecnica_obj = Analysis.objects.filter(
                    proforma=proforma, parameter=r.parameter, unit=r.unit, method=r.method
                ).first()
                tecnica = tecnica_obj.technique if tecnica_obj else "-"
            except:
                tecnica = "-"
            data.append([
                str(i), r.parameter, r.unit, r.method, tecnica, r.resultados, r.limite, r.incertidumbre
            ])

        table = Table(data, hAlign='LEFT')
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#d0efb1")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
        ]))
        story.append(table)
        story.append(Spacer(1, 24))
        story.append(Paragraph("Gracias por confiar en nuestros servicios.", styleN))

        doc.build(story)

        informe.pdf_url = pdf_path
        informe.save()

        return pdf_path

    except Exception as e:
        traceback.print_exc()
        raise Http404("Error al generar el informe PDF.")
