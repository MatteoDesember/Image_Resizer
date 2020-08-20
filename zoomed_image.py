import cv2
from tkinter import *
from PIL import ImageTk, Image
import numpy as np
import math
from win32api import GetSystemMetrics
from figures import Rectangle, Line
import image


class ZoomedImage:
    # displayed_image - it is Tkinter image not opencv image
    displayed_image = None

    # draw frag - if True: draw line, if False: do not
    draw_flag = False

    line = Line

    def __init__(self, root, image):

        # Set up new window
        self.zoomed_window = Toplevel(root)
        self.zoomed_window.title("Zoomed Image")
        self.zoomed_window.bind("<Key>", self.on_keyboard_click)

        # Create a window and add on window resize listener
        self.frame = Frame(self.zoomed_window, border=0)  # , background="red")
        self.frame.bind("<Configure>", self.on_window_resize)
        self.frame.pack(expand="yes", fill="both")

        # Set up label where is stored image
        self.image_label = Label(self.frame, border=0)  # , background="yellow")
        self.image_label.pack(expand="yes")  # , fill="both")

        # Add some listeners
        self.image_label.bind('<Motion>', self.on_mouse_move_create_line)
        self.image_label.bind('<Button-1>', self.left_button_down)
        self.image_label.bind('<ButtonRelease-1>', self.left_button_release)

        # image is an original image
        self.image = image

        # Convert image to gray
        self.gray_image = cv2.cvtColor(self.image, cv2.COLOR_RGB2GRAY)

        # And then convert to color, so there is a gray image on which user can draw coloured figures
        self.cv_image = cv2.cvtColor(self.gray_image, cv2.COLOR_BGR2RGB)

        # cv_displayed_image is an image to draw on it
        self.cv_displayed_image = self.cv_image.copy()

        # calculate aspect ratio - it's a width / height
        self.aspect_ratio = self.cv_image.shape[1] / self.cv_image.shape[0]

        # calculate zoom ratio - it's a: zommed image (displayed image) / original image width
        self.zoom_ratio = self.cv_displayed_image.shape[1] / self.cv_image.shape[1]

        # Get image size after zooming
        zoom = 10
        image_height_to_display = round(self.image.shape[0] * zoom)
        image_width_to_display = round(self.image.shape[1] * zoom)

        # Get max window width and height. An assumption is max window size is 80 percent of user monitor
        window_width = round(GetSystemMetrics(0) * 0.8)
        window_height = round(GetSystemMetrics(1) * 0.8)

        # So if image size after zooming is smaller than window, zoom image
        if image_height_to_display < window_height and image_width_to_display < window_width:
            window_width = image_width_to_display
            window_height = image_height_to_display

        # Set window size
        self.zoomed_window.geometry("{}x{}".format(window_width, window_height))

        # show image
        self.show_cv_image(self.cv_displayed_image)

        print("Select 1 inch and then..")

    '''
        left_button_down makes start point and end point so then on mouse move there can be line displayed
    '''

    def left_button_down(self, event):
        self.draw_flag = True
        self.line.x_start = event.x / self.zoom_ratio
        self.line.y_start = event.y / self.zoom_ratio
        self.line.x_end = event.x / self.zoom_ratio
        self.line.y_end = event.y / self.zoom_ratio
        self.draw_line()

    '''
        left_button_release - calculate diagonal (in reality it is just length of line)
    '''

    def left_button_release(self, event):
        self.draw_flag = False

        # Calculate diagonal (Pythagorean theorem)
        a = math.fabs(self.line.x_end - self.line.x_start)
        b = math.fabs(self.line.y_end - self.line.y_start)
        c = math.sqrt(a ** 2 + b ** 2)

        # Set pixel per inch
        Rectangle.pixel_per_inch = c
        self.draw_line()

    '''
        on_mouse_move_create_line - if there is draw_flag set to True the draw line
    '''

    def on_mouse_move_create_line(self, event):
        if self.draw_flag:
            self.line.x_end = event.x / self.zoom_ratio
            self.line.y_end = event.y / self.zoom_ratio
            self.draw_line()

    '''
        show_cv_image - shows image to user
    '''

    def show_cv_image(self, image):
        if type(image) == np.ndarray:
            self.displayed_image = ImageTk.PhotoImage(image=Image.fromarray(image))
        else:
            print("There is invalid type")

        self.image_label.configure(image=self.displayed_image)

    '''
        If user resizes window then resize image and figures on it
    '''

    def on_window_resize(self, event):

        # if window is bigger than image put an image at the center
        image_width = event.width
        image_height = int(event.width / self.aspect_ratio)

        if image_height > event.height:
            image_height = event.height
            image_width = int(event.height * self.aspect_ratio)

        # resize image and draw line on it
        self.cv_displayed_image = cv2.resize(self.cv_image, (image_width, image_height))
        self.zoom_ratio = self.cv_displayed_image.shape[1] / self.cv_image.shape[1]
        self.draw_line()

    '''
        draw_line draws line and put text on displayed image, then shows image to user
    '''

    def draw_line(self):
        # Copy displayed image so anything what is drawed on it is temporary
        image_with_line = self.cv_displayed_image.copy()

        # Draw line on image
        cv2.line(
            image_with_line,
            (round(self.line.x_start * self.zoom_ratio), round(self.line.y_start * self.zoom_ratio)),
            (round(self.line.x_end * self.zoom_ratio), round(self.line.y_end * self.zoom_ratio)),
            (255, 255, 0),  # BGR Yellow
            2)

        # Put text on image
        cv2.putText(
            image_with_line,
            "1 inch",
            (round((self.line.x_start * self.zoom_ratio + self.line.x_end * self.zoom_ratio) / 2) - 50,
             round((self.line.y_start * self.zoom_ratio + self.line.y_end * self.zoom_ratio) / 2) - 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 0),  # BGR Yellow
            2)
        # Display image
        self.show_cv_image(image_with_line)

    '''
        Short keyboard event, print info if user pressed h or H
    '''

    def on_keyboard_click(self, event):
        if event.keycode == 72:  # 'h' or 'H'
            print(image.INFO)
