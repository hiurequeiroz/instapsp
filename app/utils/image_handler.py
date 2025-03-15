from PIL import Image, ExifTags, ImageEnhance, ImageFilter
from io import BytesIO
import os

def apply_filter(image, filter_name):
    """Aplica filtros na imagem"""
    try:
        if filter_name == "normal":
            return image
        
        elif filter_name == "grayscale":
            return image.convert('L').convert('RGB')
        
        elif filter_name == "sepia":
            # Converte para RGB primeiro
            image = image.convert('RGB')
            width, height = image.size
            pixels = image.load()
            for x in range(width):
                for y in range(height):
                    r, g, b = pixels[x, y]
                    tr = int(0.393 * float(r) + 0.769 * float(g) + 0.189 * float(b))
                    tg = int(0.349 * float(r) + 0.686 * float(g) + 0.168 * float(b))
                    tb = int(0.272 * float(r) + 0.534 * float(g) + 0.131 * float(b))
                    pixels[x, y] = (min(tr, 255), min(tg, 255), min(tb, 255))
            return image
        
        elif filter_name == "warm":
            image = image.convert('RGB')
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(1.2)
            r, g, b = image.split()
            r = r.point(lambda i: min(int(float(i) * 1.1), 255))
            return Image.merge('RGB', (r, g, b))
        
        elif filter_name == "cool":
            image = image.convert('RGB')
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(1.2)
            r, g, b = image.split()
            b = b.point(lambda i: min(int(float(i) * 1.1), 255))
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
        
    except Exception as e:
        print(f"Erro ao aplicar filtro {filter_name}: {str(e)}")
        return image

def process_image(file, filter_name="normal"):
    """
    Processa a imagem:
    - Mantém a orientação original
    - Aplica filtro selecionado
    - Redimensiona mantendo proporção
    - Comprime para reduzir tamanho
    - Converte para RGB se necessário
    """
    try:
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
        
        # Redimensiona mantendo proporção se a imagem for muito grande
        max_size = (800, 800)
        if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Aplica o filtro selecionado
        image = apply_filter(image, filter_name)
        
        # Converte a imagem processada para bytes
        img_io = BytesIO()
        image.save(img_io, 'JPEG', quality=85)
        img_io.seek(0)
        return img_io
        
    except Exception as e:
        print(f"Erro ao processar imagem: {str(e)}")
        raise

def process_image_old(file, filter_name='normal'):
    """
    Processa a imagem aplicando o filtro especificado
    """
    try:
        image = Image.open(file)
        
        if filter_name == 'normal':
            pass  # Não aplica nenhum filtro
        elif filter_name == 'grayscale':
            image = image.convert('L')
        elif filter_name == 'sepia':
            # Implementação do filtro sépia
            width, height = image.size
            pixels = image.load()
            for x in range(width):
                for y in range(height):
                    r, g, b = image.getpixel((x, y))
                    tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                    tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                    tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                    image.putpixel((x, y), (min(tr, 255), min(tg, 255), min(tb, 255)))
        elif filter_name == 'warm':
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(1.5)
        elif filter_name == 'cool':
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(0.7)
        elif filter_name == 'bright':
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(1.3)
        elif filter_name == 'contrast':
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.5)
        elif filter_name == 'blur':
            image = image.filter(ImageFilter.BLUR)
        elif filter_name == 'sharpen':
            image = image.filter(ImageFilter.SHARPEN)
            
        # Converte a imagem processada para bytes
        img_io = BytesIO()
        image.save(img_io, 'JPEG', quality=85)
        img_io.seek(0)
        return img_io
        
    except Exception as e:
        print(f"Erro ao processar imagem: {str(e)}")
        raise 