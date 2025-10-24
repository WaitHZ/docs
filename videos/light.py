import os
import cv2
import numpy as np

def enhance_text_in_video_grayscale(input_path, output_path):
    """
    转为灰度、去噪、锐化，最终使文字显示最佳并抑制背景噪点和杂色。
    彩色图标效果不佳时推荐此法。
    """
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print(f"Failed to open video: {input_path}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # 灰度输出（单通道）
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height), False)

    if not out.isOpened():
        print(f"Failed to initialize VideoWriter for: {output_path}")
        cap.release()
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 转为灰度
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # 去除噪点（中值滤波）
        gray_denoised = cv2.medianBlur(gray, 3)
        # 提高文字锐度
        sharp_kernel = np.array([[0, -1, 0],
                                 [-1, 5, -1],
                                 [0, -1, 0]])
        sharp = cv2.filter2D(gray_denoised, -1, sharp_kernel)
        # 提高整体对比度
        sharp = cv2.equalizeHist(sharp)
        # 略微降低亮度，增强文字与背景区分
        sharp = cv2.convertScaleAbs(sharp, alpha=0.98, beta=-10)

        out.write(sharp)

    cap.release()
    out.release()

def process_videos_to_clear_text():
    video_exts = ['.mp4', '.avi', '.mov', '.mkv']
    for fname in os.listdir('.'):
        ext = os.path.splitext(fname)[1].lower()
        if ext in video_exts:
            output_fname = f"grayscale_clear_{fname}"
            enhance_text_in_video_grayscale(fname, output_fname)
            print(f"Processed: {fname} → {output_fname}")

if __name__ == "__main__":
    process_videos_to_clear_text()




