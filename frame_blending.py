import cv2
import numpy as np

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

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_path, fourcc, fps * interpolation_factor, (width, height))

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

    # Release everything
    cap.release()
    out.release()
    print("Interpolation completed and video saved to", output_path)

# Example usage
frame_blend_interpolation('crazyaxe.mp4', 'output_video.avi', interpolation_factor=8)
