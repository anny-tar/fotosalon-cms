from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from pathlib import Path
import io
import os


def convert_to_webp_and_thumbnail(image_file, upload_to, thumb_upload_to, thumb_size=(400, 400)):
    """
    Конвертирует изображение в WebP и создаёт миниатюру.
    Возвращает (основной_путь, путь_миниатюры) относительно MEDIA_ROOT.
    """
    img = Image.open(image_file)
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')

    # Сохраняем основное фото в WebP
    filename_stem = Path(image_file.name).stem
    main_filename = f'{filename_stem}.webp'
    main_dir = Path(settings.MEDIA_ROOT) / upload_to
    main_dir.mkdir(parents=True, exist_ok=True)
    main_path = main_dir / main_filename
    img.save(main_path, 'WEBP', quality=85)

    # Миниатюра
    thumb = img.copy()
    thumb.thumbnail(thumb_size, Image.LANCZOS)
    thumb_dir = Path(settings.MEDIA_ROOT) / thumb_upload_to
    thumb_dir.mkdir(parents=True, exist_ok=True)
    thumb_path = thumb_dir / main_filename
    thumb.save(thumb_path, 'WEBP', quality=75)

    return (
        f'{upload_to}/{main_filename}',
        f'{thumb_upload_to}/{main_filename}',
    )


def apply_watermark(image_path, watermark_logo_path=None):
    """
    Накладывает водяной знак на изображение.
    Если watermark_logo_path не задан — использует текстовый водяной знак.
    Возвращает путь к файлу с водяным знаком относительно MEDIA_ROOT.
    """
    img = Image.open(Path(settings.MEDIA_ROOT) / image_path).convert('RGBA')

    if watermark_logo_path and Path(watermark_logo_path).exists():
        # Логотип как водяной знак
        wm = Image.open(watermark_logo_path).convert('RGBA')
        # Масштабируем логотип до 15% ширины фото
        wm_width = int(img.width * 0.15)
        ratio = wm_width / wm.width
        wm_height = int(wm.height * ratio)
        wm = wm.resize((wm_width, wm_height), Image.LANCZOS)
        # Полупрозрачность
        r, g, b, a = wm.split()
        a = a.point(lambda x: int(x * 0.5))
        wm.putalpha(a)
        # Позиция — правый нижний угол с отступом
        margin = 20
        pos = (img.width - wm_width - margin, img.height - wm_height - margin)
        layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
        layer.paste(wm, pos)
        img = Image.alpha_composite(img, layer)
    else:
        # Текстовый водяной знак
        draw = ImageDraw.Draw(img, 'RGBA')
        text = '© ФотоСалон'
        font_size = max(20, img.width // 30)
        try:
            font = ImageFont.truetype('arial.ttf', font_size)
        except Exception:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        margin = 20
        x = img.width - text_width - margin
        y = img.height - text_height - margin
        # Тень
        draw.text((x + 2, y + 2), text, font=font, fill=(0, 0, 0, 120))
        # Текст
        draw.text((x, y), text, font=font, fill=(255, 255, 255, 180))

    # Сохраняем в отдельную папку
    img_rgb = img.convert('RGB')
    stem = Path(image_path).stem
    wm_dir = Path(settings.MEDIA_ROOT) / 'portfolio' / 'watermarked'
    wm_dir.mkdir(parents=True, exist_ok=True)
    wm_path = wm_dir / f'{stem}.webp'
    img_rgb.save(wm_path, 'WEBP', quality=85)

    return f'portfolio/watermarked/{stem}.webp'