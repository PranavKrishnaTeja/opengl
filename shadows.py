import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import numpy as np

def load_obj(filename):
    vertices = []
    faces = []
    with open(filename) as f:
        for line in f:
            if line.startswith('v '):
                vertex = list(map(float, line.split()[1:]))
                vertices.append(vertex)
            elif line.startswith('f '):
                face = list(map(int, [i.split('/')[0] for i in line.split()[1:]]))
                faces.append(face)
    return vertices, faces
def create_shadow_matrix(plane, light_position):
    light = np.array(light_position[:3])  
    light = np.append(light, 1) 
    dot = np.dot(plane[:3], light[:3])
    matrix = np.identity(4)
    matrix -= 2 * np.outer(light, plane)
    matrix[3, 3] = dot - 2 * plane[3] * light[3]
    return matrix

def draw_obj_with_shadow(vertices, faces, texture_data, texture_id, texture_width, texture_height, light_position):
    glEnable(GL_STENCIL_TEST)
    glColor4f(1.0, 1.0, 0.0, 1.0)
    glStencilFunc(GL_ALWAYS, 1, 0xFF)
    glStencilOp(GL_KEEP, GL_KEEP, GL_REPLACE)
    glStencilMask(0xFF)
    glDepthMask(GL_FALSE)

    ground_plane = np.array([0.0, 1.0, 0.0, 0.0])
    shadow_matrix = create_shadow_matrix(ground_plane, light_position)
    shadow_scale_factor = 0.8
    glPushMatrix()
    glScalef(shadow_scale_factor, shadow_scale_factor, shadow_scale_factor)
    glMultMatrixf(shadow_matrix.T)
    draw_obj(vertices, faces, texture_data, texture_id, texture_width, texture_height)
    glPopMatrix()

    glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE)
    glStencilFunc(GL_EQUAL, 1, 0xFF)
    glStencilMask(0x00)
    glDepthMask(GL_TRUE)

    draw_obj(vertices, faces, texture_data, texture_id, texture_width, texture_height)
    glDisable(GL_STENCIL_TEST)
"""
def create_cube_map(filenames):
    cube_map = glGenTextures(1)
    glBindTexture(GL_TEXTURE_CUBE_MAP, cube_map)

    for i, filename in enumerate(filenames):
        texture_surface = pygame.image.load(filename)
        texture_data = pygame.image.tostring(texture_surface, "RGBA", True)
        texture_width, texture_height = texture_surface.get_rect().size
        glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, 0, GL_RGBA, texture_width, texture_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)

    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)

    return cube_map

def draw_skybox(cube_map, size):
    glDepthMask(GL_FALSE)
    glDisable(GL_LIGHTING)
    glEnable(GL_TEXTURE_CUBE_MAP)
    glBindTexture(GL_TEXTURE_CUBE_MAP, cube_map)

    glBegin(GL_QUADS)

    glTexCoord3f(-1, 1, -1)
    glVertex3f(-size, size, -size)
    glTexCoord3f(-1, -1, -1)
    glVertex3f(-size, -size, -size)
    glTexCoord3f(1, -1, -1)
    glVertex3f(size, -size, -size)
    glTexCoord3f(1, 1, -1)
    glVertex3f(size, size, -size)

    glTexCoord3f(1, 1, -1)
    glVertex3f(size, size, -size)
    glTexCoord3f(1, -1, -1)
    glVertex3f(size, -size, -size)
    glTexCoord3f(1, -1, 1)
    glVertex3f(size, -size, size)
    glTexCoord3f(1, 1, 1)
    glVertex3f(size, size, size)

    glTexCoord3f(1, 1, 1)
    glVertex3f(size, size, size)
    glTexCoord3f(1, -1, 1)
    glVertex3f(size, -size, size)
    glTexCoord3f(-1, -1, 1)
    glVertex3f(-size, -size, size)
    glTexCoord3f(-1, 1, 1)
    glVertex3f(-size, size, size)

    glTexCoord3f(-1, 1, 1)
    glVertex3f(-size, size, size)
    glTexCoord3f(-1, -1, 1)
    glVertex3f(-size, -size, size)
    glTexCoord3f(-1, -1, -1)
    glVertex3f(-size, -size, -size)
    glTexCoord3f(-1, 1, -1)
    glVertex3f(-size, size, -size)

    glTexCoord3f(-1, 1, 1)
    glVertex3f(-size, size, size)
    glTexCoord3f(-1, 1, -1)
    glVertex3f(-size, size, -size)
    glTexCoord3f(1, 1, -1)
    glVertex3f(size, size, -size)
    glTexCoord3f(1, 1, 1)
    glVertex3f(size, size, size)
    glTexCoord3f(-1, -1, 1)
    glVertex3f(-size, -size, size)
    glTexCoord3f(-1, -1, -1)
    glVertex3f(-size, -size, -size)
    glTexCoord3f(1, -1, -1)
    glVertex3f(size, -size, -size)
    glTexCoord3f(1, -1, 1)
    glVertex3f(size, -size, size)

    glEnd()

    glDisable(GL_TEXTURE_CUBE_MAP)
    glEnable(GL_LIGHTING)
    glDepthMask(GL_TRUE)
"""
def center_model(vertices):
    x_min = min(vertices, key=lambda v: v[0])[0]
    x_max = max(vertices, key=lambda v: v[0])[0]
    y_min = min(vertices, key=lambda v: v[1])[1]
    y_max = max(vertices, key=lambda v: v[1])[1]
    z_min = min(vertices, key=lambda v: v[2])[2]
    z_max = max(vertices, key=lambda v: v[2])[2]
    center_x = (x_min + x_max) / 2
    center_y = (y_min + y_max) / 2
    center_z = (z_min + z_max) / 2
    centered_vertices = [[v[0] - center_x, v[1] - center_y, v[2] - center_z] for v in vertices]
    return centered_vertices

def load_texture(filename):
    texture_surface = pygame.image.load(filename)
    texture_data = pygame.image.tostring(texture_surface, "RGBA", True)
    texture_width, texture_height = texture_surface.get_rect().size
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, texture_width, texture_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
    return texture_width, texture_height, texture_data, texture_id

def draw_obj(vertices, faces, texture_data, texture_id, texture_width, texture_height):
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, texture_width, texture_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)

    glDisable(GL_LIGHTING)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    glBegin(GL_TRIANGLES)
    #glColor4f(1.0, 1.0, 0.0, 0.5)
    for face in faces:
        for vertex_index in face:
            vertex = vertices[vertex_index-1]
            glTexCoord2f(vertex[0], vertex[1])
            glVertex3fv(vertex)
    glEnd()

    glDisable(GL_TEXTURE_2D)
    glDisable(GL_BLEND)
    glEnable(GL_LIGHTING)


def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, [0.1, 0.1, 0.1, 1.0])
    glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, [1.0, 1.0, 1.0, 0.0])
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [0.5, 0.5, 1.0, 0.0])
    glMaterialfv(GL_FRONT_AND_BACK, GL_SHININESS, 10.0)

    # Set light properties
    glLightfv(GL_LIGHT0, GL_POSITION, [0.0, -10.0, 0.0, 1.0])
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 0.0])
    glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 0.0])

    
    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -5)

    # Load OBJ file and texture
    vertices, faces = load_obj('cow.obj')
    centered_vertices = center_model(vertices)
    texture_width, texture_height, texture_data, texture_id = load_texture('texture.jpg')

    # Set initial camera position and rotation
    camera_x = 0.0
    camera_y = 0.0
    camera_z = -5.0
    camera_pitch = 0.0
    camera_yaw = 0.0

    # Set initial field of view
    fov_horizontal = 45.0
    fov_vertical = 45.0
    """skybox_filenames = [
    'right.png',
    'left.png',
    'top.png',
    'bottom.png',
    'front.png',
    'back.png']
    cube_map = create_cube_map(skybox_filenames)
    skybox_size = 10"""
    prev_mouse_pos = pygame.mouse.get_pos()
    model_x = 0
    model_y = 0
    x_offset = 0.0
    y_offset = 0.0
    sensitivity = 0.1
    mouse_down = False
    prev_pos = None
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    fov_vertical -= 1.0
                elif event.button == 5:
                    fov_vertical += 1.0

    # Update camera based on mouse movement
        mouse_pos = pygame.mouse.get_pos()
        mouse_rel = pygame.mouse.get_rel()
        if pygame.mouse.get_pressed()[0]:
            camera_yaw += mouse_rel[0] * sensitivity
            camera_pitch += mouse_rel[1] * sensitivity
            if camera_pitch < -90.0:
                camera_pitch = -90.0
            elif camera_pitch > 90.0:
                camera_pitch = 90.0

        # Handle user input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            camera_x += math.sin(math.radians(camera_yaw))
            camera_z += math.cos(math.radians(camera_yaw))
        if keys[pygame.K_s]:
            camera_x -= math.sin(math.radians(camera_yaw))
            camera_z -= math.cos(math.radians(camera_yaw))
        if keys[pygame.K_a]:
            camera_x -= math.sin(math.radians(camera_yaw - 90))
            camera_z -= math.cos(math.radians(camera_yaw - 90))
        if keys[pygame.K_d]:
            camera_x += math.sin(math.radians(camera_yaw - 90))
            camera_z += math.cos(math.radians(camera_yaw - 90))
        if keys[pygame.K_q]:
            camera_pitch += 1
        if keys[pygame.K_e]:
            camera_pitch -= 1
        if keys[pygame.K_LEFT]:
            camera_yaw += 1
        if keys[pygame.K_RIGHT]:
            camera_yaw -= 1
        if keys[pygame.K_UP]:
            fov_vertical -= 1
        if keys[pygame.K_DOWN]:
            fov_vertical += 1
        if keys[pygame.K_KP_PLUS]:
            fov_horizontal -= 1
        if keys[pygame.K_KP_MINUS]:
            fov_horizontal += 1

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)
        #draw_skybox(cube_map, skybox_size)
        glClearColor(0.0, 0.0, 0.0, 0.0)

        # Set camera position and rotation
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(-camera_x, -camera_y, -camera_z)
        glRotatef(camera_pitch, 1.0, 0.0, 0.0)
        glRotatef(camera_yaw, 0.0, 1.0, 0.0)

        # Set field of view
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(fov_vertical, (display[0] / display[1]), 0.1, 50.0)
        
        # Draw ground plane
        glColor3f(0.0, 0.0, 0.5)  # Set ground plane color to dark blue
        glBegin(GL_QUADS)
        glVertex3f(-10, 0, -10)
        glVertex3f(-10, 0, 10)
        glVertex3f(10, 0, 10)
        glVertex3f(10, 0, -10)
        glEnd()


        # Draw OBJ file with shadow
        light_position = np.array([0.0, 0.0, 10.0, 10.0])
        draw_obj_with_shadow(centered_vertices, faces, texture_data, texture_id, texture_width, texture_height, light_position)

        pygame.display.flip()
        pygame.time.wait(10)

if __name__ == '__main__':
    main()
