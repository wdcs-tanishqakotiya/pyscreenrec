# type: ignore
import datetime
import subprocess

from pyscreeze import screenshot
from time import sleep
# type: ignore
import cv2
import os
from PIL import Image
from threading import Thread
# type: ignore
from natsort import natsorted


class InvalidCodec(Exception):
    pass


class InvalidStartMode(Exception):
    pass


class InvalidFPS(Exception):
    pass


class HighFPSWarning(Warning):
    pass


class ScreenRecorder:
    """
    Base class for screen recording.
    """

    def __init__(self) -> None:
        """
        Constructor.
        """
        self.__running = False
        self.__start_mode = "start"
        self.screenshot_folder = os.path.join(os.path.abspath(os.curdir), "pyscreenrec_data")

        # making the screenshot directory if not exists
        if not os.path.exists(self.screenshot_folder):
            os.mkdir(self.screenshot_folder)
        # clearing all the previous data if last session ended unsuccessfully
        self._clear_data()

    def _start_recording(self, video_name: str, fps: int, region: tuple = None) -> None:
        """
        (Protected) Starts screen recording.

        @params

        video_name (str) --> The name of the screen recording video.

        fps (int) --> The Frames Per Second for the screen recording. Implies how much screenshots will be taken in a second.
        """
        # checking for video extension and fps
        if not video_name.endswith(".mp4"):
            raise InvalidCodec("The video's extension can only be '.mp4'.")
        if fps > 60:
            raise InvalidFPS("The FPS for the screen recording can be maximum 60 FPS.")
        if fps > 30:
            raise HighFPSWarning(
                f"The FPS you have used for screen recording, {fps}, is pretty high and may result in delayed execution of other programs in most systems. It is advised to keep it under 20.")

        self.fps = fps
        self.video_name = video_name

        # checking if screen is already being recorded
        if self.__running:
            print("Screen recording is already running.")

        else:
            if self.__start_mode == "start":
                self.__running = True
                i = 1

                # starting screenshotting
                while self.__running:
                    if region is not None:
                        screenshot(os.path.join(self.screenshot_folder, f"s{i}.png"), region = region)
                        sleep(1 / self.fps)
                        i += 1
                    else:
                        screenshot(os.path.join(self.screenshot_folder, f"s{i}.png"))
                        sleep(1 / self.fps)
                        i += 1


            elif self.__start_mode == "resume":
                self.__running = True
                i = len(natsorted([img for img in os.listdir(self.screenshot_folder) if img.endswith(".png")])) + 1

                while self.__running:
                    if region is not None:
                        screenshot(os.path.join(self.screenshot_folder, f"s{i}.png"), region = region)
                        sleep(1 / self.fps)
                        i += 1
                    else:
                        screenshot(os.path.join(self.screenshot_folder, f"s{i}.png"))
                        sleep(1 / self.fps)
                        i += 1

            else:
                raise InvalidStartMode("The `self.__start_mode` can only be 'start' or 'resume'.")

    def start_recording(self, video_name: str = "Recording.mp4", fps: int = 15, region: tuple = None) -> None:
        """
        Starts screen recording.

        @params

        video_name (str) --> The name of the output screen recording.

        fps (int) --> The Frames Per Second for the screen recording. Implies how much screenshots will be taken in a second.
        """
        t = Thread(target = self._start_recording, args = (video_name, fps, region))
        t.start()

    def stop_recording(self) -> None:
        """
        Stops screen recording.
        """
        if not self.__running:
            print("No screen recording session is going on.")
            return None
        self.__running = False

        # saving the video and clearing all screenshots
        self._save_video(self.video_name)
        self._clear_data()

    def pause_recording(self) -> None:
        """
        Pauses screen recording.
        """
        if not self.__running:
            print("No screen recording session is going on.")
            return None

        self.__running = False

    def resume_recording(self) -> None:
        """
        Resumes screen recording.
        """
        if self.__running:
            print("Screen recording is already running.")
            return None

        self.__start_mode = "resume"
        self.start_recording(self.video_name)

    def _save_video(self, video_name: str) -> None:
        """
        (Protected) Makes a video out of the screenshots.

        @params

        video_name (str) --> Name or path to the output video.
        """
        # fetching image info
        images = natsorted([img for img in os.listdir(self.screenshot_folder) if img.endswith(".png")])
        frame = cv2.imread(os.path.join(self.screenshot_folder, images[0]))
        height, width, _ = frame.shape
        fourcc = None
        # making a videowriter object
        if '.mp4' in video_name:
            fourcc = cv2.VideoWriter().fourcc(*'mp4v')
        elif '.webm' in video_name:
            # TODO: This code is not working properly
            fourcc = cv2.VideoWriter().fourcc(*'vp09')
        video = cv2.VideoWriter(video_name, fourcc, self.fps, (width, height))

        # writing all the images to a video
        for image in images:
            im_read = cv2.imread(os.path.join(self.screenshot_folder, image))
            video.write(im_read)

        # releasing video
        cv2.destroyAllWindows()
        video.release()

    def _clear_data(self) -> None:
        """
        (Protected) Deletes all screenshots present in the screenshot folder taken during screen recording.
        """
        # deleting all screenshots present in the screenshot directory
        for image in os.listdir(self.screenshot_folder):
            os.remove(os.path.join(self.screenshot_folder, image))

    def __repr__(self) -> str:
        return "pyscreenrec is a small and cross-platform python library that can be used to record screen. \nFor more info, visit https://github.com/Shravan-1908/pyscreenrec#readme."