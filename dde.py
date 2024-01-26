from PIL import Image


def resize_and_save_icon(source_path, output_path, size=(32, 32)):
    # Загрузка оригинального изображения
    image = Image.open(source_path)

    # Изменение размера изображения
    resized_image = image.resize(size, Image.LANCZOS)

    # Сохранение изображения в формате .ico
    resized_image.save(output_path, format='ICO')


# Используйте эту функцию для изменения размера и сохранения вашего изображения
resize_and_save_icon('App_image/Logo.ico', 'App_image/Logo_32x32.ico')
