import cv2
import numpy as np


def bilinear_warp_inverse(img, src_quad, dst_quad, out_size):
    h, w = out_size
    result = np.zeros((h, w, 3), dtype=np.uint8)

    H = cv2.getPerspectiveTransform(src_quad, dst_quad)
    H_inv = np.linalg.inv(H)

    for y in range(h):
        for x in range(w):
            pt = np.array([x, y, 1])
            src_pt = H_inv @ pt
            src_pt /= src_pt[2]

            sx, sy = src_pt[:2]

            if 0 <= sx < img.shape[1] - 1 and 0 <= sy < img.shape[0] - 1:
                x0, y0 = int(sx), int(sy)
                dx, dy = sx - x0, sy - y0

                top = (1 - dx) * img[y0, x0] + dx * img[y0, x0 + 1]
                bottom = (1 - dx) * img[y0 + 1, x0] + dx * img[y0 + 1, x0 + 1]
                pixel = (1 - dy) * top + dy * bottom

                result[y, x] = pixel

    return result


if __name__ == "__main__":
    import os

    script_dir = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(script_dir, "pic.png")

    img = cv2.imread(img_path)

    if img is None:
        print("Ошибка загрузки изображения.")
        exit()

    img = cv2.resize(img, (600, 600))

    h, w = img.shape[:2]

    src_quad = np.float32([
        [0, 0],
        [w, 0],
        [w, h],
        [0, h]
    ])

    dst_quad = np.float32([
        [50, 100],
        [w - 50, 50],
        [w - 100, h - 50],
        [100, h - 100]
    ])

    print("9A-V: Билинейный варпинг с обратным отображением")
    warped = bilinear_warp_inverse(img, src_quad, dst_quad, (w, h))
    cv2.imshow("9A-V Bilinear Warp", warped)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
