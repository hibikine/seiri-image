from pathlib import Path
from datetime import datetime
p = Path('.')
today = datetime.now().strftime('%Y-%m-%d')
today_folder = Path('./' + today)
today_folder.exists() or today_folder.mkdir()
for mp4 in p.glob('*.mp4'):
    mp4.rename(today_folder / mp4.name)
for jpg in p.glob('*.jpg'):
    jpg.rename(today_folder / jpg.name)
for jpeg in p.glob('*.jpeg'):
    jpeg.rename(today_folder / jpeg.name)
for png in p.glob('*.png'):
    png.rename(today_folder / png.name)
