from django.http import HttpResponse
from django.utils.translation import gettext as _
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import getSampleStyleSheet
from ...models import Patient, BedAssignment, MedicalRecord, ICD10Entry, Ward, Bed, Room


def generatePDF(request, ward_id):
    """
    An export method giving a pdf containing all patients assigned to a ward

    :param ward_id: Ward id of the corresponding ward
    :type ward_id: id

    :return: A pdf containing all patients assigned to the corresponding ward
    :rtype: pdf
    """
    # Request ward
    ward = Ward.objects.get(id=ward_id)

    # Request patients
    patients = ward.patients

    # get patient data
    data = []
    for patient in patients:
        first_name = Paragraph(patient.first_name, style=getSampleStyleSheet()['Normal'])
        last_name = Paragraph(patient.last_name, style=getSampleStyleSheet()['Normal'])
        discharge_date = Paragraph(patient.current_discharge_date,
                                   style=getSampleStyleSheet()['Normal'])
        admission_date = Paragraph(patient.current_admission_date,
                                   style=getSampleStyleSheet()['Normal'])

        if not str(patient.current_diagnose) == "None":
            dia = str(patient.current_diagnose).split()
        else:
            dia = [""]

        data.append([discharge_date,
                     admission_date,
                     patient.current_room_short,
                     first_name,
                     last_name,
                     patient.gender,
                     dia[-1],
                     ""])

    # Split data into datasets
    dataset = [data[i:i + 5] for i in range(0, len(data), 5)]

    # Set Table Header
    header = ["Entlassung", "Aufnahme", "Raum", "Vorname", "Nachname", "Sex", "Diagnose", "Notizen"]

    # Create PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{ward.name}_patient_list.pdf"'

    # Set the page size to landscape
    doc = canvas.Canvas(response, pagesize=landscape(letter))
    doc.setTitle(f"Patientenliste {ward.name}")

    # Get size of PDF
    page_width, page_height = doc._pagesize

    # Add logo
    logo_path = "hospitool/static/images/logo-pdf.png"
    doc.drawImage(logo_path, 20, page_height - 60, width=150, height=50)

    # Create Title
    title = f"Patientenliste {ward.name}"
    doc.setFont("Helvetica-Bold", 20)
    text_width = doc.stringWidth(title, "Helvetica-Bold", 20)
    doc.drawString((page_width - text_width) / 2, page_height - 60, title)

    # Create table for every dataset
    for set in dataset:

        # Add Table Header to dataset
        chunkdata = [header] + set

        # Set different row heights for the header (first row) and the rest of the data
        row_heights = [30] + [80] * (len(chunkdata) - 1)

        # Design Table
        table = Table(chunkdata, colWidths=[70, 70, 50, 75, 75, 50, 50, 250], rowHeights=row_heights)
        style = TableStyle([
            # ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            # ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            # ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ])
        table.setStyle(style)
        table.wrapOn(doc, page_width, page_height)

        # Calculate y-position of the table
        y_pos = page_height - 100 - sum(row_heights)  # Berechne die Höhe der gesamten Tabelle

        # Add table to pdf
        table.drawOn(doc, 50, y_pos)

        # Create new page
        doc.showPage()

    # Save PDF
    doc.save()
    return response