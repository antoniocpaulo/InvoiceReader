from multiprocessing import freeze_support
import os
import sys


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__name__)))
    return os.path.join(base_path, relative_path)


# determine if application is a script file or frozen exe
if getattr(sys, 'frozen', False):
    exe_file_path = os.path.dirname(sys.executable)
else:
    exe_file_path = resource_path(os.path.dirname(os.path.realpath(__name__)))

main_file_path = resource_path(os.path.dirname(os.path.realpath(__name__)))
os.environ["PATH"] += os.pathsep + os.pathsep.join([exe_file_path + r"\bin\poppler"])
app_icon_path = main_file_path + r"\bin\aux_img\icon2.ico"
last_used_filepath = exe_file_path
first_run = True
freeze_support()

from .GUI.GUI_Interface import GuiInterface

app = GuiInterface(icon_path=app_icon_path,
                   main_path=main_file_path,
                   exe_path=exe_file_path)

app.wm_state('zoomed')
app.protocol("WM_DELETE_WINDOW", app.on_delete)
