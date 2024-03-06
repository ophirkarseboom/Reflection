import psutil

image_types = ["apng", "avif", "gif", "jpg", "jpeg", "jfif", "pjpeg", "pjp", "png", "svg", "webp", "bmp", "ico",
                   "cur",
                   "tif", "tiff"]

default_for_type = {'docx': 'WINWORD.EXE',
                    'pptx': 'POWERPNT.EXE',
                    'ppt': 'POWERPNT.EXE',
                    'zip': 'explorer.exe',
                    **{img: 'Microsoft.Photos.exe' for img in image_types},
                    'xlsx': 'EXCEL.EXE'}

def get_all_pid(process_name):
    """
    gets all processes running with process_name got
    :param process_name: the type of process
    :return: all processes running with the same process name
    """
    current = []
    for proc in psutil.process_iter():
        if proc.name() == process_name:
            current.append(proc.pid)

    return current

def get_process_name(file_path: str):
    """
    gets process name by file path
    :param file_path: path of file
    :return: process name of file
    """
    file_extension = file_path[file_path.rfind('.') + 1:]
    if file_extension in default_for_type:
        process_name = default_for_type[file_extension]
    else:
        process_name = 'Notepad.exe'

    return process_name

def wait_for_process_to_close(pid):
    """
    waiting for process to close
    :param pid: the process id
    :return: None
    """
    while psutil.pid_exists(pid):
        pass
