import cv2

def crop_video_y(input_video_path, output_video_path, y1, y2):
    """
    裁剪视频，使其仅保留y1到y2之间的像素，其它上下范围之外的像素舍弃
    :param input_video_path: 输入视频路径
    :param output_video_path: 输出视频路径
    :param y1: 上边界（包含）
    :param y2: 下边界（不包含）
    """
    cap = cv2.VideoCapture(input_video_path)
    if not cap.isOpened():
        raise IOError(f"无法打开视频文件: {input_video_path}")
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
    out_height = y2 - y1
    if out_height <= 0:
        raise ValueError("y2 必须大于 y1，并且必须在图像范围内")

    out = cv2.VideoWriter(
        output_video_path,
        fourcc,
        fps,
        (width, out_height)
    )

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # 裁剪y方向像素
        cropped_frame = frame[y1:y2, :]
        out.write(cropped_frame)
    cap.release()
    out.release()

if __name__ == "__main__": 
    crop_video_y("/mnt/haozewu/docs/videos/3.mp4", "/mnt/haozewu/docs/videos/3-crop.mp4", 0, 880)