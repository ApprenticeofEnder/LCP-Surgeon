from zipfile import ZipFile
import json
import shutil
import logging
import sys
import io
from fastapi import UploadFile, File

log_level = logging.DEBUG

logging.basicConfig(
    format='[%(levelname)s] - %(message)s',
    level=log_level
)

def read_json(lcp_file: ZipFile, filename: str):
    data = read_file_in_lcp(lcp_file, filename)
    if data is not None:
        return json.loads(data)
    return data

def read_file_in_lcp(lcp_file: ZipFile, filename: str):
    try:
        with lcp_file.open(filename, 'r') as data_file:
            data = data_file.read()
            return data
    except KeyError:
        logging.info(f"Could not find {filename} file in LCP. Skipping.")
        return None

def fix_frame_stats(frame_stats: dict, frame_name: str):
    for stat, value in frame_stats.items():
        try:
            frame_stats[stat] = int(value)
        except ValueError as v:
            logging.warning(f"Invalid integer value for {stat} on {frame_name}. This may be intentional. Value: {value}")

def frame_data_convert(lcp_file: ZipFile):
    frame_list = read_json(lcp_file, 'frames.json')
    if frame_list is None:
        return None
    for frame in frame_list:
        fix_frame_stats(frame["stats"], frame["name"])
    return json.dumps(frame_list)

def fix_weapon_data(weapon_data: dict):
    weapon_name = weapon_data['name']
    for range_dict in weapon_data["range"]:
        try:
            range_dict['val'] = int(range_dict['val'])
        except ValueError as v:
            logging.warning(f"Invalid integer value for {range_dict['type']} on {weapon_name}. This may be intentional. Value: {range_dict['val']}")
        logging.debug(range_dict)
    for damage_dict in weapon_data["damage"]:
        try:
            damage_dict['val'] = int(damage_dict['val'])
        except ValueError as v:
            logging.warning(f"Invalid integer value for {damage_dict['type']} damage on {weapon_name}. This may be intentional. Value: {damage_dict['val']}")
        logging.debug(damage_dict)
    logging.debug(weapon_data)

def weapon_data_convert(lcp_file: ZipFile):
    weapon_list = read_json(lcp_file, 'weapons.json')
    if weapon_list is None:
        return None
    for weapon in weapon_list:
        fix_weapon_data(weapon)
    return json.dumps(weapon_list)

def process_lcp(uploaded_file: UploadFile) -> bytes:
    untouched_filenames = [
        'lcp_manifest.json',
        'actions.json',
        'bonds.json',
        'mods.json',
        'npc_classes.json',
        'npc_features.json',
        'npc_templates.json',
        'pilot_gear.json',
        'statuses.json',
        'systems.json',
        'tags.json',
        'talents.json'
    ]
    untouched_files = {x: bytes() for x in untouched_filenames}
    with ZipFile(uploaded_file.file) as lcp_file:
        new_frames = frame_data_convert(lcp_file)
        new_weapons = weapon_data_convert(lcp_file)
        for untouched_file in untouched_files:
            untouched_files[untouched_file] = read_file_in_lcp(lcp_file, untouched_file)
    new_lcp = io.BytesIO()
    with ZipFile(new_lcp, 'w') as new_lcp_file:
        for untouched_filename, untouched_file in untouched_files.items():
            if untouched_file is not None:
                new_lcp_file.writestr(untouched_filename, untouched_file)
        new_lcp_file.writestr('frames.json', new_frames)
        new_lcp_file.writestr('weapons.json', new_weapons)
    return new_lcp.getvalue()

# def main():
#     filename = input('Enter Filename: ')
#     try:
#         shutil.copyfile(filename, f"{filename}.bak")
#         with ZipFile(filename) as lcp_file:
#             new_frame_list = frame_data_convert(lcp_file)
#             new_weapon_list = weapon_data_convert(lcp_file)
#     except FileNotFoundError:
#         logging.error(f"Could not find file: {filename}. Please verify whether the file exists.")

# if __name__ == "__main__":
#     main()
