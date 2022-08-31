import pygame
import cv2
from ramka import Game, Vector


class Video:
    def __init__(self, url, output_size=(int(256 * 1.9), 256)):
        self.url = url
        self.video = cv2.VideoCapture(url)

        try:
            success, video_image = self.video.read()
        except Exception as e:
            success, video_image = False, 0

        self.ready = success
        self.output_size = output_size
        self.video_surf = pygame.Surface(output_size)
        if success:
            self.fps = self.video.get(cv2.CAP_PROP_FPS)
            self.size = video_image.shape[1::-1]
            self.frames = self.video.get(cv2.CAP_PROP_FRAME_COUNT)
            self.video_image = video_image
            self.frame_from_buffer(video_image)
        else:
            self.frames = 0
            self.size = (0, 0)
            self.fps = 1
            self.render_error()

        self.desired_spd = 0.2
        self.frame_time = 1 / self.fps
        self.next_frame_time = 0
        self.time = 0
        self.frame = 1
        self.desired_fps=15

    def get_frame(self, time=None):
        if self.ready:

            if time is None:
                time = self.time

            if time >= self.time:
                self.update(time - self.time)

        return self.video_surf

    def frame_from_buffer(self, video_image):
        try:
            video_surf = pygame.image.frombuffer(video_image.tobytes(), self.size, "BGR")
            if self.size != self.output_size:
                self.video_surf = pygame.transform.scale(video_surf, self.output_size)
            else:
                self.video_surf = video_surf
        except Exception:
            self.ready = False

    def update(self, deltaTime: float):

        nd = self.time + deltaTime

        if self.ready:
            while self.ready and nd > self.time:
                self.time += self.frame_time / self.desired_spd
                ss = self.video.grab()
                self.frame += 1
                self.ready = ss

            ss, aa = self.video.retrieve(self.video_image)
            self.ready = ss
            if self.ready:
                self.frame_from_buffer(self.video_image)
            else:
                self.render_error()

    def render_error(self):
        self.video_surf.fill((0, 0, 0))
        txt = Game.font.render("The end", True, (255, 0, 0))
        pos=0.5 * (Vector(self.video_surf.get_size()) - Vector(txt.get_size()[0], 0))
        self.video_surf.blit(txt, pos)
