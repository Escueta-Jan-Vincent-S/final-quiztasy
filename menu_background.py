import cv2
import numpy as np
import pygame
import sys

class MenuBackground:
    def __init__(self, file_path, speed=0.5):
        self.cap = cv2.VideoCapture(file_path)
        if not self.cap.isOpened():
            print("Error: Could not open video file.")
            sys.exit()
        self.speed = speed
        self.frame_counter = 0

    def get_frame(self):
        self.frame_counter += self.speed
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.frame_counter)

        ret, frame = self.cap.read()
        if not ret:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.frame_counter = 0
            ret, frame = self.cap.read()

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = np.rot90(frame)
        return pygame.surfarray.make_surface(frame)

    def close(self):
        self.cap.release()