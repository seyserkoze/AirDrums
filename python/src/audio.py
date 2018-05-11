import os
from Queue import Queue
from threading import Thread, Event
from time import sleep

import pygame


class Audio:
    """
    Audio Player that plays .wav files using PyGame Sound library
    Plays multiple sounds at the same times by playing on multiple channels
    and multi-threaded processing
    """

    @staticmethod
    def __play_sound(drum, attack):
        """
        plays audio given drum type from map given above and volume from 0 to 100 using threads
        :param drum: type of drum
        :param attack: attack/volume from 0 to 7
        :return: nothing - plays sound
        """
        get_dir = os.path.dirname
        current = os.path.realpath(__file__)
        directory = os.path.join(get_dir(get_dir(get_dir(current))), 'samples')
        file_name = os.path.join(directory, drum, drum + str(attack) + '.wav')
        sound = pygame.mixer.Sound(file_name)
        channel = sound.play()
        while channel.get_busy():
            sleep(0.0001)


    def stop(self):
        """
        Call to stop the audio player. Terminates all the threads
        """
        self.__stop_event.set() # set stop flag

    def __worker(self):
        """
        worker plays sound with drum and volume from queue
        :param self: class
        :return: None, runs forever
        """
        while not self.__stop_event.is_set():
            (args) = self.__task_queue.get()
            drum = args[0]
            attack = args[1]
            Audio.__play_sound(drum, attack)
            print('playing ' + drum)
            self.__task_queue.task_done()

    def queue_sound(self, sound):
        """
        queues sounds to be played
        :param self: class
        :param drum: drum type
        :param attack: number from 0 to 7 representing attack/volume
        :return:
        """
        drum, attack = sound 
        self.__task_queue.put((drum, attack))

    def __init__(self, num_channels=20):
        """
        constructor that initializes data structures
        :return: None
        """
        # Task queue that contains sounds to be played
        self.__task_queue = Queue()
        self.__stop_event = Event()
        pygame.mixer.init()
        pygame.mixer.set_num_channels(num_channels)
        for i in range(num_channels):
            t = Thread(target=self.__worker)
            t.setDaemon(True)
            t.start()
