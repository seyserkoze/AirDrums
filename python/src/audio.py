import os
from queue import Queue
from threading import Thread
from time import sleep
from typing import Dict, Callable

import pygame


class Audio:

    def play_sound(self, drum: str, volume: int) -> None:
        """
        plays audio given drum type from map given above and volume from 0 to 100 using threads
        :param drum: type of drum
        :param volume: volume from 0 to 100
        :return: nothing - plays sound
        """
        get_dir: Callable[[str], str] = os.path.dirname
        current: str = os.path.realpath(__file__)
        directory: str = os.path.join(get_dir(get_dir(get_dir(current))), 'samples')
        file_name: str = os.path.join(directory, self.__drum_to_file[drum])
        sound: pygame.mixer.Sound = pygame.mixer.Sound(file_name)
        sound.set_volume(volume / 100.0)
        channel: pygame.mixer.Channel = sound.play()
        while channel.get_busy():
            sleep(0.0001)

    def __worker(self) -> None:
        """
        worker plays sound with drum and volume from queue
        :return: None, runs forever
        """
        while True:
            (args): (str, int) = self.__task_queue.get()
            drum: str = args[0]
            volume: int = args[1]
            self.play_sound(drum, volume)
            self.__task_queue.task_done()

    def __test(self) -> None:
        """
        tests audio
        :return: None
        """
        self.__task_queue.put(('clap', 100))
        self.__task_queue.put(('cowbell', 100))
        self.__task_queue.put(('openhat', 100))
        self.__task_queue.put(('ride', 100))
        self.__task_queue.put(('crash', 100))
        self.__task_queue.put(('kick', 100))
        self.__task_queue.put(('kick', 100))
        self.__task_queue.put(('kick', 100))
        self.__task_queue.put(('crash', 100))
        self.__task_queue.put(('hihat', 100))
        self.__task_queue.put(('kick', 100))
        self.__task_queue.put(('kick', 100))
        self.__task_queue.put(('kick', 100))
        self.__task_queue.put(('tambo', 100))
        self.__task_queue.put(('tambo', 100))
        self.__task_queue.put(('tambo', 100))
        self.__task_queue.put(('tambo', 100))
        self.__task_queue.put(('tom', 100))
        self.__task_queue.put(('tom', 100))
        self.__task_queue.put(('tom', 100))
        self.__task_queue.put(('kick', 100))
        self.__task_queue.put(('kick', 100))
        self.__task_queue.put(('kick', 100))
        self.__task_queue.put(('clap', 100))
        self.__task_queue.put(('cowbell', 100))
        self.__task_queue.put(('openhat', 100))
        self.__task_queue.put(('ride', 100))
        self.__task_queue.put(('crash', 100))
        self.__task_queue.put(('hihat', 100))
        self.__task_queue.put(('hihat', 100))
        self.__task_queue.put(('clap', 100))
        self.__task_queue.put(('cowbell', 100))
        self.__task_queue.put(('openhat', 100))
        self.__task_queue.put(('tambo', 100))
        self.__task_queue.put(('tambo', 100))
        self.__task_queue.put(('tambo', 100))
        self.__task_queue.put(('tambo', 100))
        self.__task_queue.put(('tom', 100))
        self.__task_queue.put(('tom', 100))
        self.__task_queue.put(('tom', 100))
        self.__task_queue.put(('kick', 100))
        self.__task_queue.put(('kick', 100))
        self.__task_queue.put(('kick', 100))
        self.__task_queue.put(('ride', 100))
        self.__task_queue.put(('crash', 100))
        self.__task_queue.put(('hihat', 100))
        self.__task_queue.put(('hihat', 100))
        self.__task_queue.put(('clap', 100))
        self.__task_queue.put(('cowbell', 100))
        self.__task_queue.put(('openhat', 100))
        self.__task_queue.put(('ride', 100))
        self.__task_queue.put(('crash', 100))
        self.__task_queue.put(('hihat', 100))
        self.__task_queue.put(('hihat', 100))
        self.__task_queue.put(('clap', 100))
        self.__task_queue.put(('tambo', 100))
        self.__task_queue.put(('tambo', 100))
        self.__task_queue.put(('tambo', 100))
        self.__task_queue.put(('tambo', 100))
        self.__task_queue.put(('kick', 100))
        self.__task_queue.put(('kick', 100))
        self.__task_queue.put(('kick', 100))
        self.__task_queue.put(('tom', 100))
        self.__task_queue.put(('tom', 100))
        self.__task_queue.put(('tom', 100))
        self.__task_queue.put(('cowbell', 100))
        self.__task_queue.put(('openhat', 100))
        self.__task_queue.put(('ride', 100))
        self.__task_queue.put(('crash', 100))
        self.__task_queue.put(('kick', 100))
        self.__task_queue.put(('kick', 100))
        self.__task_queue.put(('kick', 100))
        self.__task_queue.put(('kick', 100))
        self.__task_queue.put(('kick', 100))
        self.__task_queue.put(('tambo', 100))
        self.__task_queue.put(('tambo', 100))
        self.__task_queue.put(('tambo', 100))
        self.__task_queue.put(('tambo', 100))
        self.__task_queue.put(('tom', 100))
        self.__task_queue.put(('tom', 100))
        self.__task_queue.put(('tom', 100))
        self.__task_queue.join()

    def __init__(self, num_channels: int = 20) -> None:
        """
        constructor that initializes data structures
        :return: None
        """
        # map of drum type to file name
        self.__drum_to_file: Dict[str, str] = {
            'clap': 'clap-analog.wav',
            'cowbell': 'cowbell-808.wav',
            'crash': 'crash-acoustic.wav',
            'hihat': 'hihat-acoustic01.wav',
            'kick': 'kick-acoustic01.wav',
            'openhat': 'openhat-acoustic01.wav',
            'tambo': 'perc-tambo.wav',
            'tribal': 'perc-tribal.wav',
            'ride': 'ride-acoustic02.wav',
            'shaker': 'shaker-analog.wav',
            'snare': 'snare-noise.wav',
            'tom': 'tom-acoustic01.wav'
        }
        # Task queue that contains sounds to be played
        self.__task_queue: Queue = Queue()
        pygame.mixer.init()
        pygame.mixer.set_num_channels(num_channels)
        for i in range(num_channels):
            t: Thread = Thread(target=self.__worker)
            t.setDaemon(True)
            t.start()
        self.__test()


test: Audio = Audio()
