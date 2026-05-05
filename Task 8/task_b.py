#!/usr/bin/env python3
import numpy as np
from PIL import Image
import os


def adjust_brightness(image, factor=1.2):
    img_array = np.array(image, dtype=np.float32)
    result = np.clip(img_array * factor, 0, 255).astype(np.uint8)
    return Image.fromarray(result)


def adjust_contrast(image, factor=1.5):
    img_array = np.array(image, dtype=np.float32)
    result = np.clip((img_array - 128) * factor + 128, 0, 255).astype(np.uint8)
    return Image.fromarray(result)


def rgb_to_hsv(img_array):
    img = img_array / 255.0
    r, g, b = img[:,:,0], img[:,:,1], img[:,:,2]

    max_c = np.maximum(np.maximum(r, g), b)
    min_c = np.minimum(np.minimum(r, g), b)
    diff = max_c - min_c

    h = np.zeros_like(max_c)
    s = np.zeros_like(max_c)
    v = max_c

    mask = diff != 0
    s[mask] = diff[mask] / max_c[mask]

    r_mask = (max_c == r) & mask
    g_mask = (max_c == g) & mask
    b_mask = (max_c == b) & mask

    h[r_mask] = (60 * ((g[r_mask] - b[r_mask]) / diff[r_mask]) + 360) % 360
    h[g_mask] = (60 * ((b[g_mask] - r[g_mask]) / diff[g_mask]) + 120) % 360
    h[b_mask] = (60 * ((r[b_mask] - g[b_mask]) / diff[b_mask]) + 240) % 360

    return np.stack([h, s, v], axis=2)


def hsv_to_rgb(hsv_array):
    h, s, v = hsv_array[:,:,0], hsv_array[:,:,1], hsv_array[:,:,2]

    c = v * s
    x = c * (1 - np.abs((h / 60) % 2 - 1))
    m = v - c

    rgb = np.zeros_like(hsv_array)

    masks = [
        (h >= 0) & (h < 60),
        (h >= 60) & (h < 120),
        (h >= 120) & (h < 180),
        (h >= 180) & (h < 240),
        (h >= 240) & (h < 300),
        (h >= 300) & (h <= 360)
    ]

    values = [
        [c, x, 0], [x, c, 0], [0, c, x],
        [0, x, c], [x, 0, c], [c, 0, x]
    ]

    for mask, val in zip(masks, values):
        rgb[mask, 0] = val[0][mask] if isinstance(val[0], np.ndarray) else val[0]
        rgb[mask, 1] = val[1][mask] if isinstance(val[1], np.ndarray) else val[1]
        rgb[mask, 2] = val[2][mask] if isinstance(val[2], np.ndarray) else val[2]

    rgb = (rgb + m[:,:,np.newaxis]) * 255
    return np.clip(rgb, 0, 255).astype(np.uint8)


def adjust_hue(image, hue_shift=30):
    img_array = np.array(image, dtype=np.float32)
    hsv = rgb_to_hsv(img_array)
    hsv[:,:,0] = (hsv[:,:,0] + hue_shift) % 360
    return Image.fromarray(hsv_to_rgb(hsv))


def adjust_saturation(image, factor=1.5):
    img_array = np.array(image, dtype=np.float32)
    hsv = rgb_to_hsv(img_array)
    hsv[:,:,1] = np.clip(hsv[:,:,1] * factor, 0, 1)
    return Image.fromarray(hsv_to_rgb(hsv))


def adjust_value(image, factor=1.2):
    img_array = np.array(image, dtype=np.float32)
    hsv = rgb_to_hsv(img_array)
    hsv[:,:,2] = np.clip(hsv[:,:,2] * factor, 0, 1)
    return Image.fromarray(hsv_to_rgb(hsv))


def apply_curves(image, gamma=1.5):
    img_array = np.array(image, dtype=np.float32) / 255.0
    result = np.power(img_array, gamma) * 255
    return Image.fromarray(np.clip(result, 0, 255).astype(np.uint8))


def apply_sepia(image):
    if image.mode == 'RGBA':
        image = image.convert('RGB')
    img_array = np.array(image, dtype=np.float32)

    sepia_filter = np.array([
        [0.393, 0.769, 0.189],
        [0.349, 0.686, 0.168],
        [0.272, 0.534, 0.131]
    ])

    result = img_array @ sepia_filter.T
    return Image.fromarray(np.clip(result, 0, 255).astype(np.uint8))


def apply_negative(image):
    img_array = np.array(image)
    if img_array.shape[-1] == 4:  # RGBA
        img_array[:,:,:3] = 255 - img_array[:,:,:3]
    else:
        img_array = 255 - img_array
    return Image.fromarray(img_array)


def apply_cool_filter(image):
    img_array = np.array(image, dtype=np.float32)
    img_array[:,:,0] *= 0.8
    img_array[:,:,2] *= 1.2
    return Image.fromarray(np.clip(img_array, 0, 255).astype(np.uint8))


def apply_warm_filter(image):
    img_array = np.array(image, dtype=np.float32)
    img_array[:,:,0] *= 1.2
    img_array[:,:,2] *= 0.8
    return Image.fromarray(np.clip(img_array, 0, 255).astype(np.uint8))


if __name__ == "__main__":
    os.mkdir("task2_pics")

    img = Image.open("pic.png")
    base_name = "pic"

    adjust_brightness(img, 1.3).save(f"task2_pics/{base_name}_brightness.png")
    adjust_contrast(img, 1.5).save(f"task2_pics/{base_name}_contrast.png")

    adjust_hue(img, 30).save(f"task2_pics/{base_name}_hue_shift.png")
    adjust_saturation(img, 1.5).save(f"task2_pics/{base_name}_saturation.png")
    adjust_value(img, 1.2).save(f"task2_pics/{base_name}_value.png")

    apply_curves(img, 0.7).save(f"task2_pics/{base_name}_curves_dark.png")
    apply_curves(img, 1.5).save(f"task2_pics/{base_name}_curves_light.png")
    apply_sepia(img).save(f"task2_pics/{base_name}_sepia.png")
    apply_negative(img).save(f"task2_pics/{base_name}_negative.png")
    apply_cool_filter(img).save(f"task2_pics/{base_name}_cool.png")
    apply_warm_filter(img).save(f"task2_pics/{base_name}_warm.png")