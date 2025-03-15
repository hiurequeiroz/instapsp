from PIL import Image, ExifTags, ImageEnhance, ImageFilter
import io
import os

def apply_filter(image, filter_name):
    """Aplica filtros na imagem"""
    if filter_name == "normal":
        return image
    
    elif filter_name == "grayscale":
        return image.convert('L').convert('RGB')
    
    elif filter_name == "sepia":
        # Matriz de transformação para tom sépia
        sepia_matrix = [
            0.393, 0.769, 0.189,
            0.349, 0.686, 0.168,
            0.272, 0.534, 0.131
        ]
        return image.convert('RGB', matrix=sepia_matrix)
    
    elif filter_name == "warm":
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(1.2)
        r, g, b = image.split()
        r = r.point(lambda i: i * 1.1)
        return Image.merge('RGB', (r, g, b))
    
    elif filter_name == "cool":
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(1.2)
        r, g, b = image.split()
        b = b.point(lambda i: i * 1.1)
        return Image.merge('RGB', (r, g, b))
    
    elif filter_name == "bright":
        enhancer = ImageEnhance.Brightness(image)
        return enhancer.enhance(1.2)
    
    elif filter_name == "contrast":
        enhancer = ImageEnhance.Contrast(image)
        return enhancer.enhance(1.3)
    
    elif filter_name == "blur":
        return image.filter(ImageFilter.GaussianBlur(2))
    
    elif filter_name == "sharpen":
        return image.filter(ImageFilter.SHARPEN)
    
    return image

def process_image(file, max_size=(800, 800), quality=85, filter_name="normal"):
    """
    Processa a imagem:
    - Mantém a orientação original
    - Aplica filtro selecionado
    - Redimensiona mantendo proporção
    - Comprime para reduzir tamanho
    - Converte para RGB se necessário
    """
    # Abre a imagem
    image = Image.open(file)
    
    # Corrige a orientação baseada nos dados EXIF
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        
        exif = image._getexif()
        if exif is not None:
            if orientation in exif:
                if exif[orientation] == 3:
                    image = image.rotate(180, expand=True)
                elif exif[orientation] == 6:
                    image = image.rotate(270, expand=True)
                elif exif[orientation] == 8:
                    image = image.rotate(90, expand=True)
    except (AttributeError, KeyError, IndexError):
        # Casos onde não há dados EXIF ou não é possível processá-los
        pass
    
    # Converte para RGB se necessário
    if image.mode in ('RGBA', 'P'):
        image = image.convert('RGB')
    
    # Redimensiona mantendo proporção
    image.thumbnail(max_size, Image.Resampling.LANCZOS)
    
    # Aplica o filtro selecionado
    image = apply_filter(image, filter_name)
    
    # Salva em buffer com compressão
    buffer = io.BytesIO()
    image.save(buffer, format='JPEG', quality=quality, optimize=True)
    buffer.seek(0)
    
    return buffer 