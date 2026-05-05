import numpy as np
from PIL import Image
import os
import struct


def rgb_to_ycrcb(image):
    img_array = np.array(image, dtype=np.float32)

    if len(img_array.shape) == 2:
        img_array = np.stack([img_array] * 3, axis=2)

    transform_matrix = np.array([
        [0.299, 0.587, 0.114],
        [-0.168736, -0.331264, 0.5],
        [0.5, -0.418688, -0.081312]
    ])

    height, width = img_array.shape[:2]
    pixels = img_array.reshape(-1, 3)
    ycrcb = np.dot(pixels, transform_matrix.T)
    ycrcb[:, 1:3] += 128
    ycrcb = ycrcb.reshape(height, width, 3)

    return np.clip(ycrcb, 0, 255).astype(np.uint8)


def ycrcb_to_rgb(ycrcb_array):
    ycrcb = ycrcb_array.astype(np.float32)
    ycrcb[:, :, 1:3] -= 128

    inverse_matrix = np.array([
        [1.0, 0.0, 1.402],
        [1.0, -0.344136, -0.714136],
        [1.0, 1.772, 0.0]
    ])

    height, width = ycrcb.shape[:2]
    pixels = ycrcb.reshape(-1, 3)
    rgb = np.dot(pixels, inverse_matrix.T)
    rgb = rgb.reshape(height, width, 3)

    return np.clip(rgb, 0, 255).astype(np.uint8)


def save_444(image, filename):
    ycrcb = rgb_to_ycrcb(image)
    height, width = ycrcb.shape[:2]

    with open(filename, 'wb') as f:
        f.write(b'YCC444')
        f.write(struct.pack('II', width, height))
        f.write(ycrcb[:, :, 0].tobytes())
        f.write(ycrcb[:, :, 1].tobytes())
        f.write(ycrcb[:, :, 2].tobytes())


def load_444(filename):
    with open(filename, 'rb') as f:
        magic = f.read(6)
        if magic != b'YCC444':
            raise ValueError("Invalid format")

        width, height = struct.unpack('II', f.read(8))

        y = np.frombuffer(f.read(height * width), dtype=np.uint8).reshape(height, width)
        cr = np.frombuffer(f.read(height * width), dtype=np.uint8).reshape(height, width)
        cb = np.frombuffer(f.read(height * width), dtype=np.uint8).reshape(height, width)

        ycrcb = np.stack([y, cr, cb], axis=2)
        return Image.fromarray(ycrcb_to_rgb(ycrcb))


def save_422(image, filename):
    ycrcb = rgb_to_ycrcb(image)
    height, width = ycrcb.shape[:2]

    y = ycrcb[:, :, 0]
    cr = ycrcb[:, ::2, 1]
    cb = ycrcb[:, ::2, 2]

    with open(filename, 'wb') as f:
        f.write(b'YCC422')
        f.write(struct.pack('II', width, height))
        f.write(y.tobytes())
        f.write(cr.tobytes())
        f.write(cb.tobytes())


def load_422(filename):
    with open(filename, 'rb') as f:
        magic = f.read(6)
        if magic != b'YCC422':
            raise ValueError("Invalid format")

        width, height = struct.unpack('II', f.read(8))

        y = np.frombuffer(f.read(height * width), dtype=np.uint8).reshape(height, width)
        cr_width = (width + 1) // 2
        cr = np.frombuffer(f.read(height * cr_width), dtype=np.uint8).reshape(height, cr_width)
        cb = np.frombuffer(f.read(height * cr_width), dtype=np.uint8).reshape(height, cr_width)

        cr = np.repeat(cr, 2, axis=1)[:, :width]
        cb = np.repeat(cb, 2, axis=1)[:, :width]

        ycrcb = np.stack([y, cr, cb], axis=2)
        return Image.fromarray(ycrcb_to_rgb(ycrcb))


def rle_encode(data):
    encoded = []
    i = 0
    while i < len(data):
        count = 1
        while i + count < len(data) and data[i] == data[i + count] and count < 255:
            count += 1
        encoded.append(count)
        encoded.append(data[i])
        i += count
    return bytes(encoded)


def rle_decode(data):
    decoded = []
    i = 0
    while i < len(data):
        count = data[i]
        value = data[i + 1]
        decoded.extend([value] * count)
        i += 2
    return bytes(decoded)


def save_420_rle(image, filename):
    ycrcb = rgb_to_ycrcb(image)
    height, width = ycrcb.shape[:2]

    y = ycrcb[:, :, 0]
    cr = ycrcb[::2, ::2, 1]
    cb = ycrcb[::2, ::2, 2]

    y_rle = rle_encode(y.flatten())

    with open(filename, 'wb') as f:
        f.write(b'YCC420')
        f.write(struct.pack('II', width, height))
        f.write(struct.pack('I', len(y_rle)))
        f.write(y_rle)
        f.write(cr.tobytes())
        f.write(cb.tobytes())


def load_420_rle(filename):
    with open(filename, 'rb') as f:
        magic = f.read(6)
        if magic != b'YCC420':
            raise ValueError("Invalid format")

        width, height = struct.unpack('II', f.read(8))

        y_len = struct.unpack('I', f.read(4))[0]
        y_rle = f.read(y_len)
        y = np.frombuffer(rle_decode(y_rle), dtype=np.uint8).reshape(height, width)

        cr_height = (height + 1) // 2
        cr_width = (width + 1) // 2
        cr = np.frombuffer(f.read(cr_height * cr_width), dtype=np.uint8).reshape(cr_height, cr_width)
        cb = np.frombuffer(f.read(cr_height * cr_width), dtype=np.uint8).reshape(cr_height, cr_width)

        cr = np.repeat(np.repeat(cr, 2, axis=0), 2, axis=1)[:height, :width]
        cb = np.repeat(np.repeat(cb, 2, axis=0), 2, axis=1)[:height, :width]

        ycrcb = np.stack([y, cr, cb], axis=2)
        return Image.fromarray(ycrcb_to_rgb(ycrcb))


if __name__ == "__main__":
    if not os.path.exists("task3_pics"):
        os.mkdir("task3_pics")

    img = Image.open("pic.png").convert('RGB')
    base_name = "pic"

    print(f"Image size: {img.size}")

    save_444(img, f"task3_pics/{base_name}.ycc444")
    save_422(img, f"task3_pics/{base_name}.ycc422")
    save_420_rle(img, f"task3_pics/{base_name}.ycc420")

    load_444(f"task3_pics/{base_name}.ycc444").save(f"task3_pics/{base_name}_from_444.png")
    load_422(f"task3_pics/{base_name}.ycc422").save(f"task3_pics/{base_name}_from_422.png")
    load_420_rle(f"task3_pics/{base_name}.ycc420").save(f"task3_pics/{base_name}_from_420.png")

    size_444 = os.path.getsize(f"task3_pics/{base_name}.ycc444")
    size_422 = os.path.getsize(f"task3_pics/{base_name}.ycc422")
    size_420 = os.path.getsize(f"task3_pics/{base_name}.ycc420")
