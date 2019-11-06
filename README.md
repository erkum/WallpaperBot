# WallpaperBot
The default setting will choose one random image from /r/wallpaper and /r/wallpapers and sets it as the desktop background.


## Supported Platforms
* Windows  
* Linux:
    * Gnome (Ubuntu)
    * Plasma (Kubuntu, KDE Neon)
    * Cinnamon (Linux Mint)


## Requirements:  
* Python 3  
  
### for Linux:
* python3-dbus
* python3-xlib

## Usage:
## Common Call:
<pre>
wpb.py -m -a
</pre>
### Output from wpb.py -h  

<pre>
usage: wpb.py [-h] [--destination DESTINATION] [--outputName OUTPUTNAME] [--subreddit SUBREDDIT] [--downloadOnly [DOWNLOADONLY]] [--minResolution MINRESOLUTION]
              [--considerAspectRatio [CONSIDERASPECTRATIO]] [--noSave [NOSAVE]] [--bing [BING]] [--useMonitorResolution [USEMONITORRESOLUTION]] [--fallback [FALLBACK]]
              [--downloadAll [DOWNLOADALL]] [--setRandomIfNoneFound [SETRANDOMIFNONEFOUND]]

Downloads a wallpaper either from Reddit (wallpaper,wallpapers), Bing or from given Reddit threads.

optional arguments:
  -h, --help            show this help message and exit
  --destination DESTINATION, -d DESTINATION
                        Destination directory (default: ~/Pictures/wpb/)
  --outputName OUTPUTNAME, -o OUTPUTNAME
                        Output filename (defaults to Reddit title)
  --subreddit SUBREDDIT, -s SUBREDDIT
                        Specify multiple subreddits. (example: "wpb.py -s wallpaper,wallpapers,memes") (Default: wallpaper,wallpapers)
  --downloadOnly [DOWNLOADONLY]
                        Set wallpaper?, (default: False)
  --minResolution MINRESOLUTION, -r MINRESOLUTION
                        Specify resolution (format is NxN, example: 1920x1080). Only works in Reddit mode.
  --considerAspectRatio [CONSIDERASPECTRATIO], -a [CONSIDERASPECTRATIO]
                        Filters the Reddit images by their aspect ratio. Only works in combination with "--minResolution" or "--useMonitorResolution". Only works in Reddit
                        mode.
  --noSave [NOSAVE]     Sets the wallpaper and deletes the file afterwards. (default: False)
  --bing [BING]         Uses the current Bing image instead of Reddit.
  --useMonitorResolution [USEMONITORRESOLUTION], -m [USEMONITORRESOLUTION]
                        Same as "--minResolution" but uses the resolution from the monitor. Only works in Reddit mode. Will overwrite --minResolution. (Default: False)
  --fallback [FALLBACK], -f [FALLBACK]
                        If "--subreddit" was used, this flag will use "wallpaper,wallpapers" as fallback.
  --downloadAll [DOWNLOADALL]
                        Downloads all found images from Reddit. Sets one random image as background.
  --setRandomIfNoneFound [SETRANDOMIFNONEFOUND]
                        Sets a random wallpaper from already downloaded images if no new images were found.

  </pre>
  
  # License
  GPL v3