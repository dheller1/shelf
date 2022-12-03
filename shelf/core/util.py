import os


def try_delete_file(path, logger=None):
    try:
        os.remove(path)
        return True
    except (IOError, OSError) as e:
        if logger:
            logger.error(f"Cannot delete file '{path}': {e}")
        return False


def try_delete_directory(path, logger=None):
    try:
        os.rmdir(path)
        return True
    except (IOError, OSError) as e:
        if logger:
            logger.error(f"Cannot delete directory '{path}': {e}")
        return False
