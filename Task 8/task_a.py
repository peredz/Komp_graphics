import numpy as np
from PIL import Image
import os


def ordered_dithering(image):
    bayer_matrix = np.array([
        [0, 8, 2, 10],
        [12, 4, 14, 6],
        [3, 11, 1, 9],
        [15, 7, 13, 5]
    ], dtype=np.float32) / 16.0 * 255

    img_array = np.array(image, dtype=np.float32)
    height, width = img_array.shape
    result = np.zeros_like(img_array, dtype=np.uint8)

    for y in range(height):
        for x in range(width):
            threshold = bayer_matrix[y % 4, x % 4]
            result[y, x] = 255 if img_array[y, x] > threshold else 0

    return Image.fromarray(result)


def floyd_steinberg_dithering(image):
    img_array = np.array(image, dtype=np.float32)
    height, width = img_array.shape

    for y in range(height):
        for x in range(width):
            old_pixel = img_array[y, x]
            new_pixel = 255 if old_pixel > 128 else 0
            img_array[y, x] = new_pixel
            error = old_pixel - new_pixel

            if x + 1 < width:
                img_array[y, x + 1] += error * 7 / 16
            if y + 1 < height:
                if x > 0:
                    img_array[y + 1, x - 1] += error * 3 / 16
                img_array[y + 1, x] += error * 5 / 16
                if x + 1 < width:
                    img_array[y + 1, x + 1] += error * 1 / 16

    return Image.fromarray(np.clip(img_array, 0, 255).astype(np.uint8))


def jarvis_judice_ninke_dithering(image):
    img_array = np.array(image, dtype=np.float32)
    height, width = img_array.shape

    for y in range(height):
        for x in range(width):
            old_pixel = img_array[y, x]
            new_pixel = 255 if old_pixel > 128 else 0
            img_array[y, x] = new_pixel
            error = old_pixel - new_pixel

            if x + 1 < width:
                img_array[y, x + 1] += error * 7 / 48
            if x + 2 < width:
                img_array[y, x + 2] += error * 5 / 48

            if y + 1 < height:
                if x - 2 >= 0:
                    img_array[y + 1, x - 2] += error * 3 / 48
                if x - 1 >= 0:
                    img_array[y + 1, x - 1] += error * 5 / 48
                img_array[y + 1, x] += error * 7 / 48
                if x + 1 < width:
                    img_array[y + 1, x + 1] += error * 5 / 48
                if x + 2 < width:
                    img_array[y + 1, x + 2] += error * 3 / 48

            if y + 2 < height:
                if x - 2 >= 0:
                    img_array[y + 2, x - 2] += error * 1 / 48
                if x - 1 >= 0:
                    img_array[y + 2, x - 1] += error * 3 / 48
                img_array[y + 2, x] += error * 5 / 48
                if x + 1 < width:
                    img_array[y + 2, x + 1] += error * 3 / 48
                if x + 2 < width:
                    img_array[y + 2, x + 2] += error * 1 / 48

    return Image.fromarray(np.clip(img_array, 0, 255).astype(np.uint8))


if __name__ == "__main__":
    os.mkdir("task1_pics")

    img = Image.open("pic.png").convert('L')
    base_name = "pic"

    ordered_dithering(img).save(f"task1_pics/{base_name}_ordered.png")
    floyd_steinberg_dithering(img).save(f"task1_pics/{base_name}_floyd.png")
    jarvis_judice_ninke_dithering(img).save(f"task1_pics/{base_name}_jarvis.png")
