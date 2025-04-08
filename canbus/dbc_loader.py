import cantools

def load_dbc(file_path):
    return cantools.db.load_file(file_path)