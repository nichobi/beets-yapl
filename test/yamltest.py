import os
import io
import yaml
from pathlib import Path

total_count = 0
yaml_files = [f for f in os.listdir("E:\Captures\Audio Files\Music\playlists\playliststosave\testing\yapl") if f.endswith('.yaml') or f.endswith('.yapl')]
for yaml_file in yaml_files:
    print(f"Parsing {yaml_file}")
    with open(input_path / yaml_file, 'r') as file:
        count = 0
        playlist = yaml.safe_load(file)
        tracks = playlist["tracks"]
        for track in tracks:
            if "/" in track['track']:
                print("There is a thing")
                count = count + 1
        total_count = total_count + count
        print(f"Total count of {yaml_file}: {count}")           
print(f"Total count: {total_count}")