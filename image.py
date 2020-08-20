import copy
from fpdf import FPDF
from figures import *
import math
import os
import random
import string
from zoomed_image import ZoomedImage
from tkinter import *
from PIL import ImageTk, Image
import numpy as np
import cv2
from win32api import GetSystemMetrics

INFO = """
*********************************************
*      h - HELP                             *
*      z - select zoom range                *
* Return - zoom range                       *
*      1 - set paper size to A4_VERTICAL    *
*      2 - set paper size to A4_HORIZONTAL  *
*      3 - set paper size to A3_VERTICAL    *
*      3 - set paper size to A3_HORIZONTAL  *
*      x - select a4 range                  *
*      s - save to PDF                      *
*********************************************"""


class MyImage:
    # displayed_image - it is Tkinter image not opencv image
    displayed_image = None

    zoomed_image = None

    # list of sized rectangles
    rectangles = []

    # two rectangles - one custom_rectangle to select range to zoom, rectangle - it is sized rectangle bind to mouse
    rectangle = Rectangle()
    custom_rectangle = Rectangle()

    # draw frag - if True: draw line, if False: do not
    draw_flag = False

    def __init__(self, image_dir, root):

        # Set window
        self.root = root

        # Show window if there was hidden
        self.root.deiconify()
        self.root.title("Image Resizer")

        # Set some listeners
        # On on keyboard click can't be bind to image_label
        # So when pressed x, there must be offset calculated
        self.root.bind("<Key>", self.on_keyboard_click)

        # Set Frame in which there is label
        self.frame = Frame(self.root, border=0)  # , background="red")

        # Create frame and set listener
        self.frame.bind("<Configure>", self.on_window_resize)
        self.frame.pack(expand="yes", fill="both")

        # Set image label in which is stored image
        self.image_label = Label(self.frame, border=0)  # , background="yellow")
        self.image_label.pack(expand="yes")  # , fill="both")

        # Read image
        self.image_dir = image_dir
        self.image = cv2.imread(image_dir)

        # Convert image to gray
        self.gray_image = cv2.cvtColor(self.image, cv2.COLOR_RGB2GRAY)

        # Rotate image
        if self.gray_image.shape[0] > self.gray_image.shape[1]:
            self.gray_image = cv2.rotate(self.gray_image, cv2.ROTATE_90_CLOCKWISE)

        # And then convert to color, so there is a gray image on which user can draw coloured figures
        self.cv_image = cv2.cvtColor(self.gray_image, cv2.COLOR_GRAY2RGB)

        # cv_displayed_image is an image to draw on it
        self.cv_displayed_image = self.cv_image.copy()

        # Calculate aspect ratio - it's a width / height
        self.aspect_ratio = self.cv_image.shape[1] / self.cv_image.shape[0]

        # Calculate zoom ratio - it's a: zommed image (displayed image) / original image width
        self.zoom_ratio = self.cv_displayed_image.shape[1] / self.cv_image.shape[1]

        # Set rectangle center points
        self.rectangle.set_x_y_center(0, 0)

        # Create som listeners
        self.create_custom_rectangle_listeners()

        # Get max window width and height. An assumption is max window size is 80 percent of user monitor
        window_width = round(GetSystemMetrics(0) * 0.8)
        window_height = round(GetSystemMetrics(1) * 0.8)

        # So if image size after zooming is smaller than window, zoom image
        if self.cv_displayed_image.shape[0] < window_height or self.cv_displayed_image.shape[1] < window_width:
            window_width = self.cv_displayed_image.shape[1]
            window_height = self.cv_displayed_image.shape[0]

        # Set window size
        self.root.geometry("{}x{}".format(window_width, window_height))

    '''
        create_custom_rectangle_listeners sets some listeners which allow to draw custom rectangle
    '''

    def create_custom_rectangle_listeners(self):
        print("Select region to zoom. If selected press Enter")
        self.image_label.unbind('<Motion>')
        self.image_label.unbind('<ButtonRelease-1>')
        self.image_label.unbind('<Button-3>')

        self.image_label.bind('<Motion>', self.on_mouse_move_create_rectangle)
        self.image_label.bind('<Button-1>', self.left_button_down)
        self.image_label.bind('<ButtonRelease-1>', self.left_button_release)

    '''
        create_a4_listeners sets some listeners which allow to draw a4 rectangles
    '''

    def create_a4_listeners(self):
        print(" ..draw rectangles..")
        self.image_label.unbind('<Motion>')
        self.image_label.unbind('<ButtonRelease-1>')
        self.image_label.unbind('<Button-1>')

        self.image_label.bind('<Motion>', self.on_mouse_move_with_rectangle)
        self.image_label.bind('<ButtonRelease-1>', self.left_click)
        self.image_label.bind('<Button-3>', self.right_click)

    '''
        show_cv_image - shows image to user
    '''

    def show_cv_image(self, image):
        if type(image) == np.ndarray:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            self.displayed_image = ImageTk.PhotoImage(image=Image.fromarray(image))
        else:
            print("There is invalid type")

        self.image_label.configure(image=self.displayed_image)

    '''
        add_rectangles adds all rectangles in list to displayed image
    '''

    def add_rectangles(self):
        for index, rectangle in enumerate(self.rectangles):
            self.add_rectangle(self.cv_displayed_image, rectangle, self.zoom_ratio)
            self.put_text(self.cv_displayed_image,
                          str(index),
                          rectangle.x_center * self.zoom_ratio,
                          rectangle.y_center * self.zoom_ratio,
                          rectangle.width * self.zoom_ratio,
                          rectangle.height * self.zoom_ratio
                          )

    '''
        add_rectangle adds rectangle to image
    '''

    def add_rectangle(self, image, rectangle, ratio=1.0):
        cv2.rectangle(
            image,
            (round(rectangle.x_start * ratio), round(rectangle.y_start * ratio)),
            (round(rectangle.x_end * ratio), round(rectangle.y_end * ratio)),
            (0, 255, 0),  # BGR Green
            2)

    '''
        put_text adds text to image. 
        width - target text width
        height - target text height
    '''

    def put_text(self, image, text, x, y, width, height):
        # Default font_size and thickness
        font_size = 1.0
        thickness = 1

        # Calculate text_size to display
        (text_width, text_height), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_size, thickness)
        text_ratio = min(height / text_height, width / text_width)

        # Increase or decrease font size so the text will be target width or height
        font_size = font_size * text_ratio

        # Calculate thickness so text looks much better
        thickness = round(thickness * text_ratio * 0.5)

        # Calculate text_size to display again
        (text_width, text_height), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_size, thickness)

        cv2.putText(
            image,
            text,
            (round(x - text_width / 2),
             round(y + text_height / 2)),
            cv2.FONT_HERSHEY_SIMPLEX,
            font_size,
            (0, 255, 0),  # BGR
            thickness)

    '''
        remove rectangle from list at i position
    '''

    def remove_rectangle(self, i):
        if len(self.rectangles) == 0:
            print("Empty list")
        elif i >= len(self.rectangles):
            print("Invalid value")
        else:
            del self.rectangles[i]
            image_height, image_width = self.cv_displayed_image.shape[:2]
            self.cv_displayed_image = cv2.resize(self.cv_image, (image_width, image_height))
            self.add_rectangles()
            self.show_rectangle(self.rectangle)

    '''
        draw rectangle with user given shape using mouse
    '''

    def draw_custom_rectangle(self, rectangle):
        # Copy displayed image so anything what is drawed on it is temporary
        display_image = self.cv_displayed_image.copy()

        cv2.rectangle(
            display_image,
            (round(rectangle.x_start * self.zoom_ratio), round(rectangle.y_start * self.zoom_ratio)),
            (round(rectangle.x_end * self.zoom_ratio), round(rectangle.y_end * self.zoom_ratio)),
            (255, 0, 182),  # BGR Purple color
            2)

        self.show_cv_image(display_image)

    '''
        show_rectangle draw rectangle and text to image
    '''

    def show_rectangle(self, rectangle):
        # Copy displayed image so anything what is drawed on it is temporary
        display_image = self.cv_displayed_image.copy()
        cv2.rectangle(
            display_image,
            (round(rectangle.x_start * self.zoom_ratio), round(rectangle.y_start * self.zoom_ratio)),
            (round(rectangle.x_end * self.zoom_ratio), round(rectangle.y_end * self.zoom_ratio)),
            (0, 0, 255),  # BGR
            2)

        self.put_text(display_image,
                      rectangle.name,
                      rectangle.x_center * self.zoom_ratio,
                      rectangle.y_center * self.zoom_ratio,
                      rectangle.width * self.zoom_ratio,
                      rectangle.height * self.zoom_ratio
                      )

        self.show_cv_image(display_image)

    '''
        On left click add rectangle to list of rectangles, draw on image and display it
    '''

    def left_click(self, event):
        temp_rectangle = copy.copy(self.rectangle)
        self.add_rectangle(self.cv_displayed_image, temp_rectangle, self.zoom_ratio)
        self.put_text(self.cv_displayed_image,
                      str(len(self.rectangles)),
                      temp_rectangle.x_center * self.zoom_ratio,
                      temp_rectangle.y_center * self.zoom_ratio,
                      temp_rectangle.width * self.zoom_ratio,
                      temp_rectangle.height * self.zoom_ratio
                      )
        self.rectangles.append(temp_rectangle)
        self.show_cv_image(self.cv_displayed_image)

    '''
        On right click remove last rectangle from image and from list of rectangles
    '''

    def right_click(self, event):
        self.remove_rectangle(-1)

    '''
        on_mouse_move_create_rectangle draws custom rectangle on image
    '''

    def on_mouse_move_create_rectangle(self, event):
        if self.draw_flag:
            self.custom_rectangle.x_end = event.x / self.zoom_ratio
            self.custom_rectangle.y_end = event.y / self.zoom_ratio
            self.draw_custom_rectangle(self.custom_rectangle)

    '''
        move sized rectangle on image
    '''

    def on_mouse_move_with_rectangle(self, event):
        self.rectangle.set_x_y_center(
            event.x / self.zoom_ratio,
            event.y / self.zoom_ratio,
        )
        self.show_rectangle(self.rectangle)

    '''
        add image to pdf
    '''

    def put_image_into_pdf(self, image, pdf):
        # Create random string
        random_file_name = ''.join(random.choices(string.digits, k=5))

        # Get file extention
        file_extention = os.path.splitext(self.image_dir)[1]

        # If there is horizontal image rotate it 90 clockwise
        if image.shape[0] < image.shape[1]:
            image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)

        # Write temporary image to disk
        # I have no idea how to make it better way
        # As I know there is no way to put cv2 image or file image directly to FPDF
        # And there is next issue: FPDF saves image in 72 DPI. There is no way to increse that
        # so the images cant be lower quality
        # If there would be easy way to save in original DPI there would be fantastic!
        cv2.imwrite("_temp_" + random_file_name + file_extention, image)

        # Add page and put image to pdf page
        pdf.add_page()
        pdf.image("_temp_" + random_file_name + file_extention, x=0, y=0, w=210, h=297, type='', link='')

        # Remove temporary image from disk
        os.remove("_temp_" + random_file_name + file_extention)

    '''
        left_button_down makes start point and end point so then on mouse move there can be rectangle displayed
    '''

    def left_button_down(self, event):
        self.draw_flag = True
        self.custom_rectangle.x_start = event.x / self.zoom_ratio
        self.custom_rectangle.y_start = event.y / self.zoom_ratio
        self.custom_rectangle.x_end = event.x / self.zoom_ratio
        self.custom_rectangle.y_end = event.y / self.zoom_ratio
        self.draw_custom_rectangle(self.custom_rectangle)

    '''
        left_button_release makes end point and draw custom rectangle
    '''

    def left_button_release(self, event):
        self.draw_flag = False

        # If there is situation where start_x or start_y is little further (from 0, 0 coordinating system), rotate rectangle
        # There is no effect while drawing rectangle but when exporting part of image there is important where are taht points
        # e.g.
        # BEFORE:
        # x_stat, y_start
        #       |-----------------v
        #                  -------
        #                 |       |
        #                 |       |
        #                  -------
        #       |---------^
        # x_end, y_end
        #
        # AFTER:
        # x_end, y_end
        #       |-----------------v
        #                  -------
        #                 |       |
        #                 |       |
        #                  -------
        #       |---------^
        # x_stat, y_start

        if self.custom_rectangle.x_start is not None and self.custom_rectangle.x_end is not None and self.custom_rectangle.x_start > self.custom_rectangle.x_end:
            temp = self.custom_rectangle.x_end
            self.custom_rectangle.x_end = self.custom_rectangle.x_start
            self.custom_rectangle.x_start = temp

        if self.custom_rectangle.y_start is not None and self.custom_rectangle.y_end is not None and self.custom_rectangle.y_start > self.custom_rectangle.y_end:
            temp = self.custom_rectangle.y_end
            self.custom_rectangle.y_end = self.custom_rectangle.y_start
            self.custom_rectangle.y_start = temp
        self.draw_custom_rectangle(self.custom_rectangle)

    '''
        keyboard event, print info if user pressed h or H
    '''

    def on_keyboard_click(self, event):
        if event.keycode == 49:  # '1'
            self.rectangle.set_size(A4_VERTICAL)
            self.show_rectangle(rectangle=self.rectangle)
        elif event.keycode == 50:  # '2'
            self.rectangle.set_size(A4_HORIZONTAL)
            self.show_rectangle(rectangle=self.rectangle)
        elif event.keycode == 51:  # '3'
            self.rectangle.set_size(A3_VERTICAL)
            self.show_rectangle(rectangle=self.rectangle)
        elif event.keycode == 52:  # '4'
            self.rectangle.set_size(A3_HORIZONTAL)
            self.show_rectangle(rectangle=self.rectangle)
        elif event.keycode == 83:  # 's', 'S'
            self.save()
        # elif event.keycode == 68:  # 'd', 'D'
        #     rectangle_to_delete = input("Which one to delete?\r\n")
        #     try:
        #         rectangle_to_delete = int(rectangle_to_delete)
        #     except ValueError:
        #         print("Insert number not text!")
        #     self.remove_rectangle(rectangle_to_delete)
        #     print("Deleted " + str(rectangle_to_delete), + " rectangle")
        elif event.keycode == 13:  # 'Return'
            if not self.draw_flag:
                if self.custom_rectangle.x_start != self.custom_rectangle.x_end or self.custom_rectangle.y_start != self.custom_rectangle.y_end:

                    if self.zoomed_image is not None:
                        self.zoomed_image.zoomed_window.destroy()

                    zoomed_image = self.cv_image[
                                   round(self.custom_rectangle.y_start):round(self.custom_rectangle.y_end),
                                   round(self.custom_rectangle.x_start):round(self.custom_rectangle.x_end)
                                   ]
                    self.zoomed_image = ZoomedImage(self.root, zoomed_image)
                    self.create_a4_listeners()
                else:
                    print("Does't select region to zoom, try again.")
        elif event.keycode == 90:  # 'z', 'Z'
            self.create_custom_rectangle_listeners()
            self.show_cv_image(self.cv_displayed_image)

        elif event.keycode == 88:  # 'x' or 'X'
            self.create_a4_listeners()

            # Because of there is no way to bind keyboard click to label there should be calculating offset
            offset_x = (self.root.winfo_width() - self.image_label.winfo_width()) / 2
            offset_y = (self.root.winfo_height() - self.image_label.winfo_height()) / 2

            self.rectangle.set_x_y_center(
                (event.x - offset_x) / self.zoom_ratio,
                (event.y - offset_y) / self.zoom_ratio,
            )
            self.show_rectangle(self.rectangle)

        elif event.keycode == 72:  # 'h' or 'H'
            print(INFO)

    '''
        If user resizes window then resize image and figures on it
    '''

    def on_window_resize(self, event):
        image_width = event.width
        image_height = int(event.width / self.aspect_ratio)

        if image_height > event.height:
            image_height = event.height
            image_width = int(event.height * self.aspect_ratio)

        self.cv_displayed_image = cv2.resize(self.cv_image, (image_width, image_height))
        self.zoom_ratio = self.cv_displayed_image.shape[1] / self.cv_image.shape[1]
        self.add_rectangles()
        self.show_cv_image(self.cv_displayed_image)

    '''
        Save to pdf
    '''

    def save(self):
        print("Saving to pdf...")

        # pdf_image is the original image ont resized, not displayed
        pdf_image = self.cv_image.copy()

        # For each rectangle in rectangles list draw rectangle and put text
        for index, rectangle in enumerate(self.rectangles):
            self.add_rectangle(pdf_image, rectangle)
            self.put_text(pdf_image,
                          str(index),
                          rectangle.x_center,
                          rectangle.y_center,
                          rectangle.width,
                          rectangle.height
                          )

            if rectangle.size == A3_HORIZONTAL or rectangle.size == A3_VERTICAL:
                text_1_x = 0
                text_1_y = 0
                text_2_x = 0
                text_2_y = 0

                # Becouse of A3 size is divided into two A4 size add two more texts
                # its easiest to handle that
                if rectangle.size == A3_VERTICAL:
                    text_1_x = rectangle.x_center
                    text_1_y = rectangle.y_center - rectangle.height / 4
                    text_2_x = rectangle.x_center
                    text_2_y = rectangle.y_center + rectangle.height / 4
                elif rectangle.size == A3_HORIZONTAL:
                    text_1_x = rectangle.x_center - rectangle.width / 4
                    text_1_y = rectangle.y_center
                    text_2_x = rectangle.x_center + rectangle.width / 4
                    text_2_y = rectangle.y_center

                self.put_text(pdf_image,
                              str(index) + ".1",
                              text_1_x,
                              text_1_y,
                              rectangle.width / 2,
                              rectangle.height / 2)
                self.put_text(pdf_image,
                              str(index) + ".2",
                              text_2_x,
                              text_2_y,
                              rectangle.width / 2,
                              rectangle.height / 2)

        # Create PDF
        pdf = FPDF(orientation='P', unit='mm', format='A4')
        self.put_image_into_pdf(pdf_image, pdf)

        # For each rectangle in rectangle list
        for index, rectangle in enumerate(self.rectangles):
            top = 0
            bottom = 0
            left = 0
            right = 0

            # Check if any part of rectangle is outside image
            if rectangle.x_start < 0:
                left = round(math.fabs(rectangle.x_start))
                rectangle.x_start = 0
            if rectangle.y_start < 0:
                top = round(math.fabs(rectangle.y_start))
                rectangle.y_start = 0
            if rectangle.x_end > (pdf_image.shape[1]):
                right = round(math.fabs(rectangle.x_end - pdf_image.shape[1]))
                rectangle.x_end = pdf_image.shape[1]
            if rectangle.y_end > (pdf_image.shape[0]):
                bottom = round(math.fabs(rectangle.y_end - pdf_image.shape[0]))
                rectangle.y_end = pdf_image.shape[0]

            # Get exact rectangle
            export_part = pdf_image[
                          round(rectangle.y_start):
                          round(rectangle.y_end),
                          round(rectangle.x_start):
                          round(rectangle.x_end)]  # [y1:y2, x1:x2]

            # If rectangle is over image then add white border
            export_part = cv2.copyMakeBorder(export_part,
                                             top,
                                             bottom,
                                             left,
                                             right,
                                             cv2.BORDER_CONSTANT,
                                             None,
                                             [255, 255, 255]  # White
                                             # [0, 0, 0]  # Black
                                             )

            # If there is A3 size divide into two parts
            if rectangle.size == A3_HORIZONTAL or rectangle.size == A3_VERTICAL:
                export_part_1 = None
                export_part_2 = None

                # Split A3 size into two A4 parts
                if rectangle.size == A3_VERTICAL:
                    export_part_1 = export_part[  # [y1:y2,x1:x2]
                                    0:round(export_part.shape[0] / 2),
                                    0:export_part.shape[1]
                                    ]
                    export_part_2 = export_part[  # [y1:y2, x1:x2]
                                    round(export_part.shape[0] / 2):export_part.shape[0],
                                    0:export_part.shape[1]
                                    ]
                elif rectangle.size == A3_HORIZONTAL:
                    export_part_1 = export_part[  # [y1:y2,x1:x2]
                                    0:export_part.shape[0],
                                    0:round(export_part.shape[1] / 2)
                                    ]
                    export_part_2 = export_part[  # [y1:y2, x1:x2]
                                    0:export_part.shape[0],
                                    round(export_part.shape[1] / 2):export_part.shape[1]
                                    ]

                # Export A3 in two A4 size
                self.put_image_into_pdf(export_part_1, pdf)
                self.put_image_into_pdf(export_part_2, pdf)
            else:
                # Export A4 size
                self.put_image_into_pdf(export_part, pdf)
        try:
            # Try to save to disk
            pdf.output(os.path.splitext(self.image_dir)[0] + ".pdf", "F")
            print(" ..Saved!")
        except:
            print(" ..There is a problem with saving PDF. Is it open?")

# def image_resize(self, image, target_width=None, target_height=None, inter=cv2.INTER_AREA):
#     # initialize the dimensions of the image to be resized and
#     # grab the image size
#     image_height, image_width = image.shape[:2]
#
#     # if both the width and height are None, then return the original image
#     if target_width is None and target_height is None:
#         return image
#
#     # if target width is none or height
#     if target_width is None or image_height > image_width:
#         # calculate the ratio of the height and construct the
#         # dimensions
#         ratio = target_height / float(image_height)
#         dim = int(image_width * ratio), target_height
#
#     # otherwise, the height is None
#     else:
#         # calculate the ratio of the width and construct the
#         # dimensions
#         ratio = target_width / float(image_width)
#         dim = target_width, int(image_height * ratio)
#
#     # resize the image
#     resized_image = cv2.resize(image, dim, interpolation=inter)
#
#     # return the resized image
#     return resized_image, ratio
# def adaptive_treshold(self, image, block_size, c_value):
#     gray_image_adaptive_treshold = cv2.adaptiveThreshold(src=image,
#                                                          maxValue=255,
#                                                          adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
#                                                          thresholdType=cv2.THRESH_BINARY,
#                                                          blockSize=block_size,
#                                                          C=c_value)
#     image = cv2.cvtColor(gray_image_adaptive_treshold, cv2.COLOR_BGR2RGB)
#     return image