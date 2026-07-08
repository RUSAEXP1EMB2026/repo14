from modules import spreadsheet


def process_line_commands():
    commands = spreadsheet.get_pending_commands()

    for command in commands:
        row_number = command.get("_row_number")
        if row_number:
            spreadsheet.mark_command_done(row_number)

    return commands
