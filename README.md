beets-yapl
==================

beets plugin to parse a yaml playlist format and compile it into the near universally supported M3U format.

M3U playlists are inherently fragile, breaking at the slightest change in a file's path. This plugin utilises beets' queries to define playlists in a simple yaml format, where you can provide precisely the level of detail required to unambiguously find the song you're after.

A playlist can be written as:
```yaml
name: Christmas
tracks:
  - artist: Withered Hand
    title: Real Snow
    singleton: true
  - artist: Withered Hand
    title: It's a Wonderful Life
    album: Chrimble madness
  - artist: U.N.P.O.C.
    title: Icelandic Leopard Cat
```
which will be compiled into an m3u playlist looking something like:
```m3u
#EXTM3U
#PLAYLIST:Christmas
#EXTINF:202, Withered Hand - Real Snow
../Withered Hand/Non-Album/Real Snow.flac
#EXTINF:350, Withered Hand - It's a Wonderful Life
../Withered Hand/Non-Album/It's a Wonderful Life.mp3
#EXTINF:180, U.N.P.O.C. - The Icelandic Leopard Cat
../Fence Collective, The/0000 - Little Wonkey (FZ4)/02 The Icelandic Leopard Cat.mp3
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
