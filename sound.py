from pygame import mixer
import os

bgms = {}

def init_sound():
    global bgms
    mixer.init()

    for bgm in os.listdir("data/bgm"):
        newmsc = mixer.Sound("data/bgm/" + bgm)
        bgms[bgm[:-4]] = newmsc

def play_sfx(track, loops=0, channel=1, volume=1, fade_ms=0):
    chn = mixer.Channel(channel)
    track_full = "data/sfx/" + str(track) + ".ogg"
    snd = mixer.Sound(track_full)
    chn.set_volume(volume)
    chn.play(snd, loops, 0, fade_ms)

def get_channel_busy(channel):
    chn = mixer.Channel(channel)
    return chn.get_busy()

def fade_out_channel(channel_num, ms=500):
    channel = mixer.Channel(channel_num)
    channel.fadeout(ms)

def fade_out_bgm(fade_time = 2000):
    chn = mixer.Channel(7)
    chn.fadeout(fade_time)

def is_music_playing():
    return get_channel_busy(7)

def set_channel_volume(channel, volume):
    channel = mixer.Channel(channel)
    channel.set_volume(volume)

def stop_channel(channel):
    channel = mixer.Channel(channel)
    channel.stop()

def play_bgm(track, channel=7):
    global bgms
    chn = mixer.Channel(7)
    msc = bgms[track]
    chn.set_volume(1)
    chn.play(msc)

def sound_quit():
    mixer.quit()
