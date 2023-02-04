import math

from vector3 import *
from shell import *

class panzer:
    def __init__(self, hp, terrain_traverse, rotate_rate, turret_traverse, turret_limit,
                 gun_elevation, gun_depression, muzzle_vel, load_time, pos, rot, size, terrain,
                 color):

        self.hp = hp # health / hull points
        self.terrain_traverse = terrain_traverse # speed, basically (m/s)
        self.rotate_rate = rotate_rate # hull rotation rate (deg/s)
        self.turret_traverse = turret_traverse # turret rotation rate (deg/s)
        self.turret_limit = turret_limit # gun horizontal rotation limit for tank destroyers and the like (deg)
        self.gun_elevation = gun_elevation # how high into the sky the gun cam aim (deg)
        self.gun_depression = gun_depression # how low into the ground the gun can aim (deg)
        self.muzzle_vel = muzzle_vel # self explanatory (m/s)
        self.load_time = load_time # time it takes to ram the next shell into the cannon (s)
        self.pos = pos # tank position in the world (m)
        self.rot = rot # the tank rotation in polar angles (poles being +z and -z) (deg)
        self.size = size # 3D size in meters
        self.turret_rot = 0 # turret rotation rel to hull
        self.gun_rot = 0 # current gun elevation
        
        self.terrain = terrain # the terrain object over which the tank moves
        self.hull_angle = self.terrain.get_gradient_angle(self.pos, self.rot) # the gun angle with the zero horizon due to the tank sitting on the side of a hill (deg)

        self.color = color # the color with which the panzer will be drawn

        self.p1, self.p2, self.p3, self.p4 = self.calculate_collision_domain()

        self.load_progress = 0 # progress of loading a new shell, 1 = gun loaded

    def move(self, units, dt):

        # cap movement at max terrain traverse rate
        units = min(units, self.terrain_traverse)
        units = max(units, -self.terrain_traverse)

        rot_radians = math.radians(self.rot)

        self.pos.x += units * math.sin(rot_radians) * dt
        self.pos.z += units * math.cos(rot_radians) * dt

        self.pos.y = self.terrain.get_height(self.pos.x, self.pos.z)
        self.hull_angle = self.terrain.get_gradient_angle(self.pos, self.rot)

        self.p1, self.p2, self.p3, self.p4 = self.calculate_collision_domain()

    def rotate(self, units, dt):

        # cap rotation at max rotation rate
        units = min(units, self.rotate_rate)
        units = max(units, -self.rotate_rate)

        self.rot += units * dt

        self.hull_angle = self.terrain.get_gradient_angle(self.pos, self.rot)

        self.p1, self.p2, self.p3, self.p4 = self.calculate_collision_domain()

    def rotate_turret(self, units, dt):

        # cap rotation at max turret traverse
        units = min(units, self.turret_traverse)
        units = max(units, -self.turret_traverse)

        self.turret_rot += units * dt

    def rotate_gun(self, units, dt):

        self.gun_rot += units * dt
        if self.gun_rot > self.gun_elevation:
            self.gun_rot = self.gun_elevation

        elif self.gun_rot < -self.gun_depression:
            self.gun_rot = -self.gun_depression

    def calculate_collision_domain(self):
        p_center = self.pos

        local_x, local_y, local_z = self.update_local_vectors()

        p1 = p_center - local_x * self.size.x - local_z * self.size.z
        p4 = p_center - local_x * self.size.x + local_z * self.size.z
        p2 = p_center + local_x * self.size.x - local_z * self.size.z
        p3 = p_center - local_x * self.size.x - local_z * self.size.z + local_y * self.size.y

        return p1, p2, p3, p4

    def update_local_vectors(self):
        # local vectors defined according to hull orientation
        rot = math.radians(self.rot)

        # account for horizontal orientation
        local_z = vec3(math.sin(rot), 0, math.cos(rot)).normalized()
        local_x = vec3(math.cos(rot), 0, -math.sin(rot)).normalized()

        # now also account for vertical orientation
        # using Rodrigues' rotation formula
        local_z = local_z.rotated(local_x, -self.hull_angle)

        local_y = local_z.cross(local_x).normalized()

        self.local_x = local_x
        self.local_y = local_y
        self.local_z = local_z

        self.turret_x = local_x.rotated(local_y, self.turret_rot).normalized()
        self.turret_z = local_z.rotated(local_y, self.turret_rot).normalized()
        self.gun_z = self.turret_z.rotated(self.turret_x, -self.gun_rot).normalized()

        return local_x, local_y, local_z

    def shoot(self):
        if self.load_progress == 1:
            local_x = self.local_x
            local_y = self.local_y
            local_z = self.local_z

            turret_x = self.turret_x
            turret_z = self.turret_z

            gun_z = self.gun_z # this is the axis through which the shell is launched
            
            shell_pos = self.pos + local_y * self.size.y * 1.1 + gun_z * 1
            shell_vel = gun_z * self.muzzle_vel
            new_shell = shell("AP", shell_pos, shell_vel, 20, 0.2, 0.011449, None, 50)

            self.load_progress = 0

            return new_shell

    def load_shell(self, dt):
        if not self.load_progress == 1:
            self.load_progress += dt / self.load_time

        if self.load_progress > 1:
            self.load_progress = 1
