from ckan.lib.cli import CkanCommand
import sys
import logging
log = logging.getLogger('ckanext')
log.setLevel(logging.DEBUG)

class TorrentCmd(CkanCommand):
    """Creates torrent file of every resource
        Usage:
        torrent-cmd createAll
        - creates torrents 
    """
    
    summary = __doc__.split('\n')[0]
    usage = __doc__
    #max_args = 3
    #min_args = 0
    
    def __init__(self, name):
        super(TorrentCmd, self).__init__(name)
    def command(self):
        self._load_config()
        import tasks
        
        if len(self.args) == 0:
            self.parser.print_usage()
            sys.exit(1)
        cmd = self.args[0]
        if cmd == 'createAll':
            log.info('Starting creating torrents')
            tasks.create_torrent_file_all()
            