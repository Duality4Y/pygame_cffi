""" pygame module for loading and playing sounds """

from pygame._sdl import sdl, ffi
from pygame._error import SDLError
import pygame.mixer_music as music
import math


class Channel(object):
    """Channel(id): return Channel
       Create a Channel object for controlling playback"""

    def __init__(self, channel):
        # This is a null object for now, since most pygame sound
        # playback doesn't make use of the channel functionality.
        self._channel = channel

    def play(self, Sound, loops=0, maxtime=-1, fade_ms=0):
        """play Sound on this channel"""
        if fade_ms > 0:
            channel = sdl.Mix_FadeInChannelTimed(self._chhanel,
                                                 Sound._chunk, loops,
                                                 fade_ms, maxtime)
        else:
            channel = sdl.Mix_PlayChannelTimed(self._channel,
                                               Sound._chunk, loops,
                                               maxtime)
        if channel != -1:
            sdl.Mix_GroupChannel(self._channel, id(Sound._chunk))

    def get_busy(self):
        check_mixer()
        return sdl.Mix_Playing(self._channel) != 0

    def stop(self):
        check_mixer()
        sdl.Mix_HaltChannel(self._channel)

    def pause(self):
        check_mixer()
        sdl.Mix_Pause(self._channel)

    def unpause(self):
        check_mixer()
        sdl.Mix_Resume(self._channel)

    def set_volume(self, lvolume, rvolume=None):
        check_mixer()
        # This logic differs a bit from pygames because we can use a better
        # sentinal value
        if rvolume is None:
            # No Panning
            if sdl.Mix_SetPanning(self._channel, 255, 255) == 0:
                raise SDLError.from_sdl_error()
            volume = int(lvolume * 128)
        else:
            # Panning
            left = int(lvolume * 255)
            right = int(rvolume * 255)
            if sdl.Mix_SetPanning(self._channel, left, right) == 0:
                raise SDLError.from_sdl_error()
            volume = 128
        sdl.Mix_Volume(self._channel, volume)


class Sound(object):
    """Sound(filename): return Sound
       Sound(buffer): return Sound
       Sound(object): return Sound

       Create a new Sound object from a file or buffer object"""

    def __init__(self, obj):
        check_mixer()
        if isinstance(obj, basestring):
            RWops = sdl.SDL_RWFromFile(obj, "rb")
            if RWops == ffi.NULL:
                raise SDLError.from_sdl_error()
            self._chunk = sdl.Mix_LoadWAV_RW(RWops, 1)
            if self._chunk == ffi.NULL:
                raise SDLError.from_sdl_error()
        else:
            raise NotImplementedError("Implement loading from buffer & object")

    def play(self, loops=0, maxtime=-1, fade_ms=0):
        """play(loops=0, maxtime=-1, fade_ms=0): return Channel

           begin sound playback"""
        if fade_ms > 0:
            channel = sdl.Mix_FadeInChannelTimed(-1, self._chunk, loops,
                                                 fade_ms, maxtime)
        else:
            channel = sdl.Mix_PlayChannelTimed(-1, self._chunk, loops,
                                               maxtime)
        if channel < 0:
            # failure
            return None

        sdl.Mix_Volume(channel, 128)
        # pygame uses the pointer address as the tag to ensure uniqueness, we
        # use id for the same effect
        sdl.Mix_GroupChannel(channel, id(chunk))
        return Channel(channel)


def get_init():
    """get_init(): return (frequency, format, channels)

       test if the mixer is initialized"""
    if not sdl.SDL_WasInit(sdl.SDL_INIT_AUDIO):
        return None

    freq = ffi.new("int *")
    audioformat = ffi.new("uint16_t *")
    chan = ffi.new("int *")
    if not sdl.Mix_QuerySpec(freq, audioformat, chan):
        return None
    return (int(freq[0]), int(audioformat[0]), int(chan[0]))


def init(frequency=22050, size=-16, channels=2, buffer=4096):
    """init(frequency=22050, size=-16, channels=2, buffer=4096): return None

       initialize the mixer module"""
    # TODO: Duplicate the pre_init hackery pygame allows

    # Munge parameters into the correct requirements

    # chunk must be a power of 2
    chunk = int(math.log(buffer, 2))
    chunk = 2 ** chunk
    if chunk < buffer:
        chunk *= 2
    # fmt is a bunch of flags
    if size == 8:
        fmt = sdl.AUDIO_U8
    elif size == -8:
        fmt = sld.AUDIO_S8
    elif size == 16:
        fmt = sdl.AUDIO_U16SYS
    elif size == -16:
        fmt = sdl.AUDIO_S16SYS
    else:
        raise ValueError("unsupported size %d" % size)

    if channels >= 2:
        stereo = 2
    else:
        stereo = 1

    if not sdl.SDL_WasInit(sdl.SDL_INIT_AUDIO):
        if sdl.SDL_InitSubSystem(sdl.SDL_INIT_AUDIO) == -1:
            return False

        if sdl.Mix_OpenAudio(frequency, fmt, stereo, chunk) == -1:
            sdl.SDL_QuitSubSystem(sdl.SDL_INIT_AUDIO)
            return False
        sdl.Mix_VolumeMusic(127)


def find_channel(force):
    """find_channel(force=False): return Channel

        find an unused channel"""
    check_mixer()

    chan = sdl.Mix_GroupAvailable(-1)
    if chan == -1:
        if not force:
            return None
        chan = Mix_GroupOldest(-1)
    return Channel(chan)


def check_mixer():
    """Helper function to check if sound was initialised"""
    if not sdl.SDL_WasInit(sdl.SDL_INIT_AUDIO):
        raise SDLError("mixer system not initialized")