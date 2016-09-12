# ==============================
# Alex Thimineur and Nick Rizzo
# CSC345: Computer Graphics
#   Fall 2016
# linimation
#   Creates a crazy line screen saver style
#   This line goes OFF THE WALLS
# ==============================

from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import sys
import math
from random import randint

winWidth = 640
winHeight = 480
name = b'POKEMON-GO-TO-THE-POLLS!' # name of program (shows up on window)

DELAY = 10 # delay between animations (can be increased/decreased using A and D keys respectively)
pause = False # if animation is paused or not (space key toggles)

class Grid:
    def __init__(self):
        self.grid_list_vertical = []
        self.grid_list_horizontal = []
        self.spacing = .2
        self.line_number_vertical = 10
        self.line_number_horizontal = 10
        self.loop_num = 0
        self.loop_limit = 200
        self.brightness_direction = 0
        self.color = Color(1, 1, 1)

    def set_grid_list(self):
        self.grid_list_vertical.append(Line(0, 0, 0, 1))
        for i in range(self.line_number_vertical):
            self.grid_list_vertical.append(self.get_next_grid_line_vertical())
        self.grid_list_horizontal.append(Line(0, 0, 1, 0))
        for i in range(self.line_number_horizontal):
            self.grid_list_horizontal.append(self.get_next_grid_line_horizontal())

    def get_next_grid_line_vertical(self):
        previous_line = self.grid_list_vertical[len(self.grid_list_vertical) - 1]
        return Line(previous_line.x1 + self.spacing, previous_line.y1, previous_line.x2 + self.spacing, previous_line.y2)

    def get_next_grid_line_horizontal(self):
        previous_line = self.grid_list_horizontal[len(self.grid_list_horizontal) - 1]
        return Line(previous_line.x1, previous_line.y1 + self.spacing, previous_line.x2, previous_line.y2 + self.spacing)

    def get_brightness_vertical(self):
        return 1 * ((self.loop_num + 1) / self.loop_limit)

    def get_brightness_horizontal(self):
        return 1 * ((self.loop_num + 1) / self.loop_limit)

    def update_loop_num(self):
        if self.loop_num < 0:
            self.brightness_direction = 1
        elif self.loop_num > self.loop_limit:
            self.brightness_direction = 0

        if self.brightness_direction == 1:
            self.loop_num += 1
        else:
            self.loop_num -= 1

class Color:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b
        self.current_r = r
        self.current_g = g
        self.current_b = b

    def get_next_color(self):
        new_color = Color(self.current_r, self.current_g, self.current_b)
        while not self.is_equal_to(new_color):
            new_color.r = randint(0, 1)
            new_color.g = randint(0, 1)
            new_color.b = randint(0, 1)

            if new_color.r == 0 and new_color.g == 0 and new_color.b == 0:
                new_color.r = 1
                new_color.g = 1
                new_color.b = 1

        self.r = new_color.r
        self.g = new_color.g
        self.b = new_color.b
        self.current_r = self.r
        self.current_g = self.g
        self.current_b = self.b


    def is_equal_to(self, other_color):
        if self.r == other_color.r and self.g == other_color.g and self.b == other_color.b:
            return False
        else:
            return True

# class represents a line
class Line:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    # checks if two lines are equal
    def is_equal_to(self, other_line):
        if self.x1 == other_line.x1 and self.x2 == other_line.x2 and self.y1 == other_line.y1 and self.y2 == other_line.y2:
            return True
        else:
            return False


# class represents a list of vectors
class Vectors:

    def __init__(self):
        self.vectors = []
        self.y_difference2 = 0.0
        self.x_difference2 = 0.0
        self.y_difference1 = 0.0
        self.x_difference1 = 0.0
        self.y_magnitude = 0.0
        self.x_magnitude = 0.0
        self.vector_number = 200
        self.color = Color(1,1,1)

    # sets list of vectors at start
    def set_start(self):
        # set translation speeds between each vector
        self.y_difference2 = 0.002
        self.x_difference2 = -0.002
        self.y_difference1 = -0.002
        self.x_difference1 = 0.002
        self.x_magnitude = 0.002
        self.y_magnitude = -0.002

        # add starting vectors to list of vectors
        self.vectors.append(Line(randint(0, 10) / 10, randint(0, 10) / 10, randint(0, 10) / 10, randint(0, 10) / 10))
        for i in range(self.vector_number):
            self.add_vector()

        # set color of vectors to random color (can be changed with 'c' key)
        self.color.get_next_color()

    # adds a vector to list to be drawn
    # if a vector would go out of the window, it is reset along with it's movement to go the opposite direction
    # Also, whenever a line collides with a wall, a random modifier is applied to a random point as well as it being sent in the opposite direction
    # a repeated line will also cause a random modifier to occur
    def add_vector(self):
        temp = self.get_next_vector()
        is_x_collision = self.handle_x_collisions(temp)
        is_y_collision = self.handle_y_collisions(temp)
        is_repeat = temp.is_equal_to(self.get_last_vector())
        if is_x_collision or is_y_collision or is_repeat:
            self.apply_random_translation()
        self.vectors.append(temp)

    # gets the next vector that will be placed in the list based off of the last vector in the list of vectors
    def get_next_vector(self):
        return Line(
            self.get_last_vector().x1 + self.x_difference1 + self.x_magnitude,
            self.get_last_vector().y1 + self.y_difference1 + self.y_magnitude,
            self.get_last_vector().x2 + self.x_difference2 + self.x_magnitude,
            self.get_last_vector().y2 + self.y_difference2 + self.y_magnitude)

    # handles collisions regarding x coordinates and walls
    def handle_x_collisions(self, temp):
        is_collision = False
        if temp.x2 < 0:
            self.x_difference2 *= -1
            self.x_magnitude *= -1
            is_collision = True
            temp.x2 = 0
        elif temp.x2 > 1:
            self.x_difference2 *= -1
            self.x_magnitude *= -1
            is_collision = True
            temp.x2 = 1

        if temp.x1 < 0:
            self.x_difference1 *= -1
            self.x_magnitude *= -1
            is_collision = True
            temp.x1 = 0
        elif temp.x1 > 1:
            self.x_difference1 *= -1
            self.x_magnitude *= -1
            is_collision = True
            temp.x1 = 1
        return is_collision

    # handles collisions regarding y coordinates and walls
    def handle_y_collisions(self, temp):
        is_collision = False
        if temp.y2  < 0:
            self.y_difference2 *= -1
            self.y_magnitude *= -1
            is_collision = True
            temp.y2 = 0
        elif temp.y2 > 1:
            self.y_difference2 *= -1
            self.y_magnitude *= -1
            is_collision = True
            temp.y2 = 1

        if temp.y1 < 0:
            self.y_difference1 *= -1
            self.y_magnitude *= -1
            is_collision = True
            temp.y1 = 0

        elif temp.y1 > 1:
            self.y_difference1 *= -1
            self.y_magnitude *= -1
            is_collision = True
            temp.y1 = 1

        return is_collision

    # applies a random translation to a random point
    def apply_random_translation(self):
        randomPoint = randint(0, 3)
        if randomPoint == 0:
            self.x_difference1 = self.get_speed(randint(0, 1)) * self.get_sign(randint(0, 1))
        elif randomPoint == 1:
            self.x_difference2 = self.get_speed(randint(0, 1)) * self.get_sign(randint(0, 1))
        elif randomPoint == 2:
            self.y_difference1 = self.get_speed(randint(0, 1)) * self.get_sign(randint(0, 1))
        else:
            self.y_difference2 = self.get_speed(randint(0, 1)) * self.get_sign(randint(0, 1))

    # removes last vector in list of vectors
    def remove_last_vector(self):
        del self.vectors[0]

    # gets last vector in list of vectors
    def get_last_vector(self):
        return self.vectors[len(self.vectors) - 1]

    # gets speed of vector
    def get_speed(self, speedNum):
        if speedNum == 0:
            return 0.0
        else:
            return 0.002

    # gets sign of vector
    def get_sign(self, signNum):
        if signNum == 0:
            return 1
        else: return -1

    # gets brightness of next vector
    def get_brightness(self, vectors_index):
        return 1 * ((vectors_index + 1) / self.vector_number)


vectors = Vectors() # list of vectors to be drawn
grid = Grid()

# creates window
def main():
    global grid
    global vectors
    vectors.set_start()
    grid.set_grid_list()
    # Create the initial window
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(winWidth, winHeight)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(name)

    init()

    # This callback is invoked when window needs to be drawn or redrawn
    glutDisplayFunc(display)

    # This callback is invoked when a keyboard event happens
    glutKeyboardFunc(keyboard);

    glutTimerFunc(DELAY, timer, 0)

    # Enters the main loop.
    # Displays the window and starts listening for events.
    glutMainLoop()
    return


def timer(alarm):
    global degree
    glutTimerFunc(DELAY, timer, 0)
    if not pause: # if animation is not paused (via space key)
        glutPostRedisplay()


# Initialize some of the OpenGL matrices
def init():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0.0, 1.0, 0.0, 1.0)



# Callback function used to display the scene
# Currently it just draws a simple polyline (LINE_STRIP)

def display():
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClear(GL_COLOR_BUFFER_BIT)

    global grid
    for line in grid.grid_list_vertical:
        glColor3f(grid.color.r * grid.get_brightness_vertical(), grid.color.g * grid.get_brightness_vertical(), grid.color.b * grid.get_brightness_vertical())
        glBegin(GL_LINE_STRIP)
        glVertex3f(line.x1, line.y1, 0)  # plots point 1
        glVertex3f(line.x2, line.y2, 0)  # connects line to point 2
        glEnd()

    for line in grid.grid_list_horizontal:
        glColor3f(grid.color.r * grid.get_brightness_vertical(), grid.color.g * grid.get_brightness_vertical(), grid.color.b * grid.get_brightness_vertical())
        glBegin(GL_LINE_STRIP)
        glVertex3f(line.x1, line.y1, 0)  # plots point 1
        glVertex3f(line.x2, line.y2, 0)  # connects line to point 2
        glEnd()

    grid.update_loop_num()
    if grid.loop_num == 0:
        grid.color.get_next_color()


    global vectors
    vectors.add_vector() # adds new vector to draw first
    vectors.remove_last_vector() # removes last vector drawn last iteration
    vector_number = 0
    # loops through each vector in list of vectors and draws them with appropriate location and brightness
    for vector in vectors.vectors:
        # sets color and brightness for each line drawn
        glColor3f(vectors.color.r * vectors.get_brightness(vector_number), vectors.color.g * vectors.get_brightness(vector_number), vectors.color.b * vectors.get_brightness(vector_number))
        # creates a new line strip
        glBegin(GL_LINE_STRIP)
        glVertex3f(vector.x1, vector.y1, 0) # plots point 1
        glVertex3f(vector.x2, vector.y2, 0) # connects line to point 2
        glEnd()
        vector_number += 1
    glFlush()
    glutSwapBuffers()

# Callback function used to handle any key events
# Currently, it just responds to the ESC key (which quits)
# key: ASCII value of the key that was pressed
# x,y: Location of the mouse (in the window) at time of key press)
def keyboard(key, x, y):
    global DELAY
    if ord(key) == 27:  # ESC (exits program)
        exit(0)
    if ord(key) == 32: # Space (pauses animation)
        global pause
        pause = not pause
    if ord(key) == 97 or ord(key) == 65: # A (slows down animation)
        DELAY += 10
    if ord(key) == 68 or ord(key) == 100: # D (speeds up animation)
        if DELAY > 0:
            DELAY -= 10
    if ord(key) == 67 or ord(key) == 99: # C (changes color)
        global vectors
        vectors.color.get_next_color()

if __name__ == '__main__': main()
