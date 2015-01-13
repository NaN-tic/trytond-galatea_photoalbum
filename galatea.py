# This file is part galatea_photoalbum module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import PoolMeta
from trytond.model import fields
from trytond.pyson import Eval

__all__ = ['GalateaWebSite']
__metaclass__ = PoolMeta


class GalateaWebSite:
    __name__ = "galatea.website"
    photoalbum_comment = fields.Boolean('Photo Album Comments',
        help='Active Photo Album comments.')
    photoalbum_anonymous = fields.Boolean('Photo Album Anonymous',
        help='Active user anonymous to publish comments.')
    photoalbum_anonymous_user = fields.Many2One('galatea.user', 'Photo Album Anonymous User',
        states={
            'required': Eval('photoalbum_anonymous', True),
        })