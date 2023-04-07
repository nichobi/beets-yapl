from beets.plugins import BeetsPlugin
from beets.ui import Subcommand
from os.path import relpath
import yaml
import os
from pathlib import Path
# csv imports
import io
import csv
import py_m3u
from tinytag import TinyTag

fieldstograb = ["album", "artist", "genre", "length", "filesize", "title", "track", "year"]

class Yapl(BeetsPlugin):
    
    def commands(self):
        compile_command = Subcommand('yapl', help='compile yapl playlists')
        compile_command.func = self.compile
        m3utoyapl_beet_command = Subcommand('m3ub', help='convert m3u playlists to yapl using metadata from the beets library')
        m3utoyapl_beet_command.func = self.m3u_to_yapl_beets
        m3utoyapl_mp3tag_command = Subcommand('m3ut', help='convert m3u playlists to yapl using metadata from the actual music files')
        m3utoyapl_mp3tag_command.func = self.m3u_to_yapl_mp3tag
        csvtoyapl_command = Subcommand('csv', help='convert csv to yapl')
        csvtoyapl_command.func = self.csv_to_yapl
        #return [csvtoyapl_command, compile_command]
        return [csvtoyapl_command, compile_command, m3utoyapl_beet_command, m3utoyapl_mp3tag_command]

    def write_m3u(self, filename, playlist, items):
        print(f"Writing {filename}")
        relative = self.config['relative'].get(bool)
        output_path = Path(self.config['m3u_path'].as_filename())
        output_file = output_path / filename
        with open(output_file, 'w') as f:
            f.write("#EXTM3U\n")
            if "name" in playlist:
                f.write(f"#PLAYLIST:{playlist['name']}\n")
            for i in items:
                f.write(f"#EXTINF:{round(i.get('length'))}, {i.get('artist')} - {i.get('title')}\n")
                path = i.get('path').decode()
                if relative:
                    path = relpath(path, output_path)
                f.write(path)
                f.write("\n")

    def compile(self, lib, opts, args):
        input_path = Path(self.config['yapl_path'].as_filename())

        yaml_files = [f for f in os.listdir(input_path) if f.endswith('.yaml') or f.endswith('.yapl')]
        for yaml_file in yaml_files:
            print(f"Parsing {yaml_file}")
            with open(input_path / yaml_file, 'r') as file:
                playlist = yaml.safe_load(file)
                items = []
                # Deprecated 'playlist' field
                if 'playlist' in playlist and not 'tracks' in playlist:
                    print("Deprecation warning: 'playlist' field in yapl file renamed to 'tracks'")
                    tracks = playlist['playlist']
                else:
                    tracks = playlist['tracks']
                for track in tracks:
                    query = [f"{k}:{str(v)}" for k, v in track.items()]
                    results = lib.items(query)
                    # Replaced match with if, for python <3.10
                    l = len(results)
                    if   l == 1: items.append(results[0])
                    elif l == 0: print(f"No results for query: {query}")
                    else       : print(f"Multiple results for query: {query}")
                output_file = Path(yaml_file).stem + ".m3u"
                self.write_m3u(output_file, playlist, items)
                
    ## Write out the data from csv_to_yaml out to .yaml files
    def write_yapl(self, filename, data):
        output_path = Path(self.config['yapl_path'].as_filename())
        output_file = output_path / filename
        print("Creating file: " + str(output_file))
        with io.open(output_file, 'w', encoding='utf8') as outfile:
            yaml.dump(data, outfile, default_flow_style=False, allow_unicode=True)
    
    ## Take all csv files located at the input path and create yaml representations for them            
    def csv_to_yapl(self, lib, opts, args):
        input_path = Path(self.config['csv_path'].as_filename())
        
        csv_files = [f for f in os.listdir(input_path) if f.endswith('.csv')]
        for csv_file in csv_files:
            
            print(f"Parsing {csv_file}")
            with io.open(input_path / csv_file, 'r', encoding='utf8') as file:
                playlist = csv.DictReader(file)
                playlist_fields = playlist.fieldnames
                output_name = Path(csv_file).stem
                output_file = output_name + ".yaml"
                # Defining the dictionary and list that will go inside the dictionary
                data = dict()
                datalist = list() 
                # Adding the high level parts of the dict thing
                data["name"] = output_name
                #print(playlist_fields)
                for row in playlist:
                    tempdict = dict()
                    for field in playlist_fields:
                        #print(str(type(row[field])))
                        if str(type(row[field])) == "<class 'str'>":
                            if not len(row[field]) == 0:
                                lowerfield = field.lower()
                                if lowerfield in fieldstograb:
                                    tempdict[lowerfield] = row[field]
                    
                    datalist.append(tempdict)
                
                print("Export path: " + str(output_file))
                data["tracks"] = datalist
                self.write_yapl(output_file, data)
        
    ## Take all m3u files located at the input path and create yaml representations for them                
    def get_m3u_paths (self, input_path):
        m3u_files = [f for f in os.listdir(input_path) if f.endswith('.m3u8')]
        paths_list = list()
        for m3u_file in m3u_files:
            fileinfo = dict()
            fileinfo["filename"] = Path(m3u_file).stem
            print(f"Parsing {m3u_file}")
            paths = list()
            parser = py_m3u.M3UParser()
            with io.open (input_path / m3u_file, 'r') as file:
                audiofiles = parser.load(file)
                for audiofile in audiofiles:
                    #print("Path = " + audiofile.source)
                    if not str(audiofile.source).endswith("#"):
                        paths.append(audiofile.source)
                fileinfo["paths"] = paths    
            paths_list.append(fileinfo)
        return paths_list
            
                    
                    
    def m3u_to_yapl_beets(self, lib, opts, args):
        input_path = Path(self.config['m3u_path'].as_filename())
        dataforyapl = dict()
        paths_list = self.get_m3u_paths(input_path)
        for file in paths_list:
            filename = file['filename']
            output_file = filename + ".yaml"
            paths = file['paths']
            songlist = list()
            foundsongs = []
            dataforyapl["name"] = filename
            # For each path in paths, see if it is present in the beets Library
            for path in paths:
                querystr = f'"path:{path}"'
                results = lib.items(querystr) 
                l = len(results)
                # If the path is present, add the song to the foundsongs list
                if   l == 1: 
                    foundsongs.append(results[0])
                    print(f"Results: {results}")  
                elif l == 0: print(f"No results for query: {querystr}")
                else       : print(f"Multiple results for query: {querystr}")
            # For each song in foundsongs, create a dict to store the metadata, grab the metadata in each field listed in fieldstograb, and add the dict with the metadata to the list of songdata dicts
            for song in foundsongs:
                songdata = dict()
                #fieldstograb = ["album", "artist", "genre", "length", "filesize", "title", "track", "year"]
                for grabfield in fieldstograb:
                    if not len(str(song.get(grabfield))) == 0:
                        songdata[grabfield] = song.get(grabfield)
                songlist.append(songdata)
            # Add songlist, which contains loads of songdata dicts, to dataforyapl, and then call the write_yapl function to create a yapl file
            dataforyapl["tracks"] = songlist
            self.write_yapl(output_file, dataforyapl)
                    
                
    def m3u_to_yapl_mp3tag(self, lib, opts, args):
        input_path = Path(self.config['m3u_path'].as_filename())
        dataforyapl = dict()
        paths_list = self.get_m3u_paths(input_path) 
        # For each file in paths_list, the filename and paths are grabbed
        for file in paths_list:
            failcount = 0
            filename = file['filename']
            output_file = filename + ".yaml"
            paths = file['paths']
            songlist = list()
            foundsongs = []
            dataforyapl["name"] = filename
            # For each path in paths, we are going to grab the metadata, and add the items into the 
            for path in paths:
                songdata = dict()
                try:
                    metadata = TinyTag.get(path)
                except:
                    print(f"No file found at the given path: {path}")
                    failcount = failcount + 1
                else:                    
                    #print(str(type(metadata)))
                    #print(metadata.album)
                    songdata["album"] = metadata.album
                    songdata["artist"] = metadata.artist
                    songdata["genre"] = metadata.genre
                    songdata["length"] = metadata.duration
                    songdata["filesize"] = metadata.filesize
                    songdata["title"] = metadata.title
                    songdata["track"] = metadata.track
                    songdata["year"] = metadata.year
                    #for grabfield in fieldstograb:
                        #if grabfield == "length":
                            #songdata[grabfield] = metadata.duration
                        #else:
                            #songdata[grabfield] = metadata.grabfield
                    songlist.append(songdata)
            dataforyapl["tracks"] = songlist
            print(f"Failcount for {filename}: {failcount}")
            self.write_yapl(output_file, dataforyapl)
                        
                
            