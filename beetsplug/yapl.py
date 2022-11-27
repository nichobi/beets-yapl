from beets.plugins import BeetsPlugin
from beets.ui import Subcommand
from os.path import relpath
import yaml
import os
from pathlib import Path

class Yapl(BeetsPlugin):
    def commands(self):
        compile_command = Subcommand('yapl', help='compile yapl playlists')
        compile_command.func = self.compile
        return [compile_command]

    def write_m3u(self, filename, playlist, items):
        relative = self.config['relative'].get(bool)
        output_path = Path(self.config['output_path'].as_filename())
        output_file = output_path / filename
        with open(output_file, 'w') as f:
            f.write("#EXTM3U\n")
            if "name" in playlist:
                f.write(f"#PLAYLIST {playlist['name']}\n")
            for i in items:
                f.write(f"#EXTINF: {round(i.get('length'))}, {i.get('artist')} - {i.get('title')}\n")
                path = i.get('path').decode()
                if relative:
                    path = relpath(path, output_path)
                f.write(path)
                f.write("\n")

    def compile(self, lib, opts, args):
        input_path = Path(self.config['input_path'].as_filename())

        yaml_files = [f for f in os.listdir(input_path) if f.endswith('.yaml') or f.endswith('.yapl')]
        for yaml_file in yaml_files:
            with open(input_path / yaml_file, 'r') as file:
                playlist = yaml.safe_load(file)
                items = []
                for song in playlist['playlist']:
                    query = [":".join([k, str(v)]) for k, v in song.items()]
                    results = lib.items(query)
                    match len(results):
                        case 1: items.append(results[0])
                        case 0: print(f"No results for query: {query}")
                        case _: print(f"Multiple results for query: {query}")
                output_file = Path(yaml_file).stem + ".m3u"
                self.write_m3u(output_file, playlist, items)

