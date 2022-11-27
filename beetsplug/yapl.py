from beets.plugins import BeetsPlugin
from beets.ui import Subcommand
import yaml

def write_m3u(path, playlist, items):
    with open(path, 'w') as f:
        f.write("#EXTM3U\n")
        if "name" in playlist:
            f.write(f"#PLAYLIST {playlist['name']}\n")
        for i in items:
            f.write(f"#EXTINF: {round(i.get('length'))}, {i.get('artist')} - {i.get('title')}\n")
            f.write(i.get('path').decode())
            f.write("\n")

def compile(lib, opts, args):
    with open(args[0], 'r') as file:
        playlist = yaml.safe_load(file)
        items = []
        for song in playlist['playlist']:
            query = [":".join([k, str(v)]) for k, v in song.items()]
            results = lib.items(query)
            match len(results):
                case 1: items.append(results[0])
                case 0: print(f"No results for query: {query}")
                case _: print(f"Multiple results for query: {query}")
            write_m3u(args[1], playlist, items)

compile_command = Subcommand('yapl', help='compile yapl playlists')
compile_command.func = compile

class Yapl(BeetsPlugin):
    def commands(self):
        return [compile_command]

