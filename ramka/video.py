from typing import Callable

import pygame
import cv2
from ramka import Game, Vector, AnimatedSquence


class Video(AnimatedSquence):
    def __init__(self, url, size=None, fps=None, speed=1, looped=True,
                 callback: Callable = None):
        self.url = url
        self.video = cv2.VideoCapture(url)

        try:
            success, video_image = self.video.read()
        except Exception as e:
            success, video_image = False, 0

        self.ready = success
        self.looped = looped
        self.callback = callback

        self.output_size = size if size else (int(256 * 1.9), 256)
        self.video_surf = pygame.Surface(self.output_size)

        if success:
            self.fps = self.video.get(cv2.CAP_PROP_FPS)
            self.size = video_image.shape[1::-1]
            self.frames = self.video.get(cv2.CAP_PROP_FRAME_COUNT)
            self.video_image = video_image
            self.__frame_from_buffer(video_image)
        else:
            self.frames = 0
            self.size = (0, 0)
            self.fps = 1
            self.__render_error()

        self.desired_spd = speed
        if fps:
            fps = min(self.fps, fps)
        else:
            fps = self.fps

        self.frame_time = 1 / self.fps
        self.__prepared_time = 0
        self.time = 0
        self.frame = 1

        self.frames_for_update = self.fps / fps
        self.__grabbed_frames = 0

    def get_duration(self):
        return self.get_source_duration() * self.desired_spd

    def get_native_duration(self):
        return self.frame_time * self.frames

    def reset(self):
        self.time = 0
        self.frame = 0
        self.__grabbed_frames = 0
        self.__prepared_time = 0
        if self.ready:
            try:
                self.video.set(cv2.CAP_PROP_POS_FRAMES, 0)
            except Exception as e:
                print("reset video:", e)
                self.ready = False

    def get_frame_index(self, time: float) -> int:
        grab_time = (self.frame_time / self.desired_spd)
        if grab_time:
            return int(time / grab_time)
        else:
            return 0

    def get_image(self, time=None):
        return self.video_surf

    def __frame_from_buffer(self, video_image):
        try:
            video_surf = pygame.image.frombuffer(video_image.tobytes(), self.size, "BGR")
            if self.size != self.output_size:
                self.video_surf = pygame.transform.scale(video_surf, self.output_size)
            else:
                self.video_surf = video_surf
        except Exception:
            self.ready = False

    def update(self, deltaTime: float):

        self.__prepared_time += deltaTime

        if self.ready and self.frame < self.frames:

            grab_time = self.frame_time / self.desired_spd

            while self.ready and self.__prepared_time - self.time >= grab_time:
                self.time += grab_time
                ss = self.video.grab()
                self.__grabbed_frames += 1
                self.frame += 1
                self.ready = ss

                if self.frame >= self.frames:
                    if callable(self.callback):
                        self.callback(self)
                    if self.looped:
                        self.reset()
                    else:
                        self.__grabbed_frames = self.frames_for_update
                        break

            if self.__grabbed_frames >= self.frames_for_update:
                self.__grabbed_frames = 0
                ss, aa = self.video.retrieve(self.video_image)
                self.ready = ss
                if self.ready:
                    self.__frame_from_buffer(self.video_image)
                else:
                    self.__render_error()

    def __render_error(self):
        self.video_surf.fill((0, 0, 0))
        txt = Game.font.render("The end", True, (255, 0, 0))
        pos = 0.5 * (Vector(self.video_surf.get_size()) - Vector(txt.get_size()[0], 0))
        self.video_surf.blit(txt, pos)
