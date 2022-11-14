import requests
from pathlib import Path
from datetime import datetime
import sys


def load_target_dirs(path='./targets.txt'):
    p = Path(path)
    if not p.exists():
        print('Target file not found')
        exit(1)

    f = p.open('r', encoding='utf-8')
    target_dirs = f.readlines()
    f.close()
    target_dirs = [d.strip() for d in target_dirs]
    return target_dirs


def load_target_extensions(path='./extensions.txt'):
    p = Path(path)
    if not p.exists():
        print('Extensions file not found')
        exit(1)

    f = p.open('r')
    target_extensions = f.readlines()
    f.close()
    target_extensions = [d.strip() for d in target_extensions]
    return target_extensions


def process_dir(target_dir, target_extensions, eagle_folder):
    p = Path(target_dir)
    print(p)
    if not p.exists():
        print('Target directory {} not found'.format(target_dir))
        return
    today = datetime.today().strftime('%Y-%m-%d')
    archive_dir = p.joinpath(today)
    if not archive_dir.exists():
        archive_dir.mkdir()
    for extension in target_extensions:
        move_files_and_register(target_dir, archive_dir,
                                extension, eagle_folder)


def move_files_and_register(target_dir, archive_dir, extension, eagle_folder):
    p = Path(target_dir)

    items = []
    for f in p.glob('*.' + extension):
        print('Moving file {}'.format(f.name))
        item = f.rename(archive_dir.joinpath(f.name))
        items.append(item)
    if len(items) > 0:
        register_files(items, eagle_folder)


def register_files(files, eagle_folder):
    items = [
        {
            'path': str(f.absolute()),
            'name': f.stem
        } for f in files]
    r = requests.post('http://localhost:41595/api/item/addFromPaths',
                      json={'items': items,
                            'folderId': eagle_folder['id']})
    response = r.json()
    if response['status'] != 'success':
        print('Error adding items to Eagle')
        exit(1)


#p = Path('.')
#today = datetime.now().strftime('%Y-%m-%d')
#today_folder = Path('./' + today)
#today_folder.exists() or today_folder.mkdir()
# for mp4 in p.glob('*.mp4'):
#    mp4.rename(today_folder / mp4.name)
# for jpg in p.glob('*.jpg'):
#    jpg.rename(today_folder / jpg.name)
# for jpeg in p.glob('*.jpeg'):
#    jpeg.rename(today_folder / jpeg.name)
# for png in p.glob('*.png'):
#    png.rename(today_folder / png.name)


def create_today_folder_on_eagle():
    r = requests.get('http://localhost:41595/api/folder/list')
    response = r.json()
    if response['status'] != 'success':
        print('Error getting folder list')
        exit(1)
    folders = response['data']
    today = datetime.today().strftime('%Y-%m-%d')
    parent_folder = None
    for folder in folders:
        if folder['name'] == 'ImageSorter Temp':
            parent_folder = folder
            break
    if parent_folder is None:
        r = requests.post('http://localhost:41595/api/folder/create',
                          json={'folderName': 'ImageSorter Temp'})
        response = r.json()
        if response['status'] != 'success':
            print(response)
            print('Error creating folder')
            exit(1)
        parent_folder = response['data']
    for child in parent_folder['children']:
        if child['name'] == today:
            return child
    r = requests.post('http://localhost:41595/api/folder/create',
                      json={'folderName': today, 'parent': parent_folder['id']})
    response = r.json()
    if response['status'] != 'success':
        print("Error creating today's folder")
        exit(1)
    return response['data']


def get_args():
    args = sys.argv[1:]
    default_settings = {
        'targets': './targets.txt',
        'extensions': './extensions.txt'
    }
    settings = {}
    skip = False
    for arg in args:
        if arg.startswith('--targets='):
            if 'targets' in settings:
                print('Duplicate targets argument')
                exit(1)
            settings['targets'] = '='.join(arg.split('=')[1:])
        elif arg.startswith('--extensions='):
            if 'extensions' in settings:
                print('Duplicate extensions argument')
                exit(1)
            settings['extensions'] = '='.join(arg.split('=')[1:])
        elif arg == '--targets':
            if 'targets' in settings:
                print('Duplicate targets argument')
                exit(1)
            settings['targets'] = args[args.index(arg) + 1]
            skip = True
        elif arg == '--extensions':
            if 'extensions' in settings:
                print('Duplicate extensions argument')
                exit(1)
            settings['extensions'] = args[args.index(arg) + 1]
            skip = True
        elif skip:
            skip = False
            continue
        elif arg == '--help':
            help(0)
        else:
            print('Unknown argument {}'.format(arg))
            help(1)
    for key in default_settings:
        if key not in settings:
            settings[key] = default_settings[key]
    return settings


def help(return_value=0):
    print('''Usage: python move.py [options]
Options:
    --targets=<path>    Path to file containing target directories
    --extensions=<path> Path to file containing target extensions
    --help              Display this help message''')
    exit(return_value)


def main():
    settings = get_args()
    target_dirs = load_target_dirs(settings['targets'])
    target_extensions = load_target_extensions(settings['extensions'])

    folder = create_today_folder_on_eagle()

    for target_dir in target_dirs:
        process_dir(target_dir, target_extensions, folder)


if __name__ == '__main__':
    main()
