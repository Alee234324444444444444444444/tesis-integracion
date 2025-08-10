import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, Paragraph, SimpleDocTemplate, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from .models import Proforma, Analysis, CompanySettings, Resultado, Informe

def generate_proforma_pdf(proforma_id, output_folder="media/proformas/"):
    import os
    import traceback
    from django.http import Http404
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, Image
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from django.conf import settings
    from .models import Proforma, Analysis, CompanySettings

    try:
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
        styleTitle = ParagraphStyle('HeaderTitle', parent=styleN, alignment=1, fontSize=18, spaceAfter=10)

        # Línea horizontal superior
        linea_superior = Table([[""]], colWidths=[530])
        linea_superior.setStyle(TableStyle([
            ("LINEABOVE", (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        story.append(linea_superior)
        story.append(Spacer(1, 4))

        # Logo y encabezado con título (logo a la derecha)
        logo_path = os.path.join(settings.MEDIA_ROOT, "logos", "logo_empresa.png")
        logo_img = Image(logo_path, width=30 * mm, height=12 * mm) if os.path.exists(logo_path) else ""

        header_data = [
            [Paragraph(f"<b>PROFORMA N°: {proforma.proforma_number}</b>", styleTitle), logo_img]
        ]
        header_table = Table(header_data, colWidths=[400, 100])
        header_table.setStyle(TableStyle([
            ("ALIGN", (0, 0), (0, 0), "CENTER"),
            ("ALIGN", (1, 0), (1, 0), "RIGHT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 10))

        # Datos de empresa (una sola línea bajo el título)
        if company:
            empresa_linea = Paragraph(
                f"{company.company_name} • {company.company_address} • Tel: {company.company_phone} • Email: {company.company_email}",
                styles['Italic']
            )
            story.append(empresa_linea)
            story.append(Spacer(1, 8))

        # Datos del cliente (mismo estilo que informe)
        client_info = [
            [Paragraph("<b>FECHA:</b>", styleB), proforma.date.strftime("%d/%m/%Y")],
            [Paragraph("<b>CLIENTE:</b>", styleB), client.name],
            [Paragraph("<b>RUC:</b>", styleB), client.ruc],
            [Paragraph("<b>TELÉFONO:</b>", styleB), client.phone],
            [Paragraph("<b>EMAIL:</b>", styleB), client.email],
            [Paragraph("<b>DIRECCIÓN:</b>", styleB), client.address],
            [Paragraph("<b>CONTACTO:</b>", styleB), client.contact_person],
        ]
        client_table = Table(client_info, colWidths=[100, 400])
        client_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(client_table)
        story.append(Spacer(1, 14))

        # Tabla de ítems / análisis (encabezado verde como el informe)
        data = [["#", "Parámetro", "Unidad", "Método", "Técnica", "Precio Unitario", "Cantidad", "Subtotal"]]
        for i, a in enumerate(analyses, start=1):
            data.append([
                str(i),
                a.parameter,
                a.unit,
                a.method,
                a.technique,
                f"${a.unit_price:.2f}",
                str(a.quantity),
                f"${a.subtotal:.2f}",
            ])

        items_table = Table(
            data,
            hAlign='CENTER',
            colWidths=[30, 90, 55, 70, 70, 80, 55, 70]
        )
        items_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2d6a4f")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
        ]))
        story.append(items_table)
        story.append(Spacer(1, 14))

        # Totales (alineado a la derecha)
        if company and company.tax_rate is not None:
            iva_pct = int(company.tax_rate * 100)
        else:
            iva_pct = 12  # fallback

        totals = [
            [Paragraph("<b>Subtotal:</b>", styleB), f"${proforma.subtotal:.2f}"],
            [Paragraph(f"<b>IVA ({iva_pct}%):</b>", styleB), f"${proforma.tax_amount:.2f}"],
            [Paragraph("<b>Total:</b>", styleB), f"${proforma.total:.2f}"],
        ]
        totals_table = Table(totals, hAlign='RIGHT', colWidths=[120, 80])
        totals_table.setStyle(TableStyle([
            ("ALIGN", (1, 0), (1, -1), "RIGHT"),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
        ]))
        story.append(totals_table)
        story.append(Spacer(1, 18))

        # Mensaje final
        story.append(Paragraph("Gracias por confiar en nuestros servicios.", styles['Italic']))

        # Construir PDF y guardar URL
        doc.build(story)
        proforma.pdf_url = pdf_path
        proforma.save()
        return pdf_path

    except Exception as e:
        traceback.print_exc()
        raise Http404("Error al generar la proforma PDF.")

def generate_informe_pdf(proforma_id, output_folder="media/informes/"):
    import os
    import traceback
    from django.http import Http404
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, Image
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from django.conf import settings
    from .models import Proforma, Informe, Resultado, CompanySettings, Analysis

    try:
        proforma = Proforma.objects.get(id=proforma_id)
        informe = Informe.objects.filter(proforma=proforma).first()
        if not informe:
            raise Http404("No existe un informe asociado a esta proforma.")

        resultados = Resultado.objects.filter(informe=informe)
        company = CompanySettings.objects.first()
        client = proforma.client

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        pdf_filename = f"INF-{proforma.proforma_number}.pdf"
        pdf_path = os.path.join(output_folder, pdf_filename)

        doc = SimpleDocTemplate(pdf_path, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=40, bottomMargin=30)
        story = []
        styles = getSampleStyleSheet()
        styleN = styles['Normal']
        styleB = ParagraphStyle('Bold', parent=styleN, fontName='Helvetica-Bold')
        styleTitle = ParagraphStyle('HeaderTitle', parent=styleN, alignment=1, fontSize=18, spaceAfter=10)

        # Línea horizontal superior
        linea_superior = Table([[""]], colWidths=[530])
        linea_superior.setStyle(TableStyle([
            ("LINEABOVE", (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        story.append(linea_superior)
        story.append(Spacer(1, 4))

        # Logo y encabezado con título
        logo_path = os.path.join(settings.MEDIA_ROOT, "logos", "logo_empresa.png")
        logo_img = Image(logo_path, width=30 * mm, height=12 * mm) if os.path.exists(logo_path) else ""

        header_data = [
        [Paragraph(f"<b>INFORME TÉCNICO N°: {informe.codigo}</b>", styleTitle), logo_img]]
        header_table = Table(header_data, colWidths=[400, 100])
        header_table.setStyle(TableStyle([
            ("ALIGN", (0, 0), (0, 0), "CENTER"),
            ("ALIGN", (1, 0), (1, 0), "RIGHT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))

        story.append(header_table)
        story.append(Spacer(1, 10))

        # Datos del cliente
        client_info = [
            [Paragraph("<b>FECHA:</b>", styleB), informe.fecha_emision.strftime("%d/%m/%Y")],
            [Paragraph("<b>CLIENTE:</b>", styleB), client.name],
            [Paragraph("<b>RUC:</b>", styleB), client.ruc],
            [Paragraph("<b>TELÉFONO:</b>", styleB), client.phone],
            [Paragraph("<b>EMAIL:</b>", styleB), client.email],
            [Paragraph("<b>DIRECCIÓN:</b>", styleB), client.address],
            [Paragraph("<b>CONTACTO:</b>", styleB), client.contact_person],
        ]
        client_table = Table(client_info, colWidths=[100, 400])
        client_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(client_table)
        story.append(Spacer(1, 14))

        # Tabla de resultados
        data = [["#", "Parámetro", "Unidad", "Método", "Técnica", "Resultado", "Límite", "Incertidumbre"]]
        for i, r in enumerate(resultados, 1):
            tecnica = "-"
            tecnica_obj = Analysis.objects.filter(
                proforma=proforma, parameter=r.parameter, unit=r.unit, method=r.method
            ).first()
            if tecnica_obj:
                tecnica = tecnica_obj.technique
            data.append([
                str(i), r.parameter, r.unit, r.method, tecnica, r.resultados, r.limite, r.incertidumbre
            ])

        table = Table(data, hAlign='CENTER', colWidths=[30, 70, 60, 70, 70, 60, 60, 60])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2d6a4f")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
        ]))
        story.append(table)
        story.append(Spacer(1, 20))

        # Mensaje final
        story.append(Paragraph("Gracias por confiar en nuestros servicios.", styles['Italic']))

        doc.build(story)
        informe.pdf_url = pdf_path
        informe.save()
        return pdf_path

    except Exception as e:
        traceback.print_exc()
        raise Http404("Error al generar el informe PDF.")
