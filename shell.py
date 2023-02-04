import math
import time

from vector3 import *

class shell:
    def __init__(self, shell_type, pos, vel, mass, Cd, Ad, radius, dmg):
        self.shell_type = shell_type # "HE" for high-explosive and "AP" for armor piercing
        self.pos = pos
        self.vel = vel
        self.mass = mass
        self.Cd = Cd # drag coeff
        self.Ad = Ad # drag area
        self.radius = radius # damage radius (for HE shells)
        self.dmg = dmg # damage multiplier (max. damage multiplier for HE shells)
        self.flight_time = 0

    def update_traj(self, dt):
        self.vel += vec3(0, -9.80, 0) * dt # apply gravity

        # very basic estimate, using base density 1.3 kg m-3 and scale height 8.5 km
        air_density = 1.3 * math.e**(-self.pos.y/8500)
        
        drag_mag = 0.5 * self.Cd * self.Ad * air_density * self.vel.mag()**2
        drag_dir = -self.vel.normalized()
        drag_accel = drag_dir * drag_mag / self.mass

        self.vel += drag_accel * dt # apply drag

        self.pos += self.vel * dt # update position

    def check_collision(self, panzers, terrain):

        # check for tank hits
        for p in panzers:
            x = self.pos - p.pos

            if x.mag() < max(p.size.tolist()) * 2:
            
                u = p.p2 - p.p1
                v = p.p3 - p.p1
                w = p.p4 - p.p1

                if x.mag() < min(p.size.tolist()):
                    return p

                if 0 < u.dot(x) < u.dot(u) and 0 < v.dot(x) < v.dot(v) and 0 < w.dot(x) < w.dot(w):
                    return p

        # check for terrain collision
        if terrain.get_height(self.pos.x, self.pos.z) >= self.pos.y:
            return vec3(self.pos.x, terrain.get_height(self.pos.x, self.pos.z), self.pos.y)

        return None # no collision
