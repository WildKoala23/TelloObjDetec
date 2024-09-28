import cv2
from djitellopy import Tello
import threading
from time import sleep
import pygame
from ultralytics import YOLO


# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((720, 480))  # Set Pygame window resolution
clock = pygame.time.Clock()

# Initialize mav (Tello drone)
mav = Tello()
mav.connect()
print(f"Battery level: {mav.get_battery()}%")
mav.streamon()

# Load model
model = YOLO('C:\\Users\\pedrinho\\Desktop\\Python\\Bolsa\\TelloDrone\\yolov8n.pt', task="detect")

# Countdown for takeoff
print('Turning stream on')
print('Preparing for takeoff: ')
for i in range(1, 4):
    print(i)
    sleep(1)

# Get the 'BackgroundFrameRead' object that holds the latest captured frame from the mav
frame_read = mav.get_frame_read(with_queue=False, max_queue_len=0)

stop_streaming = False
stop_flying = False

# Display drone stream so as to not freeze when moving
def display():
    global stop_streaming
    while not stop_streaming:
        frame = frame_read.frame
        if frame is not None:
            # "Runs" the model
            results = model(frame)
            annotated_frame = results[0].plot()
            annotated_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
            #Test frame without model
            #new_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            cv2.imshow("mav STREAM", annotated_frame)

        if cv2.waitKey(1) == 27:  # ESC key to exit
            stop_streaming = True
            mav.streamoff()
            break
    cv2.destroyAllWindows()

# Start display thread
stream_thread = threading.Thread(target=display, daemon=True)
stream_thread.start()

# Houston, we have takeoff
mav.takeoff()
print('Taking off...')

# Control with keyboard
# Running on the main thread
while not stop_flying:
    try:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                stop_flying = True
                stop_streaming = True
                break
            # Controls for the drone
            elif event.type == pygame.KEYDOWN:  # Only trigger on key press (not key hold)
                if event.key == pygame.K_w:
                    print('Moving forward...')
                    mav.move_forward(30)
                elif event.key == pygame.K_s:
                    print('Moving back...')
                    mav.move_back(30)
                elif event.key == pygame.K_a:
                    print('Moving left....')
                    mav.move_left(30)
                elif event.key == pygame.K_d:
                    print('Moving right....')
                    mav.move_right(30)
                elif event.key == pygame.K_q:
                    print('Turning left 45º...')
                    mav.rotate_counter_clockwise(45)
                elif event.key == pygame.K_e:
                    print('Turning right 45º...')
                    mav.rotate_clockwise(45)
                elif event.key == pygame.K_z:
                    print('Moving up....')
                    mav.move_up(30)
                elif event.key == pygame.K_x:
                    print('Moving down....')
                    mav.move_down(30)
                elif event.key == pygame.K_ESCAPE:
                    print('Landing...')
                    stop_flying = True
                    stop_streaming = True
                    break
        # Leaves fps to 60 
        clock.tick(60)
    except Exception as err:
        print(f'Movement failed: {err}')



# Test
# mav.move_up(30)
# sleep(3)
# mav.move_back(70)
# sleep(3)
# mav.rotate_counter_clockwise(90)
# sleep(3)

# Land the drone safely
mav.land()
mav.end()
# Clean up pygame and other resources
pygame.quit()
