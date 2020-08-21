import tkinter as tk
from tkinter import filedialog
from image import *

'''
    open_file_dialog opens file dialog and return selected file chosen by user as string
'''


def open_file_dialog():
    file_path = tk.filedialog.askopenfilename()
    # file_dir = os.path.dirname(os.path.abspath(file))
    # file_name = os.path.basename(os.path.abspath(file))
    return file_path


root = Tk()
root.title("Select an image...")
print("Select an image...")

image_path = open_file_dialog()
# image_path = 'test/IMG_4711.JPG'
if image_path:
    my_image = MyImage(image_path, root)
    root.mainloop()
else:
    print("Cant open a file. Exit program...")
