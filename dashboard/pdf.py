# dashboard/pdf.py
"""PDF en blanco y negro con la lista vertical de familias de una o más manzanas."""
from io import BytesIO

from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (KeepTogether, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)

NEGRO = colors.black
GRIS = colors.Color(0.9, 0.9, 0.9)

TITULO = ParagraphStyle("t", fontSize=18, leading=22, fontName="Helvetica-Bold", textColor=NEGRO)
SUBTITULO = ParagraphStyle("s", fontSize=10, leading=13, fontName="Helvetica", textColor=NEGRO)
CUADRA = ParagraphStyle("c", fontSize=12, leading=15, fontName="Helvetica-Bold", textColor=NEGRO)
CELDA = ParagraphStyle("td", fontSize=9, leading=11, fontName="Helvetica", textColor=NEGRO)
CABECERA = ParagraphStyle("th", fontSize=8.5, leading=10, fontName="Helvetica-Bold", textColor=NEGRO)
VACIO = ParagraphStyle("v", fontSize=9, leading=12, fontName="Helvetica-Oblique", textColor=NEGRO)

MAX_FILAS_JUNTAS = 12


def _esc(texto):
    return str(texto).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _plural(n, singular, plural):
    return f"{n} {singular if n == 1 else plural}"


def _intencion(familia):
    return familia.voto.get_intencion_display() if hasattr(familia, "voto") else "—"


def _tabla_familias(familias):
    filas = [[Paragraph(h, CABECERA) for h in
              ("N.°", "Familia", "Integ.", "Contacto", "Intención de voto")]]
    for f in familias:
        contacto = _esc(f.contacto_1 or "—")
        if f.contacto_2:
            contacto += "<br/>" + _esc(f.contacto_2)
        filas.append([
            Paragraph(_esc(f.numero_familia), CELDA),
            Paragraph(_esc(f.nombre_familia), CELDA),
            Paragraph(str(f.integrantes), CELDA),
            Paragraph(contacto, CELDA),
            Paragraph(_esc(_intencion(f)), CELDA),
        ])
    t = Table(filas, colWidths=[16 * mm, 62 * mm, 14 * mm, 44 * mm, 38 * mm], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), GRIS),
        ("LINEBELOW", (0, 0), (-1, 0), 1, NEGRO),
        ("LINEBELOW", (0, 1), (-1, -1), 0.4, NEGRO),
        ("BOX", (0, 0), (-1, -1), 0.8, NEGRO),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def _resumen(familias):
    conteo = {}
    for f in familias:
        if hasattr(f, "voto"):
            k = f.voto.get_intencion_display()
            conteo[k] = conteo.get(k, 0) + 1
    base = _plural(len(familias), "familia", "familias")
    partes = ", ".join(f"{k}: {n}" for k, n in sorted(conteo.items()))
    return f"{base} — {partes}" if partes else base


def _bloque_manzana(parcela, familias):
    """Encabezado + tabla. El encabezado nunca queda huérfano al pie de página."""
    cabecera = [Paragraph(f"Manzana {parcela.numero}", CUADRA),
                Paragraph(_resumen(familias), SUBTITULO), Spacer(1, 3 * mm)]
    if not familias:
        return [KeepTogether(cabecera + [Paragraph("Sin familias relevadas.", VACIO)]),
                Spacer(1, 7 * mm)]
    tabla = _tabla_familias(familias)
    if len(familias) <= MAX_FILAS_JUNTAS:
        return [KeepTogether(cabecera + [tabla]), Spacer(1, 7 * mm)]
    return [*cabecera, tabla, Spacer(1, 7 * mm)]


def generar_pdf(titulo, bloques, usuario, subtitulo=None):
    """`bloques`: lista de (parcela, [familias]). Devuelve los bytes del PDF."""
    buf = BytesIO()
    generado = timezone.localtime().strftime("%d/%m/%Y %H:%M")

    def pie(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(NEGRO)
        canvas.drawString(18 * mm, 10 * mm,
                          f"Confidencial — datos personales sensibles (Ley 25.326) · "
                          f"Generado {generado} por {usuario}")
        canvas.drawRightString(A4[0] - 18 * mm, 10 * mm, f"Página {doc.page}")
        canvas.restoreState()

    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                            topMargin=16 * mm, bottomMargin=18 * mm, title=titulo)
    total = sum(len(f) for _, f in bloques)
    historia = [Paragraph(_esc(titulo), TITULO)]
    if subtitulo:
        historia.append(Paragraph(_esc(subtitulo), SUBTITULO))
    historia.append(Paragraph(
        f"{_plural(len(bloques), 'manzana', 'manzanas')} · "
        f"{_plural(total, 'familia relevada', 'familias relevadas')}", SUBTITULO))
    historia.append(Spacer(1, 6 * mm))
    for parcela, familias in bloques:
        historia.extend(_bloque_manzana(parcela, familias))
    doc.build(historia, onFirstPage=pie, onLaterPages=pie)
    return buf.getvalue()
