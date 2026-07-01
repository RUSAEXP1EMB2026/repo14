from modules import spreadsheet


def info(target, action, result=""):
    spreadsheet.save_control_log(target, action, result)
