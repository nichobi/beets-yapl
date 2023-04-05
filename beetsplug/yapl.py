from beets.plugins import BeetsPlugin
from beets.ui import Subcommand
from os.path import relpath
import yaml
import os
from pathlib import Path
# csv imports
import io
import csv
import m3u8


class Yapl(BeetsPlugin):
    def commands(self):
        compile_command = Subcommand('yapl', help='compile yapl playlists')
        compile_command.func = self.compile
        #m3utoyapl_command = Subcommand('m3u2', help='convert m3u playlists to yapl')
        #m3utoyapl_command.func = self.m3u_to_yapl
        csvtoyapl_command = Subcommand('csv', help='convert csv to yapl')
        csvtoyapl_command.func = self.csv_to_yapl
        return [csvtoyaplcommand, compile_command]
        #return [csvtoyaplcommand, compile_command, m3utoyapl_command]

    def write_m3u(self, filename, playlist, items):
        print(f"Writing {filename}")
        relative = self.config['relative'].get(bool)
        output_path = Path(self.config['output_path'].as_filename())
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
        input_path = Path(self.config['input_path'].as_filename())

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
        output_path = Path(self.config['yaml_output_path'].as_filename())
        with io.open(output_path, 'w', encoding='utf8') as outfile:
            yaml.dump(data, outfile, default_flow_style=False, allow_unicode=True)
    
    ## Take all csv files located at the input path and create yaml representations for them            
    def csv_to_yapl(self, lib, opts, args):
        input_path = Path(self.config['csv_input_path'].as_filename())
        
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
                
                print(playlist_fields)
                
                for row in playlist:
                    #pprint.pprint(row)
                    tempdict = dict()
                    for field in playlist_fields:
                        lowerfield = field.lower()
                        if "path" not in lowerfield:
                            tempdict[lowerfield] = row[field]
                    
                    # Putting values into the temporary dictionary
                    #tempdict["filename"] = row["Filename"]
                    #tempdict["title"] = row["Title"]
                    #tempdict["artist"] = row["Artist"]
                    #tempdict["album"] = row["Album"]
                    
                    datalist.append(tempdict)
                
                print("Export path: " + str(output_file))
                data["tracks"] = datalist
                self.write_yapl(self, output_file, data)
        
    ## Take all m3u files located at the input path and create yaml representations for them                
    
    def m3u_to_yapl (self, lib, opts, args):
        input_path = Path(self.config['m3u_input_path'].as_filename())

        m3u_files = [f for f in os.listdir(input_path) if f.endswith('.m3u')]
        for m3u_file in m3u_files:
            
            print(f"Parsing {m3u_file}")
            playlist = m3u8.load(m3u_file)
            print(playlist.segments)
            #with io.open(input_path / m3u_file, 'r', encoding='utf8') as file:
             #   if (f.readline() = "#EXTM3U\n":
              #      for line in f:
               #         if 
                    
                
                
                output_name = Path(csv_file).stem
                output_file = output_name + ".yaml"
                # Defining the dictionary and list that will go inside the dictionary
                data = dict()
                datalist = list() 
                # Adding the high level parts of the dict thing
                data["name"] = output_name
                
                print(playlist.fieldnames)
                
                for row in playlist:
                    #pprint.pprint(row)
                    tempdict = dict()
                    
                    # Putting values into the temporary dictionary
                    tempdict["filename"] = row["Filename"]
                    tempdict["title"] = row["Title"]
                    tempdict["artist"] = row["Artist"]
                    tempdict["album"] = row["Album"]
                    
                    datalist.append(tempdict)
                
                print("Export path: " + str(output_file))
                data["tracks"] = datalist
                self.write_yaml(self, output_file, data)
