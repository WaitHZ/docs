import cv2
import numpy as np

def remove_black_bottom_border(input_video_path, output_video_path, threshold=20, min_black_height=4):
    """
    自动检测视频底部的黑色边框并将其裁掉，输出无黑边的视频。默认仅裁掉底部纯黑横条。
    :param input_video_path: 输入视频路径
    :param output_video_path: 输出视频路径
    :param threshold: 黑色判定阈值（0-255，小于该值判为黑）
    :param min_black_height: 至少连续多少行为黑色才认为是黑边
    """
    cap = cv2.VideoCapture(input_video_path)
    if not cap.isOpened():
        raise IOError(f"无法打开视频文件: {input_video_path}")
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # 检测首帧底部黑边高度
    ret, frame = cap.read()
    if not ret:
        raise IOError("无法读取视频帧进行边框检测")
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 逐行判定，检测底部有多少连续黑色行
    black_border_height = 0
    for y in range(height-1, -1, -1):
        row = gray[y, :]
        # 判定该行是否为黑色行：绝大多数像素小于阈值
        if np.mean(row < threshold) > 0.95:
            black_border_height += 1
        else:
            if black_border_height >= min_black_height:
                break  # 连续黑色行足够，即为黑边
            else:
                black_border_height = 0  # 太短的黑色片段不计入，重新统计

    # 计算新裁剪后的区域
    cut_height = height - black_border_height if black_border_height >= min_black_height else height
    if cut_height < height:
        print(f"检测到底部黑边高 {black_border_height} px，将自动移除")
    else:
        print("未检测到底部明显黑边，不做裁剪")

    # 重新初始化cap到头
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(
        output_video_path,
        fourcc,
        fps,
        (width, cut_height)
    )
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        cropped = frame[:cut_height, :]
        out.write(cropped)
    cap.release()
    out.release()



if __name__ == "__main__": 
    remove_black_bottom_border("/mnt/haozewu/docs/videos/3.mp4", "/mnt/haozewu/docs/videos/3-crop.mp4")