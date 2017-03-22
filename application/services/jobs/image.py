from PIL import Image, ImageOps
import urllib.request
from io import StringIO

import boto
from boto.s3.key import Key
from configs import settings
from application.cel import celery


@celery.task
def upload(space, path, image=None, url=None, async=True, make_thumbnails=True):

    conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
    bucket_name = space
    bucket = conn.get_bucket(bucket_name)
    k = Key(bucket)

    def make_thumb(image):
        im =  Image.open(image)
        for size in [(400, 400), (150, 150)]:
            output = StringIO()
            im2 = ImageOps.fit(im, size, Image.ANTIALIAS)
            im2.save(output, "JPEG")

            k.key = "thumbnails/%sx%s/%s"%(size[0], size[1], path)
            k.set_contents_from_string(output.getvalue())
            k.make_public()
            output.close()

    # save original img
    if image is None and url:
        fd = urllib.request.urlopen(url)
        image = StringIO(fd.read())

    else:
        image = StringIO(image)

    k.key = path
    k.set_contents_from_file(image)
    k.make_public()

    # make thumbnails
    if make_thumbnails:
        make_thumb(image)

    image.close()
    orig_url = "http://assets.maybi.cn/%s"%path
    return orig_url


@celery.task
def make_thumbnails(space, path, url, async=True):

    conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
    bucket_name = space
    bucket = conn.get_bucket(bucket_name)
    k = Key(bucket)

    # save original img
    fd = urllib.request.urlopen(url)
    image = StringIO(fd.read())

    im =  Image.open(image)
    for size in [(480, 480), (180, 180)]:
        output = StringIO()
        im2 = ImageOps.fit(im, size, Image.ANTIALIAS)
        im2.save(output, "JPEG")

        k.key = "post_thumbs/%sx%s/%s"%(size[0], size[1], path)
        k.set_contents_from_string(output.getvalue())
        k.make_public()
        output.close()


@celery.task
def save_avatar(space, path, url, save_original=False, async=True):

    conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
    bucket_name = space
    bucket = conn.get_bucket(bucket_name)
    k = Key(bucket)
    fd = urllib.request.urlopen(url)
    image = StringIO(fd.read())


    # save original img
    if save_original:
        k.key = path
        k.set_contents_from_file(image)
        k.make_public()

    im =  Image.open(image)
    for size in [(200, 200), (80, 80)]:
        output = StringIO()
        im2 = ImageOps.fit(im, size, Image.ANTIALIAS)
        im2.save(output, "JPEG")

        k.key = "avatar_thumbs/%sx%s/%s"%(size[0], size[1], path)
        k.set_contents_from_string(output.getvalue())
        k.make_public()
        output.close()
