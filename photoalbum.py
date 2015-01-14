# This file is part galatea_photoalbum module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.model import ModelSQL, ModelView, fields
from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.config import config
from datetime import datetime
from mimetypes import guess_type
import os
import hashlib

__all__ = ['GalateaPhotoAlbumPhoto', 'GalateaPhotoAlbumWebSite', 'GalateaPhotoAlbumComment']
IMAGE_TYPES = ['image/jpeg', 'image/png',  'image/gif']


class GalateaPhotoAlbumPhoto(ModelSQL, ModelView):
    "Galatea Photo"
    __name__ = 'galatea.photoalbum.photo'
    _rec_name = 'file_name'
    photo = fields.Function(fields.Binary('Photo', filename='file_name'), 'get_image',
        setter='set_image')
    photo_path = fields.Function(fields.Char('Photo Path'), 'get_photopath')
    file_name = fields.Char('File Name', required=True)
    photo_create_date = fields.DateTime('Create Date', readonly=True)
    photo_write_date = fields.DateTime('Write Date', readonly=True)
    user = fields.Many2One('galatea.user', 'User', required=True)
    description = fields.Text('Description', translate=True,
        help='You could write wiki markup to create html content. Formats text following '
        'the MediaWiki (http://meta.wikimedia.org/wiki/Help:Editing) syntax.')
    metadescription = fields.Char('Meta Description', translate=True, 
        help='Almost all search engines recommend it to be shorter ' \
        'than 155 characters of plain text')
    metakeywords = fields.Char('Meta Keywords',  translate=True,
        help='Separated by comma')
    metatitle = fields.Char('Meta Title',  translate=True)
    active = fields.Boolean('Active',
        help='Dissable to not show content photo.')
    visibility = fields.Selection([
            ('public','Public'),
            ('register','Register'),
            ('manager','Manager'),
            ], 'Visibility', required=True)
    websites = fields.Many2Many('galatea.photoalbum.photo-galatea.website', 
        'photo', 'website', 'Websites',
        help='Photo will be available in those websites')
    comment = fields.Boolean('Comment', help='Active comments.')
    comments = fields.One2Many('galatea.photoalbum.comment', 'photo', 'Comments')
    total_comments = fields.Function(fields.Integer("Total Comments"),
        'get_totalcomments')

    @staticmethod
    def default_active():
        return True

    @staticmethod
    def default_visibility():
        return 'public'

    @staticmethod
    def default_websites():
        Website = Pool().get('galatea.website')
        return [p.id for p in Website.search([('registration','=',True)])]

    @classmethod
    def default_user(cls):
        Website = Pool().get('galatea.website')
        websites = Website.search([('active', '=', True)], limit=1)
        if not websites:
            return None
        website, = websites
        if website.photoalbum_anonymous_user:
            return website.photoalbum_anonymous_user.id
        return None

    @staticmethod
    def default_comment():
        return True

    @staticmethod
    def _create_photoalbum_dir():
        db_name = Transaction().cursor.dbname
        directory = os.path.join(config.get('database', 'path'), db_name)
        if not os.path.isdir(directory):
            os.makedirs(directory, 0770)
        directory = os.path.join(directory, 'photoalbum')
        if not os.path.isdir(directory):
            os.makedirs(directory, 0770)

    @classmethod
    def __setup__(cls):
        super(GalateaPhotoAlbumPhoto, cls).__setup__()
        cls._order.insert(0, ('photo_create_date', 'DESC'))
        cls._error_messages.update({
            'copy_photos': ('You can not copy photos. Create new record.'),
            'delete_photos': ('You can not delete photos because you will get ' \
                'error 404 NOT Found. Dissable active field.'),
            'not_file_mime': ('Not know file mime "%(file_name)s"'),
            'not_file_mime_image': ('"%(file_name)s" file mime is not an image ' \
                '(jpg, png or gif)'),
            'image_size': ('"%(file_name)s" size is larger than "%(size)s"MB'),
            })
        cls._create_photoalbum_dir()

    @classmethod
    def create(cls, vlist):
        now = datetime.now()
        vlist = [x.copy() for x in vlist]
        for vals in vlist:
            vals['photo_create_date'] = now
        photos = super(GalateaPhotoAlbumPhoto, cls).create(vlist)
        return photos

    @classmethod
    def write(cls, *args):
        now = datetime.now()

        actions = iter(args)
        args = []
        for photos, values in zip(actions, actions):
            values = values.copy()
            values['photo_write_date'] = now
            args.extend((photos, values))
        return super(GalateaPhotoAlbumPhoto, cls).write(*args)

    @classmethod
    def copy(cls, teams, default=None):
        cls.raise_user_error('copy_teams')

    @classmethod
    def delete(cls, photos):
        cls.raise_user_error('delete_photos')

    def get_image(self, name):
        db_name = Transaction().cursor.dbname
        filename = self.file_name
        if not filename:
            return None
        filename = os.path.join(config.get('database', 'path'), db_name,
            'photoalbum', filename[0:2], filename[2:4], self.file_name)

        value = None
        try:
            with open(filename, 'rb') as file_p:
                value = buffer(file_p.read())
        except IOError:
            pass
        return value

    def get_photopath(self, name):
        filename = self.file_name
        if not filename:
            return None
        return '%s/%s/%s' % (filename[:2], filename[2:4], filename)

    def get_totalcomments(self, name):
        return len(self.comments)

    @classmethod
    def set_image(cls, photos, name, value):
        if value is None:
            return

        ConfigPhotoAlbum = Pool().get('galatea.photoalbum.configuration')
        config_photoalbum = ConfigPhotoAlbum(1)
        size = config_photoalbum.max_size or 1000000

        db_name = Transaction().cursor.dbname
        photodir = os.path.join(
            config.get('database', 'path'), db_name, 'photoalbum')

        for photo in photos:
            file_name = photo['file_name']
            
            file_mime, _ = guess_type(file_name)
            if not file_mime:
                cls.raise_user_error('not_file_mime', {
                        'file_name': file_name,
                        })
            if file_mime not in IMAGE_TYPES:
                cls.raise_user_error('not_file_mime_image', {
                        'file_name': file_name,
                        })
            if len(value) > size:
                cls.raise_user_error('image_size', {
                        'file_name': file_name,
                        'size': size/1000000,
                        })
    
            _, ext = file_mime.split('/')
            digest = '%s.%s' % (hashlib.md5(value).hexdigest(), ext)
            subdir1 = digest[0:2]
            subdir2 = digest[2:4]
            directory = os.path.join(photodir, subdir1, subdir2)
            filename = os.path.join(directory, digest)

            if not os.path.isdir(directory):
                os.makedirs(directory, 0770)
            with open(filename, 'wb') as file_p:
                file_p.write(value)

            cls.write([photo], {
                'file_name': digest,
                })


class GalateaPhotoAlbumWebSite(ModelSQL):
    'Galatea Photo - Website'
    __name__ = 'galatea.photoalbum.photo-galatea.website'
    _table = 'galatea_photoalbum_galatea_website'
    photo = fields.Many2One('galatea.photoalbum.photo', 'Photo', ondelete='CASCADE',
            select=True, required=True)
    website = fields.Many2One('galatea.website', 'Website', ondelete='RESTRICT',
            select=True, required=True)


class GalateaPhotoAlbumComment(ModelSQL, ModelView):
    "Galatea Photo Comment"
    __name__ = 'galatea.photoalbum.comment'
    photo = fields.Many2One('galatea.photoalbum.photo', 'Photo', required=True)
    user = fields.Many2One('galatea.user', 'User', required=True)
    description = fields.Text('Description', required=True,
        help='You could write wiki markup to create html content. Formats text following '
        'the MediaWiki (http://meta.wikimedia.org/wiki/Help:Editing) syntax.')
    active = fields.Boolean('Active',
        help='Dissable to not show content photo.')
    comment_create_date = fields.Function(fields.Char('Create Date'),
        'get_comment_create_date')

    @classmethod
    def __setup__(cls):
        super(GalateaPhotoAlbumComment, cls).__setup__()
        cls._order.insert(0, ('create_date', 'DESC'))
        cls._order.insert(1, ('id', 'DESC'))

    @staticmethod
    def default_active():
        return True

    @classmethod
    def default_user(cls):
        Website = Pool().get('galatea.website')
        websites = Website.search([('active', '=', True)], limit=1)
        if not websites:
            return None
        website, = websites
        if website.photoalbum_anonymous_user:
            return website.photoalbum_anonymous_user.id
        return None

    @classmethod
    def get_comment_create_date(cls, records, name):
        'Created domment date'
        res = {}
        DATE_FORMAT = '%s %s' % (Transaction().context['locale']['date'], '%H:%M:%S')
        for record in records:
            res[record.id] = record.create_date.strftime(DATE_FORMAT) or ''
        return res
