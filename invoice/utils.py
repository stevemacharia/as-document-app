# utils.py
import qrcode
from io import BytesIO
from django.core.files import File

def generate_qr_code(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')
    return img

def save_qr_code(instance, data):
    img = generate_qr_code(data)
    blob = BytesIO()
    img.save(blob, 'PNG')
    blob.seek(0)
    instance.qr_image.save(f'{instance.name}_qr.png', File(blob), save=False)
