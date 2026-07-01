from modules import spreadsheet


def process_line_commands():
    commands = spreadsheet.get_pending_commands()
    return commands
