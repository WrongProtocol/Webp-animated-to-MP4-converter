import cv2
import numpy as np

def warp_image(image, flow):
    """Warp an image using the provided optical flow."""
    h, w = flow.shape[:2]
    # Create a grid of pixel coordinates
    grid_x, grid_y = np.meshgrid(np.arange(w), np.arange(h))
    # Compute the remap coordinates by adding the flow
    map_x = (grid_x + flow[..., 0]).astype(np.float32)
    map_y = (grid_y + flow[..., 1]).astype(np.float32)
    # Warp the image using remap
    warped = cv2.remap(image, map_x, map_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return warped

def generate_interpolated_frame(prev_frame, next_frame, t):
    """
    Generate an intermediate frame at time fraction t between 0 and 1.
    t=0 gives the previous frame, t=1 gives the next frame.
    """
    # Convert frames to grayscale for optical flow calculation
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    next_gray = cv2.cvtColor(next_frame, cv2.COLOR_BGR2GRAY)
    
    # Calculate optical flow from prev_frame to next_frame
    flow = cv2.calcOpticalFlowFarneback(prev_gray, next_gray, None,
                                        pyr_scale=0.5, levels=3, winsize=15,
                                        iterations=3, poly_n=5, poly_sigma=1.2, flags=0)
    
    # Warp the previous frame forward by t and the next frame backward by (1-t)
    flow_t = flow * t
    flow_inv_t = flow * (t - 1)  # Negative scaling to go backward from next_frame
    
    warped_prev = warp_image(prev_frame, flow_t)
    warped_next = warp_image(next_frame, flow_inv_t)
    
    # Blend the warped images together
    interpolated_frame = cv2.addWeighted(warped_prev, 1 - t, warped_next, t, 0)
    return interpolated_frame

# Example usage: Process a video and insert one interpolated frame between each original frame
cap = cv2.VideoCapture("test.mp4")
# Get video properties and initialize output (adjust as needed)
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter("output_interpolated.mp4", fourcc, fps * 2, (frame_width, frame_height))

ret, prev_frame = cap.read()
if not ret:
    print("Error reading video")
    cap.release()
    out.release()
    exit()

while True:
    ret, next_frame = cap.read()
    if not ret:
        # Write the last frame if needed
        out.write(prev_frame)
        break
    
    # Write the original previous frame
    out.write(prev_frame)
    
    # Generate an intermediate frame at t=0.5 (the midpoint)
    t = 0.5  # You can adjust t or generate multiple frames for different t values
    inter_frame = generate_interpolated_frame(prev_frame, next_frame, t)
    out.write(inter_frame)
    
    prev_frame = next_frame

cap.release()
out.release()
