# This file is part galatea_photoalbum module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.model import ModelView, ModelSQL, ModelSingleton, fields

__all__ = ['GalateaPhotoAlbumConfiguration']


class GalateaPhotoAlbumConfiguration(ModelSingleton, ModelSQL, ModelView):
    'Galatea Photo Album Configuration'
    __name__ = 'galatea.photoalbum.configuration'
    max_size = fields.Integer('Max Size',
        help='Maxim Image Size (bites)')

    @staticmethod
    def default_max_size():
        return 1000000
