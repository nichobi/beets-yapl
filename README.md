beets-yapl
==================

beets plugin to parse a yaml playlist format and compile it into the near universally supported M3U format.

M3U playlists are inherently fragile, breaking at the slightest change in a file's path. This plugin utilises beetDreamers' queries to define playlists in a simple yaml format, where you can provide precisely the level of detail required to unambiguously find the song you're after.

A playlist can be written as:
```yaml
name: Christmas
tracks:
  # The library only contains one version of this song, so this is enough.
  - title: Christmas (Baby Please Come Home)
    artist: Darlene Love
  # The library contains multiple recordings of this track, so let's include
  # the year to get the right version.
  - artist: Withered Hand
    title: Real Snow
    year: 2013
  # Typing Japanese characters is finicky, so let's just use the track's
  # MusicBrainz ID
  - mb_trackid: dafff56a-f327-4de5-ab35-633c8863857f
```
which will be compiled into an M3U playlist looking something like:
```m3u
#EXTM3U
#PLAYLIST:Christmas
#EXTINF:166, Darlene Love - Christmas (Baby Please Come Home)
../Darlene Love/Non-Album/Christmas (Baby Please Come Home).flac
#EXTINF:202, Withered Hand - Real Snow
../Withered Hand/Non-Album/Real Snow.flac
#EXTINF:266, クレイジーケンバンド - クリスマスなんて、大嫌い!!なんちゃって
../クレイジーケンバンド/Non-Album/クリスマスなんて、大嫌い!!なんちゃって.m4a
```

Getting Started
---------------
Install the plugin. So far it is only published on the AUR as [beets-yapl-git](https://aur.archlinux.org/packages/beets-yapl-git). Pip installation will arrive once I've had time to look into publishing on PyPI.

[Enable the plugin](https://beets.readthedocs.io/en/latest/plugins/index.html#using-plugins) by adding it to your plugin option in the beets configuration and configure the plugin.
```yaml
plugins:
- ...
- yapl

yapl:
  input_path: /home/nichobi/Music/playlists/
  output_path: /home/nichobi/Music/playlists/
  relative: true
```

`input_path: path` decides what directory yapl will search for yaml files.  
`output_path: path` decides where to output the compiled m3u files. Can be the same as input_path.  
`relative: bool` controls whether to use absolute or relative filepaths in the outputted M3U files.

Once configured, run `beet yapl` to compile all the playlists. Warnings will be issued for any ambiguous or resultless queries and these tracks will be left out of the output.

```
$ beet yapl
Parsing christmas.yaml
Multiple results for query: ['artist:Withered Hand', 'title:Real Snow']
No results for query: ['artist:UNPOC', 'title:Icelandic Leopard Cat']
Writing christmas.m3u
```
