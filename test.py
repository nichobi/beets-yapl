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


class Yapl:   
    
    ## Write out the data from csv_to_yaml out to .yaml files
    def write_yapl(self, filename, data):
        #output_path = Path(self.config['yaml_output_path'].as_filename())
        output_path = Path("./test/csv_output/" + filename)
        
        with io.open(output_path, 'w', encoding='utf8') as outfile:
            yaml.dump(data, outfile, default_flow_style=False, allow_unicode=True)
    
    ## Take all csv files located at the input path and create yaml representations for them            
    def csv_to_yapl(self):
        #input_path = Path(self.config['csv_input_path'].as_filename())
        input_path = Path('./test/csv_input')
        
        csv_files = [f for f in os.listdir(input_path) if f.endswith('.csv')]
        for csv_file in csv_files:
            
            print(f"Parsing {csv_file}")
            with io.open(input_path / csv_file, 'r', encoding='utf8') as file:
                #print("This thing is awesome sauce: " + str(input_path / csv_file))
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
                
                
                
    def m3u_to_yapl (self):
        input_path = Path('./test/m3u_input')

        m3u_files = [f for f in os.listdir(input_path) if f.endswith('.m3u8')]
        for m3u_file in m3u_files:
            print(f"Parsing {m3u_file}")
            m3upath = str(Path(input_path) / Path(m3u_file)) 
            print(m3upath)
            playlist = m3u8.load(m3upath)
            print(playlist.files)
            segmentlist = playlist.segments
            print(segmentlist.__str__())
            print(segmentlist.uri)
            #for segment in segmentlist:
            #    print(segment.uri)
            #    print(segment.base_uri)

beans = Yapl
beans.csv_to_yapl(beans)
beans.m3u_to_yapl(beans)