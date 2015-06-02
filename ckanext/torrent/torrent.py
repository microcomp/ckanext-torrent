import logging
import os
import ckan.lib.base as base
import ckan.plugins.toolkit as tk
import ckan.model as model
from hurry.filesize import size
import ckan.logic as logic
from ckan.common import _, c, request, response
import ckan.lib.helpers as h
from pylons import config
import ckan.lib.base as base

log = logging.getLogger('ckanext')

class TorrentController(base.BaseController):
    def download(self, id):
        torrent_name = id + '.torrent.added'
        torrent_storage_path = config.get('ckan.torrent_storage_path','')
        if not torrent_storage_path:
            storage_path = config.get('ckan.storage_path','')
            storage_path = os.path.join(storage_path, 'resources')
            torrent_storage_path = os.path.join(storage_path, 'torrents')
        torrent_file_path = os.path.join(torrent_storage_path, torrent_name)
        if os.path.isfile(torrent_file_path):
            file_size = os.path.getsize(torrent_file_path)
            headers = [('Content-Disposition', 'attachment; filename=\"' + id+'.torrent' + '\"'),
                   ('Content-Type', 'text/plain'),
                   ('Content-Length', str(file_size))]
    
            from paste.fileapp import FileApp
            fapp = FileApp(torrent_file_path, headers=headers)
            return fapp(request.environ, self.start_response)
        else:
            base.abort(404, _('Resource not found'))