import cv2
import numpy as np

def cartoonize_frame(frame, num_colors=8, edge_threshold1=100, edge_threshold2=200):
    # Step 1: Convert to grayscale and apply bilateral filter for smoothing
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.bilateralFilter(gray, 9, 75, 75)  # Smooth while preserving edges

    # Step 2: Detect edges with Canny
    edges = cv2.Canny(blurred, edge_threshold1, edge_threshold2)
    edges = cv2.bitwise_not(edges)  # Invert so edges are black

    # Step 3: Color quantization using k-means clustering
    # Reshape the frame into a 2D array of pixels
    Z = frame.reshape((-1, 3))
    Z = np.float32(Z)

    # Define criteria and apply k-means
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    _, labels, palette = cv2.kmeans(Z, num_colors, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

    # Reconstruct the quantized image
    quantized = palette[labels.flatten()]
    quantized = quantized.reshape(frame.shape).astype(np.uint8)

    # Step 4: Combine edges and quantized colors
    # Convert edges to 3-channel for compatibility
    edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    cartoon = cv2.bitwise_and(quantized, edges_colored)

    return cartoon

# Main function to process webcam feed
def main():
    # Open webcam (0 is default camera)
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    print("Press 'q' to quit.")

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        # Apply cartoon effect
        cartoon_frame = cartoonize_frame(frame, num_colors=8, edge_threshold1=100, edge_threshold2=200)

        # Display the result
        cv2.imshow('Cartoon Effect', cartoon_frame)

        # Break loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()