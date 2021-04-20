import os





def create_dir(path):
    try:
        os.makedirs(path)
        print("creat dir {}".format(path))
    except:
        pass


def is_image_path(imagepath):
    if isinstance(imagepath, str):
        if imagepath.lower().endswith(('bmp', 'dib', 'png', 'jpg', 'jpeg', 'pbm', 'pgm', 'ppm', 'tif', 'tiff')):
            return True
        else:
            return False
