import os
import random
from time import sleep
from typing import Dict, Callable

import pygame

"""
map of drum type to file name
"""
drum_to_file: Dict[str, str] = {
    'clap': 'clap-analog.wav',
    'cowbell': 'cowbell-808.wav',
    'crash': 'crash-acoustic.wav',
    'hihat': 'hihat-acoustic01.wav',
    'kick': 'kick-acoustic01.wav',
    'openhat': 'openhat-acoustic01.wav',
    'tambo': 'perc-tambo.wav',
    'tribal': 'perc-tribal.wav',
    'ride':  'ride-acoustic02.wav',
    'shaker': 'shaker-analog.wav',
    'snare': 'snare-noise.wav',
    'tom': 'tom-acoustic01.wav'
}


def play_sound(drum: str, volume: int) -> None:
    """
    plays audio given drum type from map given above and volume from 0 to 100
    :param drum: type of drum
    :param volume: volume from 0 to 100
    :return: nothing - plays sound
    """
    get_dir: Callable[[str], str] = os.path.dirname
    pygame.mixer.init()
    current: str = os.path.realpath(__file__)
    directory: str = os.path.join(get_dir(get_dir(get_dir(current))), 'samples')
    file_name: str = os.path.join(directory, drum_to_file[drum])
    pygame.mixer.music.load(file_name)
    pygame.mixer.music.set_volume(volume/100.0)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        sleep(0.0001)


def test() -> None:
    for drum_type in drum_to_file:
        volume: int = random.randint(0, 100)
        print(drum_type)
        play_sound(drum_type, volume)


test()
