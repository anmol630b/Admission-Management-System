import re

new_func = '''# =========================
# STUDENT ID CARD PDF
# =========================
@login_required
def student_id_card(request):
    from reportlab.lib.utils import ImageReader
    import os, io

    admission = Admission.objects.filter(email=request.user.email).last()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="UniVio_ID_{request.user.username}.pdf"'

    W, H = 360, 600
    p = canvas.Canvas(response, pagesize=(W, H))

    p.setFillColor(colors.HexColor('#0f0f1a'))
    p.rect(0, 0, W, H, fill=True, stroke=False)

    p.setFillColor(colors.HexColor('#ffcc00'))
    p.rect(0, H - 10, W, 10, fill=True, stroke=False)
    p.rect(0, 0, 6, H, fill=True, stroke=False)
    p.rect(W - 6, 0, 6, H, fill=True, stroke=False)

    p.setFillColor(colors.HexColor('#ffcc00'))
    p.circle(W / 2, H - 52, 28, fill=True, stroke=False)
    p.setFillColor(colors.HexColor('#0f0f1a'))
    p.setFont("Helvetica-Bold", 20)
    p.drawCentredString(W / 2, H - 60, "U")

    p.setFillColor(colors.HexColor('#ffcc00'))
    p.setFont("Helvetica-Bold", 24)
    p.drawCentredString(W / 2, H - 98, "UNIVIO")

    p.setFillColor(colors.HexColor('#aaaacc'))
    p.setFont("Helvetica", 7.5)
    p.drawCentredString(W / 2, H - 112, "COLLEGE OF EXCELLENCE  •  EST. 2010")

    p.setStrokeColor(colors.HexColor('#ffcc00'))
    p.setLineWidth(0.8)
    p.line(30, H - 122, W - 30, H - 122)

    p.setFillColor(colors.HexColor('#ffcc00'))
    p.setFont("Helvetica-Bold", 9)
    p.drawCentredString(W / 2, H - 136, "STUDENT IDENTITY CARD")

    photo_cx = W / 2
    photo_cy = H - 210
    p.setStrokeColor(colors.HexColor('#ffcc00'))
    p.setLineWidth(3)
    p.circle(photo_cx, photo_cy, 50, fill=False, stroke=True)

    if request.user.profile_photo:
        try:
            photo_path = request.user.profile_photo.path
            if os.path.exists(photo_path):
                p.drawImage(ImageReader(photo_path), photo_cx - 46, photo_cy - 46, width=92, height=92, preserveAspectRatio=True, mask='auto')
        except Exception:
            pass
    else:
        p.setFillColor(colors.HexColor('#1e1e3a'))
        p.circle(photo_cx, photo_cy, 46, fill=True, stroke=False)
        p.setFillColor(colors.HexColor('#ffcc00'))
        p.setFont("Helvetica-Bold", 34)
        p.drawCentredString(photo_cx, photo_cy - 13, request.user.username[0].upper())

    name_y = photo_cy - 68
    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 15)
    name_display = admission.name.upper() if admission and admission.name else request.user.username.upper()
    p.drawCentredString(W / 2, name_y, name_display)

    badge_y = name_y - 26
    if admission:
        badge_w = 110
        p.setFillColor(colors.HexColor('#ffcc00'))
        p.roundRect(W/2 - badge_w/2, badge_y - 6, badge_w, 20, 10, fill=True, stroke=False)
        p.setFillColor(colors.HexColor('#0f0f1a'))
        p.setFont("Helvetica-Bold", 9)
        p.drawCentredString(W / 2, badge_y + 4, admission.course)

    info_top = badge_y - 24
    info_items = [
        ("Student ID", f"UNV{request.user.id:05d}"),
        ("Username", request.user.username),
        ("Email", request.user.email if len(request.user.email) <= 32 else request.user.email[:30] + ".."),
        ("Phone", request.user.phone if request.user.phone else "Not Provided"),
        ("Valid Till", "May 2027"),
    ]

    row_h = 34
    box_h = len(info_items) * row_h + 20
    box_y = info_top - box_h

    p.setFillColor(colors.HexColor('#16162a'))
    p.roundRect(18, box_y, W - 36, box_h, 10, fill=True, stroke=False)

    y = info_top - 18
    for label, value in info_items:
        p.setFillColor(colors.HexColor('#888899'))
        p.setFont("Helvetica", 7)
        p.drawString(32, y, label.upper())
        p.setFillColor(colors.white)
        p.setFont("Helvetica-Bold", 10)
        p.drawString(32, y - 14, value)
        p.setStrokeColor(colors.HexColor('#2a2a45'))
        p.setLineWidth(0.4)
        p.line(32, y - 19, W - 32, y - 19)
        y -= row_h

    try:
        import qrcode
        qr_data = f"UNIVIO|{request.user.username}|UNV{request.user.id:05d}|{request.user.email}"
        qr_img = qrcode.make(qr_data)
        qr_buffer = io.BytesIO()
        qr_img.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)
        qr_size = 55
        qr_x = W - qr_size - 20
        qr_y = 42
        p.drawImage(ImageReader(qr_buffer), qr_x, qr_y, width=qr_size, height=qr_size)
        p.setFillColor(colors.HexColor('#888899'))
        p.setFont("Helvetica", 6)
        p.drawCentredString(qr_x + qr_size/2, qr_y - 8, "Scan to Verify")
    except Exception:
        pass

    p.setFillColor(colors.HexColor('#ffcc00'))
    p.rect(0, 0, W, 36, fill=True, stroke=False)
    p.setFillColor(colors.HexColor('#0f0f1a'))
    p.setFont("Helvetica-Bold", 8)
    p.drawString(18, 22, "univio.edu.in")
    p.drawString(18, 10, "info@univio.edu.in  |  +91 98765 43210")

    p.showPage()
    p.save()
    return response'''

with open('/home/anmol/collage_website/home/views.py', 'r') as f:
    content = f.read()

pattern = r'# =========================\n# STUDENT ID CARD PDF\n# =========================\n@login_required\ndef student_id_card\(request\):.*?p\.save\(\)\n    return response'
new_content = re.sub(pattern, new_func, content, flags=re.DOTALL)

with open('/home/anmol/collage_website/home/views.py', 'w') as f:
    f.write(new_content)

print("Done!")
