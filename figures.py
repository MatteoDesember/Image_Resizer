# paper size
A4_VERTICAL = 1
A4_HORIZONTAL = 2
A3_VERTICAL = 3
A3_HORIZONTAL = 4

# paper size [mm]
A3_WIDTH = 420
A3_HEIGHT = 297
A4_WIDTH = 297
A4_HEIGHT = 210

# 1 inch = mm_in_inch
mm_in_inch = 25.4


class Rectangle:
    name = None
    size = A4_VERTICAL
    x_start = None
    y_start = None
    x_center = None
    y_center = None
    x_end = None
    y_end = None
    width = None
    height = None
    pixel_per_inch = 5  # Default value is 5, but if user select 1 inch on zoomed_image this variable is changed

    def set_x_y_center(self, x_center, y_center):
        self.x_center = x_center
        self.y_center = y_center
        self.calculate()

    def set_size(self, size):
        self.size = size
        self.calculate()

    def calculate(self):
        # calculate start, end points and width and height depend on size type
        if self.size == A4_VERTICAL:
            self.name = "A4_V"
            self.x_start = self.x_center - (A4_HEIGHT / mm_in_inch * self.pixel_per_inch / 2)
            self.y_start = self.y_center - (A4_WIDTH / mm_in_inch * self.pixel_per_inch / 2)
            self.x_end = self.x_center + (A4_HEIGHT / mm_in_inch * self.pixel_per_inch / 2)
            self.y_end = self.y_center + (A4_WIDTH / mm_in_inch * self.pixel_per_inch / 2)
            self.width = A4_HEIGHT / mm_in_inch * self.pixel_per_inch
            self.height = A4_WIDTH / mm_in_inch * self.pixel_per_inch
        elif self.size == A4_HORIZONTAL:
            self.name = "A4_H"
            self.x_start = self.x_center - (A4_WIDTH / mm_in_inch * self.pixel_per_inch / 2)
            self.y_start = self.y_center - (A4_HEIGHT / mm_in_inch * self.pixel_per_inch / 2)
            self.x_end = self.x_center + (A4_WIDTH / mm_in_inch * self.pixel_per_inch / 2)
            self.y_end = self.y_center + (A4_HEIGHT / mm_in_inch * self.pixel_per_inch / 2)
            self.width = A4_WIDTH / mm_in_inch * self.pixel_per_inch
            self.height = A4_HEIGHT / mm_in_inch * self.pixel_per_inch
        elif self.size == A3_VERTICAL:
            self.name = "A3_V"
            self.x_start = self.x_center - (A3_HEIGHT / mm_in_inch * self.pixel_per_inch / 2)
            self.y_start = self.y_center - (A3_WIDTH / mm_in_inch * self.pixel_per_inch / 2)
            self.x_end = self.x_center + (A3_HEIGHT / mm_in_inch * self.pixel_per_inch / 2)
            self.y_end = self.y_center + (A3_WIDTH / mm_in_inch * self.pixel_per_inch / 2)
            self.width = A3_HEIGHT / mm_in_inch * self.pixel_per_inch
            self.height = A3_WIDTH / mm_in_inch * self.pixel_per_inch
        elif self.size == A3_HORIZONTAL:
            self.name = "A3_H"
            self.x_start = self.x_center - (A3_WIDTH / mm_in_inch * self.pixel_per_inch / 2)
            self.y_start = self.y_center - (A3_HEIGHT / mm_in_inch * self.pixel_per_inch / 2)
            self.x_end = self.x_center + (A3_WIDTH / mm_in_inch * self.pixel_per_inch / 2)
            self.y_end = self.y_center + (A3_HEIGHT / mm_in_inch * self.pixel_per_inch / 2)
            self.width = A3_WIDTH / mm_in_inch * self.pixel_per_inch
            self.height = A3_HEIGHT / mm_in_inch * self.pixel_per_inch

    # print short info about rectangle
    def info(self):
        print("[",
              self.x_start, self.y_start, "] [",
              self.x_center, self.y_center, "] [",
              self.x_end, self.y_end, "] [",
              self.width, self.height,
              "]")


class Line:
    # start and end points represent start and end line
    x_start = 0
    x_end = 0
    y_start = 0
    y_end = 0

    # print short info about line
    def info(self):
        print("[", self.x_start, self.y_start, "] [", self.x_end, self.y_end, "]")
