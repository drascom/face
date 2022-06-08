import cv2
import pygame

cap = cv2.VideoCapture(0)
wn = pygame.display.set_mode((640, 480))
clock = pygame.time.Clock()
success = True
while success:
    ret, imgn = cap.read()
    img = cv2.flip(imgn, +1)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            success = False
    # cv2.imshow('facedetect', img)
    if cv2.waitKey(5) != -1:
        break
    clock.tick(60)
    pygame.display.update()

pygame.quit()
