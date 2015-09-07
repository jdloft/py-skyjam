import sys
import os
import logging

from gmusicapi.clients import Musicmanager

logging.basicConfig(filename='dl.log', level=logging.DEBUG)


def fix(path):
    path = path.replace(':', "")
    path = path.replace('/', '_')
    # path.replace('/', "\u2215")

    return path


if os.path.exists('oauth.cred'):
    pass
else:
    Musicmanager.perform_oauth('oauth.cred', True)

manager = Musicmanager()

manager.login('oauth.cred')

rows, columns = [int(v) for v in os.popen('stty size', 'r').read().split()]

logging.info('starting download')
count = 0
for songs in manager.get_uploaded_songs(True):
    for song in songs:
        count = count + 1

        dartist = '%s/%s' % (os.path.expanduser("~/Music"), fix(song['album_artist'] or song['artist']))
        if not os.path.exists(dartist):
            os.mkdir(dartist)

        dalbum = '%s/%s' % (dartist, fix(song['album']))
        if not os.path.exists(dalbum):
            os.mkdir(dalbum)

        fsong = '%s/%02d %s.mp3' % (dalbum,
                                      song['track_number'],
                                      fix(song['title']))

        sys.stdout.write('\r' + (' ' * (columns-1)) + '\r')
        sys.stdout.write(("%05d %s" % (count, fsong))[0:columns-1])
        sys.stdout.flush()
        if not os.path.exists(fsong):
            audio = None
            try:
                filename, audio = manager.download_song(song['id'])
                logging.info('download success: "%s"' % fsong)
            except KeyboardInterrupt:
                sys.stdout.write('\n')
                sys.exit(1)  # move this up
            except Exception, e:
                logging.error('download failed: "%s" %s' % (fsong, e))
            else:
                with open(fsong, 'wb') as f:
                    f.write(audio)
        else:
            logging.info('download skipped: "%s"' % fsong)

sys.stdout.write('\n')
