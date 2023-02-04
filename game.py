import OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
import os
import keyboard
import mouse
import glfw
import time
from screeninfo import get_monitors

from terrain import *
from panzer import *
from shell import *
from camera import *
from graphics import *
from vector3 import *
from matrix3x3 import *
from sound import *

mouse_rot_active = True
cam_dist = 15

def get_os_type():
    return os.name

def clear_cmd_terminal(os_name):
    if os_name == "nt":
        os.system("cls")
    else:
        os.system("clear")

vp_size_changed = False
def resize_cb(window, w, h):
    global vp_size_changed
    vp_size_changed = True

# clear all keyboard buffer
# e.g. don't keep camera movement keys
# in buffer as we try to enter a command
def flush_input():
    try:
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()
    except ImportError:
        import sys, termios    #for linux/unix
        termios.tcflush(sys.stdin, termios.TCIOFLUSH)

def init():
    ground = terrain(vec3(), vec3(5000, 200, 5000), vec3(150, 1, 150))
    cam = camera("main_cam", vec3(), matrix3x3(), True)
    p1 = panzer(100, 10, 10, 10, None, 70, 5, 600, 10, vec3(1000, ground.get_height(1000,1000), 1000), 0, vec3(2, 2, 3), ground, (1,0,0))
    p2 = panzer(100, 10, 10, 10, None, 70, 5, 600, 10, vec3(-30, ground.get_height(-30,-30), -30), 0, vec3(2, 2, 3), ground, (0,0,1))

    monitor = get_monitors()[0]
    screen_x = monitor.width
    screen_y = monitor.height

    return ground, cam, p1, p2, screen_x, screen_y

def main():
    global vp_size_changed, mouse_rot_active, cam_dist
    ground, cam, p1, p2, screen_x, screen_y = init()
    shells = []

    glfw.init()

    mw = glfw.create_window(1280,720,"Panzer Function", None, None)
    glfw.set_window_pos(mw,100,100)
    glfw.make_context_current(mw)
    glfw.set_window_size_callback(mw, resize_cb)
    
    gluPerspective(70, 1280/720, 1, 100000)
    glEnable(GL_CULL_FACE)
    glClearColor(0.0, 0.1, 0.3, 1)
    glPointSize(3)

    init_sound()
    
    cam.rotate(vec3(0, 180, 0))
    cam.rotate(vec3(-15, 0, 0))

    cam_rotate_speed = 30
    cam_strafe_speed = 5

    cam_pitch_up = "W"
    cam_pitch_down = "S"
    cam_yaw_left = "A"
    cam_yaw_right = "D"

    cam_roll_ccw = "U"
    cam_roll_cw = "O"

    turn_right = "D"
    go_forward = "W"
    turn_left = "A"
    go_backward = "S"
    shoot = "space"

    turret_left = "Q"
    turret_right = "E"

    gun_up = "R"
    gun_down = "F"

    def toggle_mouse_active():
        global mouse_rot_active
        mouse_rot_active = not mouse_rot_active

    def zoom_in():
        global cam_dist
        cam_dist -= 5

    def zoom_out():
        global cam_dist
        cam_dist += 5

    mouse.on_middle_click(toggle_mouse_active)
    mouse.on_click(zoom_in)
    mouse.on_right_click(zoom_out)
    
    cam.lock = p1
    
    dt = 0.01
    game_time = 0

    # channel organization:
    # ch 1 - p1 engine noise
    # ch 2 - p2 engine noise
    # ch 3 - p1 gun/damage
    # ch 4 - p2 gun/damage
    # ch 5 - p1 shell load
    # ch 6 - p2 shell load
    # ch 7 - bgm
    play_sfx("panzer_starting")
    p1_engine_state = "starting"
    
    while not glfw.window_should_close(mw):
        cycle_start = time.perf_counter()
        glfw.poll_events()

        if vp_size_changed:
            vp_size_changed = False
            w, h = glfw.get_framebuffer_size(mw)
            glViewport(0, 0, w, h)

        if mouse_rot_active:
            m_pos = mouse.get_position()
            cam.rotate(vec3((m_pos[1] - screen_y*0.5) / screen_y, -(m_pos[0] - screen_x * 0.5) / screen_x, 0) * cam_rotate_speed)
            mouse.move(screen_x * 0.5, screen_y * 0.5, True)
            cam.set_pos(-p1.pos - cam.orient.vz() * cam_dist)

        if keyboard.is_pressed(cam_roll_ccw):
            cam.rotate(vec3(0,0,cam_rotate_speed)*0.1)

        if keyboard.is_pressed(cam_roll_cw):
            cam.rotate(vec3(0,0,-cam_rotate_speed)*0.1)

        is_p1_moving = False

        if not p1_engine_state == "starting":
            if keyboard.is_pressed(turn_left):
                p1.rotate(15, dt)
                is_p1_moving = True

            if keyboard.is_pressed(turn_right):
                p1.rotate(-15, dt)
                is_p1_moving = True

            if keyboard.is_pressed(go_forward):
                p1.move(15, dt)
                is_p1_moving = True
                
            if keyboard.is_pressed(go_backward):
                p1.move(-15, dt)
                is_p1_moving = True

            if keyboard.is_pressed(turret_left):
                p1.rotate_turret(15, dt)

            if keyboard.is_pressed(turret_right):
                p1.rotate_turret(-15, dt)

            if keyboard.is_pressed(gun_up):
                p1.rotate_gun(15, dt)

            if keyboard.is_pressed(gun_down):
                p1.rotate_gun(-15, dt)

        # sound stuff
        if p1_engine_state == "starting" and not get_channel_busy(1):
            p1_engine_state = "idle"
            fade_out_channel(1)
            play_sfx("panzer_idling", -1, 1)

        elif p1_engine_state == "idle" and is_p1_moving:
            p1_engine_state = "moving"
            fade_out_channel(1)
            play_sfx("panzer_moving", -1, 1, 1, 50)

        elif p1_engine_state == "moving" and not is_p1_moving:
            p1_engine_state = "idle"
            fade_out_channel(1)
            play_sfx("panzer_idling", -1, 1, 1, 50)

        if p1.load_progress < 1 and not get_channel_busy(5):
            play_sfx("panzer_loading", -1, 5)

        elif p1.load_progress == 1 and get_channel_busy(5):
            stop_channel(5)

        # end sound stuff

        if keyboard.is_pressed(shoot) and p1.load_progress == 1:
            play_sfx("panzer_firing", 0, 3)
            new_shell = p1.shoot()
            shells.append(new_shell)

        for s in shells:
            s.update_traj(dt)
            s.flight_time += dt
            col_check = s.check_collision([p1, p2], ground)
            
            if col_check:
                if col_check == p1:
                    p1.hp -= s.dmg
                    shells.remove(s)
                    del s
                    play_sfx("panzer_hit", 0, 3)
                    print("P1 hit!")
                elif col_check == p2:
                    p2.hp -= s.dmg
                    shells.remove(s)
                    del s
                    play_sfx("panzer_hit", 0, 4)
                    print("P2 hit!")
                else:
                    shells.remove(s)
                    del s
                    play_sfx("ground_shell", 0, 4)

            elif ((not ground.center.x - ground.size.x < s.pos.x < ground.center.x + ground.size.x) or
                  (not ground.center.z - ground.size.z < s.pos.z < ground.center.z + ground.size.z)):
                shells.remove(s)
                del s

        p1.update_local_vectors()
        p2.update_local_vectors()
        
        p1.load_shell(dt)
        p2.load_shell(dt)

        if p1.hp <= 0:
            p1.color = (0.2, 0.2, 0.2)

        if p2.hp <= 0:
            p2.color = (0.2, 0.2, 0.2)

        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        drawScene(ground, cam, p1, p2, shells)
        glfw.swap_buffers(mw)

        game_time += dt
        dt = time.perf_counter() - cycle_start

    glfw.destroy_window(mw)
    sound_quit()

main()
