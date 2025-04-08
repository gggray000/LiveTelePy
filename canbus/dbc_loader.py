import cantools

def load_dbc(file_path):
    return cantools.database.load_file(file_path)