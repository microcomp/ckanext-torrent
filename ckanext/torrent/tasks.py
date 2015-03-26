from ckan.lib.celery_app import celery
import logging
import os
import subprocess
import ckan.plugins.toolkit as toolkit
from pylons import config

log = logging.getLogger('ckanext')

def get_directory(storage_path, id):
    directory = os.path.join(storage_path, id[0:3], id[3:6])
    return directory

def get_path(storage_path, id):
    directory = get_directory(storage_path, id)
    filepath = os.path.join(directory, id[6:])
    return filepath

@celery.task(name = "torrent.create")
def create_torrent_file(resource_path, torrent_storage_path, resource_id):
    if not os.path.exists(torrent_storage_path):
        os.makedirs(torrent_storage_path)
    resource_id += '.torrent'
    output_path = os.path.join(torrent_storage_path, resource_id)
    #with open(output_path, 'w') as fout:
    #    fout.write('test')
    response = subprocess.check_call(["transmission-create", "-o", output_path, resource_path])
    log.info(response)
    #response = subprocess.check_call(["touch", output_path,])
    #log.info(response)
    return 1

def create_torrent_file_all():
    storage_path = config.get('ckan.storage_path','')
    storage_path = os.path.join(storage_path, 'resources')
    torrent_storage_path = config.get('ckan.torrent_storage_path','')
    if not torrent_storage_path:
        torrent_storage_path = storage_path + '/torrents'
    result = toolkit.get_action('current_package_list_with_resources')(data_dict={})
    #log.info('packages with resources: %s', result)
    resource_counter = 0
    resource_upload_counter = 0
    for dataset in result:
        for resource in dataset['resources']:
            resource_counter+=1
            if resource['url_type'] == 'upload':
                resource_upload_counter +=1
                log.info('resource id: %s', resource['id'])
                resource_path = get_path(storage_path, resource['id'])
                create_torrent_file(resource_path, torrent_storage_path, resource['id'])
                
    log.info('available resources: %d', resource_counter)
    log.info('available resources uploaded: %d', resource_upload_counter)