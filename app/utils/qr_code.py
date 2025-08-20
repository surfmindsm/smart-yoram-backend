"""
QR Code generation utilities for members
"""

import qrcode
import io
import base64
from typing import Optional
import json
from datetime import datetime


def generate_member_qr_code(member) -> Optional[str]:
    """
    Generate QR code for a member containing their information.
    Returns base64 encoded PNG image string.
    """
    try:
        # Prepare member data for QR code
        qr_data = {
            "member_id": member.id,
            "name": member.name,
            "phone": member.phone,
            "church_id": member.church_id,
            "position": member.position,
            "created_at": datetime.utcnow().isoformat(),
        }

        # Convert to JSON string
        qr_content = json.dumps(qr_data, ensure_ascii=False)

        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_content)
        qr.make(fit=True)

        # Create image
        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode()

        return f"data:image/png;base64,{img_str}"

    except Exception as e:
        print(f"Error generating QR code: {e}")
        return None


def decode_member_qr_code(qr_data: str) -> Optional[dict]:
    """
    Decode member information from QR code data.
    """
    try:
        return json.loads(qr_data)
    except Exception as e:
        print(f"Error decoding QR code: {e}")
        return None
