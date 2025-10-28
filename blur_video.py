import cv2
import sys

print("Creating blurred version of video for ethical display...")

# Open original video
input_video = cv2.VideoCapture('test_30sec.mp4')

if not input_video.isOpened():
    print("ERROR: Cannot open input video")
    sys.exit(1)

# Get video properties
fps = int(input_video.get(cv2.CAP_PROP_FPS))
width = int(input_video.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(input_video.get(cv2.CAP_PROP_FRAME_HEIGHT))
frame_count = int(input_video.get(cv2.CAP_PROP_FRAME_COUNT))

print(f"Input: {width}x{height}, {fps} FPS, {frame_count} frames")

# Create output video
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
output_video = cv2.VideoWriter('test_30sec_blurred.mp4', fourcc, fps, (width, height))

frame_num = 0
while True:
    ret, frame = input_video.read()
    if not ret:
        break

    # Apply strong blur for privacy
    blurred_frame = cv2.GaussianBlur(frame, (99, 99), 30)
    output_video.write(blurred_frame)

    frame_num += 1
    if frame_num % 100 == 0:
        print(f"  Processed {frame_num}/{frame_count} frames...")

# Cleanup
input_video.release()
output_video.release()

print(f"\nBlurred video created: test_30sec_blurred.mp4")
print(f"Total frames processed: {frame_num}")
print("Video content blurred for ethical display!")
