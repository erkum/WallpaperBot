from sys import platform
import sys
import fractions
from urllib.error import HTTPError
from pathlib import Path
import urllib.request
import random
import json
import os
import argparse
import time
import re
from glob import glob


if platform == "linux" or platform == "linux2":
    import dbus
    from Xlib.display import Display
    d = Display()
    monitor_resolution = (int(d.screen()['width_in_pixels']), d.screen()['height_in_pixels'])

elif platform == "darwin":
    sys.exit('Mac is not supported.')

elif platform == "win32":
    import ctypes
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
    monitor_resolution = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)


DATA_DIR = str(Path.home()).replace('\\', '/') + '/Pictures/wpb/'
SUBREDDITS = 'wallpaper,wallpapers'
BING_URL = 'https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1'
MAX_ATTEMPTS = 5
SLEEP_SECONDS_AFTER_ATTEMPT = 2
RES_RE = re.compile('\d{3,5}x\d{3,5}')


def makeFilenameValid(name):
    name = name.replace('<', '')
    name = name.replace("'", "")
    name = name.replace('>', '')
    name = name.replace(':', '')
    name = name.replace('"', '')
    name = name.replace('/', '')
    name = name.replace('\\', '')
    name = name.replace('|', '')
    name = name.replace('?', '')
    name = name.replace('*', 'x')
    name = name.replace('\n', '')
    name = name.replace('\r', '')
    return name


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def openJSON(url):
    i = 0
    while True:

        if i >= MAX_ATTEMPTS:
            print('Max. attempts reached.')
            return None
        try:
            with urllib.request.urlopen(url) as url:
                data = json.loads(url.read().decode('utf-8'))
            return data

        except HTTPError as e:
            # Too many requests, give reddit a break, try again.
            print("JSON api throttled, attempt %s on %s" % (i, MAX_ATTEMPTS))
            if getattr(e, 'code', None) == 429:
                time.sleep(SLEEP_SECONDS_AFTER_ATTEMPT)
            if getattr(e, 'code', None) == 404:
                eprint(e.__str__())
                sys.exit(1)
            i += 1
        except Exception:
            print("Timeout, attempt %s of %s" % (i, MAX_ATTEMPTS))
            time.sleep(SLEEP_SECONDS_AFTER_ATTEMPT)
            i += 1


def getImageUrlReddit(subreddit_list, dest, desired_res=None, aspect_ratio=None):
    candidates = []
    downoadedImageList = glob(dest + '*')
    for subreddit in subreddit_list:
        url = 'http://www.reddit.com/r/' + subreddit + '/top.json?t=week&limit=100'
        print('Looking for pictures in /r/%s.' % subreddit)
        data = openJSON(url)
        for item in data['data']['children']:

            # check if the file was already downloaded
            if any(item['data']['id'] in s for s in downoadedImageList):
                print('"' + item['data']['title'] + '_' + item['data']['id'] + os.path.splitext(item['data']['url'])[1] + '" was already downloaded.')
                continue

            try:
                if desired_res:
                    img_x = item['data']['preview']['images'][0]['source']['width']
                    img_y = item['data']['preview']['images'][0]['source']['height']
                    desired_res_x = int(desired_res[0])
                    desired_res_y = int(desired_res[1])

                    if aspect_ratio:
                        img_aspect_ratio = fractions.Fraction(img_x, img_y)
                        desired_aspect_ratio = fractions.Fraction(desired_res_x, desired_res_y)

                        if img_x >= desired_res_x and img_y >= desired_res_y \
                                and img_aspect_ratio == desired_aspect_ratio:
                            candidates.append((item['data']['url'],
                                              item['data']['title'] + '_' + item['data']['id'] + os.path.splitext(item['data']['url'])[1]))
                    else:
                        if img_x >= desired_res_x and img_y >= desired_res_y:
                            candidates.append((item['data']['url'],
                                               item['data']['title'] + '_' + item['data']['id'] +
                                               os.path.splitext(item['data']['url'])[1]))
                else:
                    candidates.append((item['data']['url'],
                                       item['data']['title'] + '_' + item['data']['id'] +
                                       os.path.splitext(item['data']['url'])[1]))
            except KeyError:
                print('Post does not contain an image. Skipping...')

    return candidates


def getImageUrlBing(url):
    data = openJSON(url)

    imgUrl = 'https://www.bing.com' + data['images'][0]['url']
    filename = imgUrl[imgUrl.find('id=') + 3:]

    if filename.find('&') >= 0:
        filename = filename[:filename.find('&')]

    return [(imgUrl, filename)]


def downloadImage(dest, candidate):
    url = candidate[0]
    filename = makeFilenameValid(candidate[1])
    print('Downloading "%s"...' % filename)
    dest += filename

    if os.path.exists(dest):
        return dest
    i = 0
    while True:
        if i == MAX_ATTEMPTS:
            raise Exception('Max. retries reached.')
        try:
            urllib.request.urlretrieve(url, dest)
            return dest
        except Exception as e:
            print('Something happend. ' + e.__str__())
            time.sleep(SLEEP_SECONDS_AFTER_ATTEMPT)
            i += 1


def setBackgroundWin(path):
    return ctypes.windll.user32.SystemParametersInfoW(20, 0, path, 1)


def setBackgroundPlasma(path, plugin='org.kde.image'):
    jscript = """
    var allDesktops = desktops();
    print (allDesktops);
    for (i=0;i<allDesktops.length;i++) {
        d = allDesktops[i];
        d.wallpaperPlugin = "%s";
        d.currentConfigGroup = Array("Wallpaper", "%s", "General");
        d.writeConfig("Image", "file://%s")
    }
    """
    bus = dbus.SessionBus()
    plasma = dbus.Interface(bus.get_object('org.kde.plasmashell', '/PlasmaShell'), dbus_interface='org.kde.PlasmaShell')
    plasma.evaluateScript(jscript % (plugin, plugin, path))


def setBackgroundGnome(path, plugin):
    return os.system("gsettings set %s picture-uri file://'%s'" % (plugin, path))


def setBackground(dl_img):
    if platform == "linux" or platform == "linux2":
        desktop = os.environ.get('DESKTOP_SESSION')
        if desktop in ('plasma', '/usr/share/xsessions/plasma'):
            return setBackgroundPlasma(dl_img)
        elif desktop in ('ubuntu'):
            return setBackgroundGnome(dl_img, 'org.gnome.desktop.background')
        elif desktop in ('cinnamon'):
            return setBackgroundGnome(dl_img, 'org.cinnamon.desktop.background')
        else:
            print('Your Linux desktop environment %s is not supported.' % desktop)
            sys.exit(0)
    elif platform == "darwin":
        sys.exit(0)
    elif platform == "win32":
        return setBackgroundWin(dl_img)


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def getArgs():
    parser = argparse.ArgumentParser(
        description='Downloads a wallpaper either from Reddit (' + str(SUBREDDITS) + '), Bing or from given Reddit threads.'
    )

    parser.add_argument(
        '--destination',
        '-d',
        type=str,
        default=DATA_DIR,
        help='Destination directory (default: %s)' % DATA_DIR
    )


    parser.add_argument(
        '--outputName',
        '-o',
        type=str,
        default=None,
        help='Output filename (defaults to Reddit title)',
    )

    parser.add_argument(
        '--subreddit',
        '-s',
        type=str,
        default=SUBREDDITS,
        help='Specify multiple subreddits. (example: "wpb.py -s wallpaper,wallpapers,memes") (Default: %s)' % str(SUBREDDITS),
    )

    parser.add_argument(
        '--downloadOnly',
        type=str2bool,
        nargs='?',
        const=True,
        default=False,
        help='Set wallpaper?, (default: False)'
    )

    parser.add_argument(
        '--minResolution',
        '-r',
        type=str,
        default='None',
        help='Specify resolution (format is NxN, example: 1920x1080). Only works in Reddit mode.'
    )

    parser.add_argument(
        '--considerAspectRatio',
        '-a',
        type=str2bool,
        nargs='?',
        const=True,
        default=False,
        help=('Filters the Reddit images by their aspect ratio. Only works in combination with '
              '"--minResolution" or "--useMonitorResolution". Only works in Reddit mode.')
    )

    parser.add_argument(
        '--noSave',
        type=str2bool,
        nargs='?',
        const=True,
        default=False,
        help='Sets the wallpaper and deletes the file afterwards. (default: False)'
    )

    parser.add_argument(
        '--bing',
        type=str2bool,
        nargs='?',
        const=True,
        default=False,
        help='Uses the current Bing image instead of Reddit.'
    )

    parser.add_argument(
        '--useMonitorResolution',
        '-m',
        type=str2bool,
        nargs='?',
        const=True,
        default=False,
        help=('Same as "--minResolution" but uses the resolution from the monitor. Only works in Reddit mode. '
              'Will overwrite --minResolution. (Default: False)')
    )

    parser.add_argument(
        '--fallback',
        '-f',
        type=str2bool,
        nargs='?',
        const=True,
        default=False,
        help='If "--subreddit" was used, this flag will use "' + str(SUBREDDITS) + '" as fallback.'
    )

    parser.add_argument(
        '--downloadAll',
        type=str2bool,
        nargs='?',
        const=True,
        default=False,
        help='Downloads all found images from Reddit. Sets one random image as background.'
    )

    parser.add_argument(
        '--setRandomIfNoneFound',
        type=str2bool,
        nargs='?',
        const=True,
        default=False,
        help='Sets a random wallpaper from already downloaded images if no new images were found.'
    )

    return parser.parse_args()


def __main__():
    args = getArgs()

    args.destination = os.path.normpath(args.destination) + '/'

    if not os.path.exists(args.destination):
        os.makedirs(args.destination)

    if not os.path.exists(args.destination):
        raise Exception(
            ('Destination directory %s does not exist, or is '
             'unreadable') % args.destination)

    if args.minResolution == 'None':
        desired_res = None
    elif RES_RE.match(args.minResolution):
        desired_res = args.minResolution.split('x')
    else:
        eprint("Error: Bad resolution, or resolution too big (or small)\n")
        sys.exit(1)

    if args.bing:
        candidates = getImageUrlBing(BING_URL)
    else:
        if args.useMonitorResolution:
            desired_res = monitor_resolution
        candidates = getImageUrlReddit(str(args.subreddit).split(','), args.destination, desired_res, args.considerAspectRatio)

    noDl = False
    if len(candidates) == 0:
        noDl = True
        if args.fallback and args.subreddit:
            print("No images were found... Using fallback.")
            candidates = getImageUrlReddit(SUBREDDITS.split(','), args.destination, desired_res, args.considerAspectRatio)
        if len(candidates) == 0:
            if args.setRandomIfNoneFound:
                print("No new images were found. Setting random from already downloaded images.")
                downoadedImageList = glob(args.destination + '*')
                dl_img = downoadedImageList[random.randrange(0, len(downoadedImageList))]
            else:
                eprint('No images found mathing your settings.')
                sys.exit(0)
        else:
            noDl = False

    if not noDl:
        if args.downloadAll and not args.bing:
            dl_candidates = []
            for candidate in candidates:
                dl_candidates.append(downloadImage(args.destination, candidate))
            dl_img = dl_candidates[random.randrange(0, len(dl_candidates))]
        else:
            candidate = candidates[random.randrange(0, len(candidates))]
            if args.outputName:
                candidate = (candidate[0], makeFilenameValid(args.outputName))
            dl_img = downloadImage(args.destination, candidate)

    if not args.downloadOnly:
        setBackground(dl_img)

    if args.noSave:
        time.sleep(1)
        os.remove(dl_img)

    sys.exit(1)


if __name__ == '__main__':
    __main__()
