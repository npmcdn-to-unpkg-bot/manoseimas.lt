import datetime

from couchdbkit import ResourceNotFound
from couchdbkit import Server

from scrapy.conf import settings

_dbs = {}
_servers = {}


def get_db(item_name, cache=True):
    global _servers, _dbs
    if not cache or item_name not in _dbs:
        for item, server_name, db_name in settings['COUCHDB_DATABASES']:
            if item == item_name:
                if not cache or server_name not in _servers:
                    server = _servers[server_name] = Server(server_name)
                else:
                    server = _servers[server_name]
                _dbs[item_name] = server.get_or_create_db(db_name)
                break
    return _dbs[item_name]


class ManoseimasPipeline(object):
    def process_item(self, item, spider):
        if '_id' not in item or not item['_id']:
            raise Exception('Missing doc _id. Doc: %s' % item)

        item_name = item.__class__.__name__.lower()
        db = get_db(item_name)
        try:
            doc = db.get(item['_id'])
        except ResourceNotFound:
            doc = dict(item)

        doc['doc_type'] = item_name
        doc['updated'] = datetime.datetime.now().isoformat()

        doc = db.save_doc(doc)

        if '_attachments' in item:
            for attachment, content in item['_attachments']:
                db.put_attachment(doc, content, attachment)

        return item
