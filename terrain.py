import math

from vector3 import *
from perlin_noise import PerlinNoise

class terrain:
    def __init__(self, center, size, divs):
        self.center = center
        self.size = size
        self.divs = divs

        self.data = self.generate()

    def generate(self):
        
        gridpts = []
        dx = self.size.x / self.divs.x
        dz = self.size.z / self.divs.z
        
        cx = self.center.x - self.size.x/2
        cz = self.center.z - self.size.z/2

        pnoise = PerlinNoise(octaves=10)

        for idx_z in range(self.divs.z):
            cx = self.center.x - self.size.x/2
            
            for idx_x in range(self.divs.x):
                x = cx
                y = pnoise([idx_x/self.divs.x, idx_z/self.divs.z]) * self.size.y
                z = cz
                
                gridpts.append(vec3(x, y, z))
                cx += dx

            cz += dz

        return gridpts

    def get_height(self, pt_x, pt_z):

        dx = self.data[1].x - self.data[0].x
        dz = self.data[self.divs.x + 1].z - self.data[0].z

        idx_x = (pt_x - (self.center.x - self.size.x/2))/dx
        idx_z = (pt_z - (self.center.z - self.size.z/2))/dz

        low_x = int(idx_x)
        high_x = low_x + 1
        low_z = int(idx_z)
        high_z = low_z + 1

        try:
            corner_top_right = self.data[high_z * self.divs.x + high_x]
            corner_bottom_right = self.data[low_z * self.divs.x + high_x]
            corner_top_left = self.data[high_z * self.divs.x + low_x]
            corner_bottom_left = self.data[low_z * self.divs.x + low_x]
        except:
            return 0

        low_z_diff = pt_z - corner_bottom_right.z
        low_x_diff = pt_x - corner_bottom_left.x

        z_ratio = low_z_diff / dz
        x_ratio = low_x_diff / dx

        right_height = corner_bottom_right.y + z_ratio * (corner_top_right.y - corner_bottom_right.y)
        left_height = corner_bottom_left.y + z_ratio * (corner_top_left.y - corner_bottom_left.y)

        height = left_height + x_ratio * (right_height - left_height)

        return height

    def get_gradient_angle(self, position, direction):
        y1 = self.get_height(position.x, position.z)

        delta = (self.size.x / self.divs.x) * 0.2

        pt2 = vec3()
        pt2.x = position.x + delta * math.sin(math.radians(direction))
        pt2.z = position.z + delta * math.cos(math.radians(direction))
        y2 = self.get_height(pt2.x, pt2.z)

        dist = delta * math.sqrt(2)
        gradient = (y2 - y1)/delta
        angle = math.degrees(math.atan(gradient))
        return angle
        
