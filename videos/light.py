#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频文字对比度增强工具
用于提高视频中文字的清晰度和可读性
"""

import cv2
import numpy as np
import os
import argparse
from pathlib import Path
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VideoContrastEnhancer:
    """视频对比度增强器"""
    
    def __init__(self, output_dir="enhanced_videos"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def enhance_contrast_clahe(self, frame, clip_limit=2.0, tile_grid_size=(8, 8)):
        """
        使用CLAHE (Contrast Limited Adaptive Histogram Equalization) 增强对比度
        特别适合处理文字区域
        """
        # 转换为LAB色彩空间
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # 对L通道应用CLAHE
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
        l = clahe.apply(l)
        
        # 合并通道并转换回BGR
        enhanced = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
        
        return enhanced
    
    def enhance_contrast_histogram(self, frame):
        """使用直方图均衡化增强对比度"""
        # 转换为YUV色彩空间
        yuv = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV)
        y, u, v = cv2.split(yuv)
        
        # 对Y通道应用直方图均衡化
        y = cv2.equalizeHist(y)
        
        # 合并通道并转换回BGR
        enhanced = cv2.merge([y, u, v])
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_YUV2BGR)
        
        return enhanced
    
    def sharpen_image(self, frame, strength=1.0):
        """图像锐化处理"""
        # 创建锐化核
        kernel = np.array([[-1, -1, -1],
                          [-1,  9, -1],
                          [-1, -1, -1]]) * strength
        
        # 应用锐化
        sharpened = cv2.filter2D(frame, -1, kernel)
        
        # 确保像素值在有效范围内
        sharpened = np.clip(sharpened, 0, 255).astype(np.uint8)
        
        return sharpened
    
    def enhance_text_region(self, frame):
        """专门针对文字区域的增强"""
        # 转换为灰度图
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # 使用OTSU阈值进行二值化
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # 形态学操作，去除噪声
        kernel = np.ones((2, 2), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        # 找到文字区域
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # 创建掩码
        mask = np.zeros_like(gray)
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 100:  # 过滤小区域
                cv2.fillPoly(mask, [contour], 255)
        
        # 对文字区域应用增强
        enhanced = frame.copy()
        text_region = mask > 0
        
        if np.any(text_region):
            # 对文字区域应用CLAHE
            enhanced[text_region] = self.enhance_contrast_clahe(frame)[text_region]
            
            # 对文字区域应用锐化
            sharpened = self.sharpen_image(enhanced, strength=0.5)
            enhanced[text_region] = sharpened[text_region]
        
        return enhanced
    
    def adaptive_enhancement(self, frame):
        """自适应增强，结合多种方法"""
        # 计算图像的平均亮度
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mean_brightness = np.mean(gray)
        
        # 根据亮度选择增强策略
        if mean_brightness < 100:  # 暗图像
            enhanced = self.enhance_contrast_clahe(frame, clip_limit=3.0)
        elif mean_brightness > 200:  # 亮图像
            enhanced = self.enhance_contrast_histogram(frame)
        else:  # 中等亮度
            enhanced = self.enhance_contrast_clahe(frame, clip_limit=2.0)
        
        # 应用文字区域增强
        enhanced = self.enhance_text_region(enhanced)
        
        # 轻微锐化
        enhanced = self.sharpen_image(enhanced, strength=0.3)
        
        return enhanced
    
    def process_video(self, input_path, output_path=None, method='adaptive'):
        """
        处理单个视频文件
        
        Args:
            input_path: 输入视频路径
            output_path: 输出视频路径
            method: 增强方法 ('clahe', 'histogram', 'text_region', 'adaptive')
        """
        input_path = Path(input_path)
        if not input_path.exists():
            raise FileNotFoundError(f"输入文件不存在: {input_path}")
        
        if output_path is None:
            output_path = self.output_dir / f"enhanced_{input_path.name}"
        
        # 打开视频
        cap = cv2.VideoCapture(str(input_path))
        if not cap.isOpened():
            raise ValueError(f"无法打开视频文件: {input_path}")
        
        # 获取视频属性
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        logger.info(f"处理视频: {input_path.name}")
        logger.info(f"分辨率: {width}x{height}, FPS: {fps}, 总帧数: {total_frames}")
        
        # 设置输出视频编码器
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
        
        frame_count = 0
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # 根据选择的方法进行增强
                if method == 'clahe':
                    enhanced_frame = self.enhance_contrast_clahe(frame)
                elif method == 'histogram':
                    enhanced_frame = self.enhance_contrast_histogram(frame)
                elif method == 'text_region':
                    enhanced_frame = self.enhance_text_region(frame)
                else:  # adaptive
                    enhanced_frame = self.adaptive_enhancement(frame)
                
                # 写入增强后的帧
                out.write(enhanced_frame)
                
                frame_count += 1
                if frame_count % 100 == 0:
                    progress = (frame_count / total_frames) * 100
                    logger.info(f"处理进度: {progress:.1f}% ({frame_count}/{total_frames})")
        
        except Exception as e:
            logger.error(f"处理视频时出错: {e}")
            raise
        finally:
            cap.release()
            out.release()
        
        logger.info(f"视频处理完成: {output_path}")
        return output_path
    
    def batch_process(self, input_dir, method='adaptive'):
        """批量处理目录中的所有视频文件"""
        input_dir = Path(input_dir)
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv']
        
        video_files = []
        for ext in video_extensions:
            video_files.extend(input_dir.glob(f"*{ext}"))
        
        if not video_files:
            logger.warning(f"在目录 {input_dir} 中未找到视频文件")
            return []
        
        logger.info(f"找到 {len(video_files)} 个视频文件")
        
        processed_files = []
        for video_file in video_files:
            try:
                output_path = self.process_video(video_file, method=method)
                processed_files.append(output_path)
            except Exception as e:
                logger.error(f"处理文件 {video_file} 时出错: {e}")
        
        return processed_files

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='视频文字对比度增强工具')
    parser.add_argument('input', help='输入视频文件或目录路径')
    parser.add_argument('-o', '--output', help='输出目录路径', default='enhanced_videos')
    parser.add_argument('-m', '--method', 
                       choices=['clahe', 'histogram', 'text_region', 'adaptive'],
                       default='adaptive',
                       help='增强方法 (默认: adaptive)')
    parser.add_argument('--batch', action='store_true', help='批量处理目录中的所有视频')
    
    args = parser.parse_args()
    
    # 创建增强器
    enhancer = VideoContrastEnhancer(args.output)
    
    try:
        if args.batch or os.path.isdir(args.input):
            # 批量处理
            processed_files = enhancer.batch_process(args.input, args.method)
            print(f"批量处理完成，共处理 {len(processed_files)} 个文件")
        else:
            # 处理单个文件
            output_path = enhancer.process_video(args.input, method=args.method)
            print(f"处理完成: {output_path}")
    
    except Exception as e:
        logger.error(f"处理失败: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())