# This file is part galatea_photoalbum module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool
from .photoalbum import *
from .galatea import *
from .configuration import *

def register():
    Pool.register(
        GalateaPhotoAlbumPhoto,
        GalateaPhotoAlbumWebSite,
        GalateaPhotoAlbumComment,
        GalateaWebSite,
        GalateaPhotoAlbumConfiguration,
        module='galatea_photoalbum', type_='model')
