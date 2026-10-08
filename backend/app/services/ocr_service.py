"""OCR: Tesseract (default, ringan & mendukung bahasa Indonesia). PaddleOCR opsional untuk layout kompleks."""
import io
from PIL import Image, ImageOps

from app.core.config import settings


def _preprocess(img: Image.Image) -> Image.Image:
    img = ImageOps.exif_transpose(img).convert("L")
    img = ImageOps.autocontrast(img)
    if max(img.size) < 1500:  # upscale gambar kecil agar OCR lebih akurat
        img = img.resize((img.width * 2, img.height * 2))
    return img


def ocr_image(img: Image.Image) -> str:
    import pytesseract
    return pytesseract.image_to_string(_preprocess(img), lang=settings.ocr_lang, config="--psm 6").strip()


def ocr_bytes(data: bytes) -> str:
    return ocr_image(Image.open(io.BytesIO(data)))
