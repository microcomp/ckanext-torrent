from ckan.lib.celery_app import celery
import logging
import os
import subprocess
import ckan.plugins.toolkit as toolkit
from pylons import config
import uuid

log = logging.getLogger('ckanext')

def get_directory(storage_path, id):
    directory = os.path.join(storage_path, id[0:3], id[3:6])
    return directory

def get_path(storage_path, id):
    directory = get_directory(storage_path, id)
    filepath = os.path.join(directory, id[6:])
    return filepath

@celery.task(name = "torrent.create")
def create_torrent_file(resource_path, torrent_storage_path, payload_storage_path, resource_id, tracker_url):
    if not os.path.exists(torrent_storage_path):
        os.makedirs(torrent_storage_path)
    if not os.path.exists(payload_storage_path):
        os.makedirs(payload_storage_path)
    payload_id = resource_id[6:]
    resource_id += '.torrent'
    output_path = os.path.join(torrent_storage_path, resource_id)
    try:
        log.info('resource_path: %s', resource_path)
        log.info('payload_storage_path: %s', payload_storage_path)
        subprocess.check_call(["ln", "-s", resource_path, payload_storage_path])
        payload_storage_path = os.path.join(payload_storage_path, payload_id)
        log.info('payload_storage_path: %s', payload_storage_path)
        log.info('output_path: %s', output_path)
        log.info('tracker_url: %s', tracker_url)
        status = subprocess.check_call(["sudo", "-u", "transmission", "transmission-create", "-o", output_path, "-t", tracker_url, payload_storage_path])
        return status
    except subprocess.CalledProcessError as e:
        log.exception(e)
        return -1


def create_torrent_file_all():
    tracker_url = config.get('ckan.torrent_tracker_url', '')
    if not tracker_url:
        return None
    log.info('tracker_url: %s', tracker_url)
    storage_path = config.get('ckan.storage_path','')
    storage_path = os.path.join(storage_path, 'resources')
    torrent_storage_path = config.get('ckan.torrent_storage_path','')
    payload_storage_path = config.get('ckan.torrent_payload_storage_path', '')
    if not torrent_storage_path:
        torrent_storage_path = os.path.join(storage_path,'torrents')
    if not payload_storage_path:
        payload_storage_path = os.path.join(storage_path,'payload')
    result = toolkit.get_action('current_package_list_with_resources')(data_dict={})
    resource_counter = 0
    resource_upload_counter = 0
    resource_success_counter = 0
    for dataset in result:
        for resource in dataset['resources']:
            resource_counter+=1
            if resource['url_type'] == 'upload':
                resource_upload_counter +=1
                log.info('resource id: %s', resource['id'])
                resource_path = get_path(storage_path, resource['id'])
                status = create_torrent_file(resource_path, torrent_storage_path, payload_storage_path,resource['id'], tracker_url)
                if status==0:
                    resource_success_counter+=1            
    log.info('available resources: %d', resource_counter)
    log.info('available uploaded resources : %d', resource_upload_counter)
    log.info('torrents created : %d', resource_success_counter)