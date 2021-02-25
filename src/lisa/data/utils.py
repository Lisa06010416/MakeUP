import os

import wget


def check_os():
    import platform
    if platform.system().lower() == "windows":
        return "win"
    elif platform.system().lower() == "darwin":
        return "mac"


def create_dir(path):
    try:
        os.makedirs(path)
    except OSError:
        print("Creation of the directory %s failed" % path)
    else:
        print("Successfully created the directory %s " % path)


def is_image_path(imagepath):
    if isinstance(imagepath, str):
        if imagepath.lower().endswith(('bmp', 'dib', 'png', 'jpg', 'jpeg', 'pbm', 'pgm', 'ppm', 'tif', 'tiff')):
            return True
        else:
            return False