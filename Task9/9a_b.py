import cv2
import numpy as np

def interactive_warp_cv2(img):
    h, w = img.shape[:2]

    # границы исходного изображения
    src_quad = np.float32([
        [0, 0],
        [w, 0],
        [w, h],
        [0, h]
    ])

    # копия исходных точек
    dst_points = src_quad.copy()

    selected = -1

    def mouse_callback(event, x, y, flags, param):
        nonlocal selected, dst_points
        if event == cv2.EVENT_LBUTTONDOWN:
            # Проверяем, попал ли клик в одну из точек
            for i, p in enumerate(dst_points):
                if np.linalg.norm(p - [x, y]) < 20:
                    selected = i
        elif event == cv2.EVENT_MOUSEMOVE and selected != -1:
            # Обновляем координаты выбранной точки
            dst_points[selected] = [x, y]
        elif event == cv2.EVENT_LBUTTONUP:
            selected = -1

    cv2.namedWindow("CV2 Optimized Warp")
    cv2.setMouseCallback("CV2 Optimized Warp", mouse_callback)

    print("Перетаскивайте красные углы. ESC — выход.")

    while True:
        H = cv2.getPerspectiveTransform(src_quad, dst_points)

        warped = cv2.warpPerspective(img, H, (w, h), flags=cv2.INTER_LINEAR)

        for p in dst_points:
            cv2.circle(warped, tuple(p.astype(int)), 8, (0, 0, 255), -1)

        cv2.imshow("CV2 Optimized Warp", warped)

        if cv2.waitKey(1) == 27:
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    import os

    script_dir = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(script_dir, "pic.png")

    img = cv2.imread(img_path)
    if img is None:
        img = np.zeros((600, 600, 3), dtype=np.uint8)
        cv2.putText(img, "Image not found", (150, 300), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    else:
        img = cv2.resize(img, (600, 600))

    interactive_warp_cv2(img)