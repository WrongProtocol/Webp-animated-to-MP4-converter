import cv2
import numpy as np
import os
import subprocess

def frame_blend_interpolation(video_path, output_path, interpolation_factor=2):
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Could not open video.")
        return

    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Temporary file for intermediate output
    temp_output = "temp_output.avi"
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(temp_output, fourcc, fps * interpolation_factor, (width, height))

    if not out.isOpened():
        print("Error: Could not initialize VideoWriter.")
        cap.release()
        return

    # Read the first frame
    ret, prev_frame = cap.read()
    if not ret:
        print("Error: Could not read the first frame.")
        return

    # Process each frame
    for _ in range(frame_count - 1):
        ret, next_frame = cap.read()
        if not ret:
            break

        # Write the original frame
        out.write(prev_frame)

        # Interpolate frames
        for i in range(1, interpolation_factor):
            alpha = i / interpolation_factor
            interpolated_frame = cv2.addWeighted(prev_frame, 1 - alpha, next_frame, alpha, 0)
            out.write(interpolated_frame)

        prev_frame = next_frame

    # Write the last frame
    out.write(prev_frame)

    # Release OpenCV resources
    cap.release()
    out.release()

# Replace with your actual FFmpeg path
    ffmpeg_path = r"C:\Program Files\ffmpeg\bin\ffmpeg.exe"  # Example path, adjust as needed

    try:
        subprocess.run([
            ffmpeg_path, '-i', temp_output,
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-c:a', 'aac',
            '-b:a', '128k',
            '-y',
            output_path
        ], check=True)
        print("Interpolation completed and video saved to", output_path)
    except subprocess.CalledProcessError as e:
        print("Error during FFmpeg conversion:", e)
    finally:
        # Clean up temporary file
        if os.path.exists(temp_output):
            os.remove(temp_output)

# Example usage
frame_blend_interpolation('input.mp4', 'output_video.mp4', interpolation_factor=4)