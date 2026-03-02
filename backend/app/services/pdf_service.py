from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    Image,
)
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from datetime import datetime

from app.models.models import Orden


def generar_pdf_orden(orden: Orden) -> BytesIO:
    """Generar PDF de recibo de orden"""

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter, topMargin=0.5 * inch, bottomMargin=0.5 * inch
    )
    elements = []
    styles = getSampleStyleSheet()


    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=24,
        textColor=colors.HexColor("#3E352F"),  # emily-dark
        spaceAfter=30,
        alignment=TA_CENTER,
    )

    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=colors.HexColor("#3E352F"),
        spaceAfter=12,
    )

    normal_style = ParagraphStyle(
        "CustomNormal",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#6B5B4F"),  # emily-taupe
    )


    title = Paragraph("Emily Designs", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.2 * inch))


    info_data = [
        ["Número de Orden:", orden.numero_orden],
        ["Fecha:", orden.fecha_orden.strftime("%d/%m/%Y %H:%M")],
        ["Estado:", orden.estado],
        ["Método de Pago:", orden.metodo_pago or "Stripe"],
    ]

    info_table = Table(info_data, colWidths=[2 * inch, 4 * inch])
    info_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#3E352F")),
                ("TEXTCOLOR", (1, 0), (1, -1), colors.HexColor("#6B5B4F")),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )

    elements.append(info_table)
    elements.append(Spacer(1, 0.3 * inch))


    elements.append(Paragraph("Dirección de Envío", heading_style))
    direccion = Paragraph(orden.direccion_envio, normal_style)
    elements.append(direccion)
    elements.append(Spacer(1, 0.3 * inch))


    elements.append(Paragraph("Productos", heading_style))

    items_data = [["Producto", "Cantidad", "Precio Unit.", "Subtotal"]]

    for item in orden.items:
        items_data.append(
            [
                item.nombre_producto,
                str(item.cantidad),
                f"${float(item.precio_unitario):.2f}",
                f"${float(item.subtotal):.2f}",
            ]
        )

    items_table = Table(
        items_data, colWidths=[3 * inch, 1 * inch, 1.25 * inch, 1.25 * inch]
    )
    items_table.setStyle(
        TableStyle(
            [
                # Header
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#3E352F")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 11),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                # Body
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 10),
                ("TEXTCOLOR", (0, 1), (-1, -1), colors.HexColor("#6B5B4F")),
                ("ALIGN", (1, 1), (-1, -1), "CENTER"),
                ("ALIGN", (0, 1), (0, -1), "LEFT"),
                ("BOTTOMPADDING", (0, 1), (-1, -1), 8),
                ("TOPPADDING", (0, 1), (-1, -1), 8),
                # Grid
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E5E5")),
            ]
        )
    )

    elements.append(items_table)
    elements.append(Spacer(1, 0.3 * inch))


    totales_data = [
        ["Subtotal:", f"${float(orden.subtotal):.2f}"],
        ["Envío:", f"${float(orden.costo_envio):.2f}"],
        ["Impuestos (12%):", f"${float(orden.impuestos):.2f}"],
        ["", ""],
        ["Total:", f"${float(orden.total):.2f}"],
    ]

    totales_table = Table(totales_data, colWidths=[4.5 * inch, 2 * inch])
    totales_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (0, 2), "Helvetica"),
                ("FONTNAME", (1, 0), (1, 2), "Helvetica-Bold"),
                ("FONTNAME", (0, 4), (-1, 4), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 2), 10),
                ("FONTSIZE", (0, 4), (-1, 4), 14),
                ("TEXTCOLOR", (0, 0), (0, 2), colors.HexColor("#6B5B4F")),
                ("TEXTCOLOR", (1, 0), (1, 2), colors.HexColor("#3E352F")),
                ("TEXTCOLOR", (0, 4), (-1, 4), colors.HexColor("#3E352F")),
                ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
                ("LINEABOVE", (0, 4), (-1, 4), 2, colors.HexColor("#3E352F")),
                ("BOTTOMPADDING", (0, 0), (-1, 2), 6),
                ("BOTTOMPADDING", (0, 4), (-1, 4), 12),
                ("TOPPADDING", (0, 4), (-1, 4), 12),
            ]
        )
    )

    elements.append(totales_table)
    elements.append(Spacer(1, 0.5 * inch))


    footer_style = ParagraphStyle(
        "Footer",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.HexColor("#9CA3AF"),
        alignment=TA_CENTER,
    )

    footer = Paragraph(
        "Gracias por tu compra en Emily Designs<br/>Moda Estética de Quevedo",
        footer_style,
    )
    elements.append(footer)


    doc.build(elements)
    buffer.seek(0)

    return buffer
