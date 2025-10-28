import cv2
import sys

print("Extracting and blurring frames for ethical display...")

video = cv2.VideoCapture('test_30sec.mp4')

if not video.isOpened():
    print("ERROR: Cannot open video")
    sys.exit(1)

# Extract frame 28 (instead of frame 1)
video.set(cv2.CAP_PROP_POS_FRAMES, 27)  # 0-indexed, so 27 = frame 28
ret, frame_28 = video.read()
if ret:
    # Apply strong blur for privacy
    blurred = cv2.GaussianBlur(frame_28, (99, 99), 30)
    cv2.imwrite('frame_first.jpg', blurred)
    print("[OK] Saved blurred frame 28 as first frame")

# Extract middle frame
frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
video.set(cv2.CAP_PROP_POS_FRAMES, frame_count // 2)
ret, middle_frame = video.read()
if ret:
    blurred = cv2.GaussianBlur(middle_frame, (99, 99), 30)
    cv2.imwrite('frame_middle.jpg', blurred)
    print("[OK] Saved blurred middle frame")

# Extract last frame
video.set(cv2.CAP_PROP_POS_FRAMES, frame_count - 1)
ret, last_frame = video.read()
if ret:
    blurred = cv2.GaussianBlur(last_frame, (99, 99), 30)
    cv2.imwrite('frame_last.jpg', blurred)
    print("[OK] Saved blurred last frame")

video.release()
print("\nFrames extracted and blurred for ethical display!")
