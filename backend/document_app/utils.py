from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO
from decimal import Decimal
from django.conf import settings
import os


def generate_proforma_pdf(proforma):
    """
    Genera un PDF de la proforma usando ReportLab
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20*mm, leftMargin=20*mm,
                           topMargin=20*mm, bottomMargin=20*mm)
    
    # Obtener estilos
    styles = getSampleStyleSheet()
    
    # Estilos personalizados
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.darkgreen
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        textColor=colors.darkgreen
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6
    )
    
    # Contenido del PDF
    story = []
    
    # Header con logo de la empresa (si existe)
    try:
        from .models import CompanySettings
        company = CompanySettings.objects.first()
        
        if company:
            # Información de la empresa
            company_info = f"""
            <b>{company.company_name}</b><br/>
            {company.company_address}<br/>
            Tel: {company.company_phone}<br/>
            Email: {company.company_email}<br/>
            RUC: {company.company_ruc}
            """
            story.append(Paragraph(company_info, normal_style))
            story.append(Spacer(1, 20))
    except:
        # Si no hay configuración, usar valores por defecto
        story.append(Paragraph("<b>ENVIRONOVALAB</b>", title_style))
    
    # Título de la proforma
    story.append(Paragraph(f"PROFORMA N° {proforma.proforma_number}", title_style))
    story.append(Spacer(1, 20))
    
    # Información del cliente
    story.append(Paragraph("DATOS DEL CLIENTE", subtitle_style))
    
    client_data = [
        ['Cliente:', proforma.client.name],
        ['RUC:', proforma.client.ruc],
        ['Dirección:', proforma.client.address],
        ['Teléfono:', proforma.client.phone],
        ['Email:', proforma.client.email],
        ['Contacto:', proforma.client.contact_person],
        ['Fecha:', proforma.date.strftime('%d/%m/%Y')]
    ]
    
    client_table = Table(client_data, colWidths=[40*mm, 120*mm])
    client_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    story.append(client_table)
    story.append(Spacer(1, 20))
    
    # Tabla de análisis
    story.append(Paragraph("DETALLE DE SERVICIOS", subtitle_style))
    
    # Headers de la tabla
    analysis_data = [
        ['PARÁMETRO', 'UNIDAD', 'MÉTODO/REF.', 'TÉCNICA', 'CANT.', 'P. UNIT.', 'SUBTOTAL']
    ]
    
    # Agrupar análisis por categoría
    categories = {}
    for analysis in proforma.analysis_set.all().order_by('order'):
        category = analysis.parameter.get_category_display()
        if category not in categories:
            categories[category] = []
        categories[category].append(analysis)
    
    # Agregar análisis agrupados por categoría
    for category, analyses in categories.items():
        # Agregar header de categoría
        analysis_data.append([
            Paragraph(f"<b>{category.upper()}</b>", ParagraphStyle('CategoryHeader', fontSize=11, textColor=colors.darkgreen)),
            '', '', '', '', '', ''
        ])
        
        # Agregar análisis de la categoría
        for analysis in analyses:
            analysis_data.append([
                analysis.parameter.name,
                analysis.unit,
                analysis.method.name,
                analysis.technique.name,
                str(analysis.quantity),
                f"${analysis.unit_price:.2f}",
                f"${analysis.subtotal:.2f}"
            ])
    
    # Crear tabla de análisis
    analysis_table = Table(analysis_data, colWidths=[50*mm, 20*mm, 35*mm, 35*mm, 15*mm, 20*mm, 25*mm])
    analysis_table.setStyle(TableStyle([
        # Header principal
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        
        # Contenido
        ('ALIGN', (4, 1), (-1, -1), 'RIGHT'),  # Cantidad, precios alineados a derecha
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        
        # Espaciado
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    
    story.append(analysis_table)
    story.append(Spacer(1, 20))
    
    # Totales
    totals_data = [
        ['', 'SUBTOTAL:', f"${proforma.subtotal:.2f}"],
        ['', 'IVA (12%):', f"${proforma.tax_amount:.2f}"],
        ['', 'TOTAL:', f"${proforma.total:.2f}"]
    ]
    
    totals_table = Table(totals_data, colWidths=[120*mm, 30*mm, 30*mm])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('LINEBELOW', (1, 0), (-1, 0), 0.5, colors.black),
        ('LINEBELOW', (1, 1), (-1, 1), 0.5, colors.black),
        ('LINEBELOW', (1, 2), (-1, 2), 2, colors.black),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    
    story.append(totals_table)
    story.append(Spacer(1, 30))
    
    # Términos y condiciones
    terms = """
    <b>TÉRMINOS Y CONDICIONES:</b><br/>
    • Esta proforma tiene validez de 30 días.<br/>
    • Los precios están expresados en dólares americanos.<br/>
    • El tiempo de entrega de resultados es de 5 a 10 días laborables.<br/>
    • El pago debe realizarse contra entrega de resultados.<br/>
    • Los análisis se realizan según métodos estándar reconocidos.<br/>
    """
    
    story.append(Paragraph(terms, normal_style))
    
    # Construir PDF
    doc.build(story)
    
    # Obtener el contenido del buffer
    pdf_content = buffer.getvalue()
    buffer.close()
    
    return pdf_content


def generate_proforma_preview(proforma):
    """
    Genera una vista previa HTML de la proforma para preview en el frontend
    """
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Proforma {proforma.proforma_number}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ text-align: center; color: #2d5a27; }}
            .client-info {{ margin: 20px 0; }}
            .client-info table {{ width: 100%; }}
            .client-info td {{ padding: 5px; }}
            .analysis-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            .analysis-table th {{ background-color: #2d5a27; color: white; padding: 8px; }}
            .analysis-table td {{ border: 1px solid #ccc; padding: 6px; }}
            .category-header {{ background-color: #f0f8f0; font-weight: bold; }}
            .totals {{ text-align: right; margin: 20px 0; }}
            .terms {{ margin-top: 30px; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>ENVIRONOVALAB</h1>
            <h2>PROFORMA N° {proforma.proforma_number}</h2>
        </div>
        
        <div class="client-info">
            <h3>DATOS DEL CLIENTE</h3>
            <table>
                <tr><td><strong>Cliente:</strong></td><td>{proforma.client.name}</td></tr>
                <tr><td><strong>RUC:</strong></td><td>{proforma.client.ruc}</td></tr>
                <tr><td><strong>Dirección:</strong></td><td>{proforma.client.address}</td></tr>
                <tr><td><strong>Teléfono:</strong></td><td>{proforma.client.phone}</td></tr>
                <tr><td><strong>Email:</strong></td><td>{proforma.client.email}</td></tr>
                <tr><td><strong>Fecha:</strong></td><td>{proforma.date.strftime('%d/%m/%Y')}</td></tr>
            </table>
        </div>
        
        <h3>DETALLE DE SERVICIOS</h3>
        <table class="analysis-table">
            <thead>
                <tr>
                    <th>PARÁMETRO</th>
                    <th>UNIDAD</th>
                    <th>MÉTODO/REF.</th>
                    <th>TÉCNICA</th>
                    <th>CANT.</th>
                    <th>P. UNIT.</th>
                    <th>SUBTOTAL</th>
                </tr>
            </thead>
            <tbody>
    """
    
    # Agrupar por categoría
    categories = {}
    for analysis in proforma.analysis_set.all().order_by('order'):
        category = analysis.parameter.get_category_display()
        if category not in categories:
            categories[category] = []
        categories[category].append(analysis)
    
    # Agregar filas agrupadas
    for category, analyses in categories.items():
        html_content += f'<tr class="category-header"><td colspan="7">{category.upper()}</td></tr>'
        for analysis in analyses:
            html_content += f"""
                <tr>
                    <td>{analysis.parameter.name}</td>
                    <td>{analysis.unit}</td>
                    <td>{analysis.method.name}</td>
                    <td>{analysis.technique.name}</td>
                    <td>{analysis.quantity}</td>
                    <td>${analysis.unit_price:.2f}</td>
                    <td>${analysis.subtotal:.2f}</td>
                </tr>
            """
    
    html_content += f"""
            </tbody>
        </table>
        
        <div class="totals">
            <p><strong>SUBTOTAL: ${proforma.subtotal:.2f}</strong></p>
            <p><strong>IVA (12%): ${proforma.tax_amount:.2f}</strong></p>
            <p><strong>TOTAL: ${proforma.total:.2f}</strong></p>
        </div>
        
        <div class="terms">
            <h4>TÉRMINOS Y CONDICIONES:</h4>
            <ul>
                <li>Esta proforma tiene validez de 30 días.</li>
                <li>Los precios están expresados en dólares americanos.</li>
                <li>El tiempo de entrega de resultados es de 5 a 10 días laborables.</li>
                <li>El pago debe realizarse contra entrega de resultados.</li>
            </ul>
        </div>
    </body>
    </html>
    """
    
    return html_content