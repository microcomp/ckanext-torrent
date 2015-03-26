from pylons import config
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import logging
from ckan import model
from subprocess import call
from ckan.lib.celery_app import celery
import uuid
import os

log = logging.getLogger('ckanext')

def get_directory(storage_path, id):
    directory = os.path.join(storage_path, id[0:3], id[3:6])
    return directory

def get_path(storage_path, id):
    directory = get_directory(storage_path, id)
    filepath = os.path.join(directory, id[6:])
    return filepath

class TorrentPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IDomainObjectModification, inherit=True)
    plugins.implements(plugins.IResourceUrlChange)
    plugins.implements(plugins.IRoutes, inherit=True)
        
    def before_map(self, map):
        map.connect('torrents_download','/torrents/download/{id}', action='download', controller='ckanext.torrent.torrent:TorrentController')
        return map
    
    def notify(self, entity, operation=None):
        log.warn("notify")
        self._notify(entity, operation)
    
    def notify_after_commit(self, entity, operation=None):
        log.warn("notify_after_commit")
        self._notify(entity, operation)
        
    def _notify(self, entity, operation):
        if not isinstance(entity, model.Resource):
            return
        log.debug('Notified of resource event: %s', entity.id)
        if operation:
            # Only interested in 'new resource' events, since that's what you
            # get when you change the URL field. Note that once this occurs, in tasks.py
            # it will update the resource with the new cache_url, that will cause a
            # 'change resource' notification, which we need to ignore here.
            if operation == model.DomainObjectOperation.new and entity.resource_type == 'upload':
                self._create_torrent_task(entity)
            else:
                log.debug('Ignoring resource event because operation is: %s', operation)
        else:
            # if operation is None, resource URL has been changed, as the
            # notify function in IResourceUrlChange only takes 1 parameter
            self._create_torrent_task(entity)
        
    def _create_torrent_task(self, resource):
        log.info("resource attrs: %s", dir(resource))
        log.info("resource id: %s", resource.id)
        storage_path = config.get('ckan.storage_path','')
        storage_path = os.path.join(storage_path, 'resources')
        resource_path = get_path(storage_path, resource.id)
        log.info('resource path %s', resource_path)
        torrent_storage_path = config.get('ckan.torrent_storage_path','')
        if not torrent_storage_path:
            torrent_storage_path = storage_path + '/torrents'
        celery.send_task("torrent.create", args=[resource_path, torrent_storage_path, resource.id], countdown=10, task_id=str(uuid.uuid4()))    