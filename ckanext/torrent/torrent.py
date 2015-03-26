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

log = logging.getLogger('ckanext')

class TorrentController(base.BaseController):
    def download(self, id):
        torrent_name = id + '.torrent'
        torrent_storage_path = config.get('ckan.torrent_storage_path','')
        if not torrent_storage_path:
            storage_path = config.get('ckan.storage_path','')
            storage_path = os.path.join(storage_path, 'resources')
            torrent_storage_path = os.path.join(storage_path, 'torrents')
        torrent_file_path = os.path.join(torrent_storage_path, torrent_name)
        
        file_size = os.path.getsize(torrent_file_path)
        headers = [('Content-Disposition', 'attachment; filename=\"' + torrent_name + '\"'),
               ('Content-Type', 'text/plain'),
               ('Content-Length', str(file_size))]

        from paste.fileapp import FileApp
        fapp = FileApp(torrent_file_path, headers=headers)
        return fapp(request.environ, self.start_response)