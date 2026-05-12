import cv2
import numpy as np
from scipy.spatial import Delaunay
import time


def warp_triangle(img, src_tri, dst_tri, output):
    h, w = img.shape[:2]

    r1 = cv2.boundingRect(np.float32([src_tri]))
    r2 = cv2.boundingRect(np.float32([dst_tri]))

    x1, y1, w1, h1 = r1
    x2, y2, w2, h2 = r2

    if x2 < 0 or y2 < 0 or x2 + w2 > w or y2 + h2 > h:
        x2 = max(0, x2)
        y2 = max(0, y2)
        w2 = min(w - x2, w2)
        h2 = min(h - y2, h2)

    src_rect = []
    dst_rect = []

    for i in range(3):
        src_rect.append((src_tri[i][0] - x1, src_tri[i][1] - y1))
        dst_rect.append((dst_tri[i][0] - x2, dst_tri[i][1] - y2))

    src_crop = img[y1:y1+h1, x1:x1+w1]

    if src_crop.size == 0 or w2 <= 0 or h2 <= 0:
        return

    M = cv2.getAffineTransform(np.float32(src_rect), np.float32(dst_rect))
    warped = cv2.warpAffine(
        src_crop,
        M,
        (w2, h2),
        None,
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_REFLECT_101
    )

    mask = np.zeros((h2, w2, 3), dtype=np.float32)
    cv2.fillConvexPoly(mask, np.int32(dst_rect), (1.0, 1.0, 1.0))

    output[y2:y2+h2, x2:x2+w2] *= (1 - mask)
    output[y2:y2+h2, x2:x2+w2] += warped * mask


def triangle_warp_2x2_interactive(img):
    h, w = img.shape[:2]

    src_points = np.float32([
        [0, 0],
        [w, 0],
        [0, h],
        [w, h]
    ])

    dst_points = src_points.copy()

    selected = -1

    def mouse(event, x, y, flags, param):
        nonlocal selected, dst_points
        if event == cv2.EVENT_LBUTTONDOWN:
            for i, p in enumerate(dst_points):
                if np.linalg.norm(p - [x, y]) < 10:
                    selected = i
                    break
        elif event == cv2.EVENT_MOUSEMOVE and selected != -1:
            dst_points[selected] = [np.clip(x, 0, w-1),
                                    np.clip(y, 0, h-1)]
        elif event == cv2.EVENT_LBUTTONUP:
            selected = -1

    cv2.namedWindow("9B-A 2x2")
    cv2.setMouseCallback("9B-A 2x2", mouse)

    while True:
        start_time = time.time()
        output = np.zeros_like(img, dtype=np.float32)
        tri = Delaunay(src_points)

        for simplex in tri.simplices:
            src_tri = src_points[simplex]
            dst_tri = dst_points[simplex]
            warp_triangle(img, src_tri, dst_tri, output)

        display = output.astype(np.uint8)
        for p in dst_points:
            cv2.circle(display, tuple(p.astype(int)), 6, (0, 255, 0), -1)

        cv2.imshow("9B-A 2x2", display)

        elapsed = time.time() - start_time
        wait_time = max(1, int(33 - elapsed * 1000))
        
        if cv2.waitKey(wait_time) == 27:
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    import os

    script_dir = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(script_dir, "pic.png")

    img = cv2.imread(img_path)

    if img is None:
        print("Ошибка загрузки изображения.")
        exit()

    img = cv2.resize(img, (600, 600))

    print("9B-A: 2x2 треугольная сетка")
    print("Перетаскивайте зеленые точки. ESC — выход.")
    triangle_warp_2x2_interactive(img)
