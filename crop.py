import cv2

def crop_video(
    input_path, 
    output_path, 
    start_frame, 
    end_frame, 
    top, 
    bottom
):
    """
    裁剪视频帧的范围以及每帧的上下部分，并将输出分辨率同比缩小到原来2/3。

    Args:
        input_path (str): 输入视频文件路径
        output_path (str): 输出裁剪后的视频文件路径
        start_frame (int): 保留的起始帧编号（包含该帧，0为第一帧）
        end_frame (int): 保留的结束帧编号（包含该帧）
        top (int): 每帧保留的上边界像素（从该行开始保留，0为第一行）
        bottom (int): 每帧保留的下边界像素（到该行，不包括该行）
    """

    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise IOError(f"无法打开视频文件: {input_path}")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    print(f"视频总帧数: {total_frames}，视频尺寸: {width}x{height}")

    # 检查裁剪范围是否合法
    if top < 0 or bottom > height or top >= bottom:
        raise ValueError(f"非法的裁剪高度范围: top={top}, bottom={bottom}, 视频高度={height}")
    if start_frame < 0 or end_frame >= total_frames or start_frame > end_frame:
        raise ValueError(f"非法的帧范围: start_frame={start_frame}, end_frame={end_frame}, 总帧数={total_frames}")

    # 计算裁剪后帧的原始尺寸
    cropped_height = bottom - top
    cropped_width = width

    # 计算缩小2/3以后的分辨率，保持宽高比
    scale = 2 / 3
    scaled_width = int(cropped_width * scale)
    scaled_height = int(cropped_height * scale)

    # 强制使用mp4v编码，部分平台h264不可用
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (scaled_width, scaled_height))

    # 跳转到start_frame
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    current_frame = start_frame

    while current_frame <= end_frame:
        ret, frame = cap.read()
        if not ret:
            break
        cropped_frame = frame[top:bottom, :, :]
        resized_frame = cv2.resize(cropped_frame, (scaled_width, scaled_height), interpolation=cv2.INTER_AREA)
        out.write(resized_frame)
        current_frame += 1

    cap.release()
    out.release()


crop_video("/mnt/haozewu/docs/LLM Trajectory Replay - Google Chrome 2025-10-23 22-08-30.mp4", "output.mp4", 50, 870, 250, 1370)