"""
Utility methods that allow to pre-load game data.
"""

import io
import glob
import os.path

assets_data = dict()


def load_assets_from_folder(assets_base_folder):
    """
    Load all files from the given folder as game assets.
    """
    glob_str = os.path.normpath(os.path.join(assets_base_folder, "**"))
    for filename in glob.iglob(glob_str, recursive=True):

        # only files, no folders
        if not os.path.isfile(filename):
            continue

        # read file
        with open(filename, "rb") as f:
            data = f.read()

        # store it in memory
        key = os.path.relpath(filename, start=assets_base_folder)
        assets_data[key] = data


def get_asset_data(asset_name):
    """
    Returns a byte array for the given asset.
    asset_name is the path within the assets foolder.
    raises a FileNotFound exception, if the given asset does not exist.
    """
    try:
        return assets_data[asset_name]
    except KeyError:
        raise FileNotFoundError()


def get_asset_file(asset_name):
    """
    Returns a file-like object for the given asset.
    asset_name is the path within the assets foolder.
    raises a FileNotFound exception, if the given asset does not exist.
    """
    data = get_asset_data(asset_name)
    return io.BytesIO(data)


def get_asset_text_file(asset_name):
    """
    Returns a text-file-like object for the given asset.
    asset_name is the path within the assets foolder.
    raises a FileNotFound exception, if the given asset does not exist.
    """
    binary_file = get_asset_file(asset_name)
    return io.TextIOWrapper(binary_file, 'utf-8')
