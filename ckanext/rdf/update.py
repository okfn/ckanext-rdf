import logging
from urlparse import urljoin
from itertools import count
from urllib import urlopen, quote_plus

from ckan.model import DomainObjectOperation, Package
from ckan.plugins import SingletonPlugin, implements
from ckan.plugins import IConfigurable, IDomainObjectModification

from produce import pkg_produce

log = logging.getLogger(__name__)

class StoreUpdatePlugin(SingletonPlugin):

    implements(IDomainObjectModification, inherit=True)
    implements(IConfigurable, inherit=True)
    
    def configure(self, config):
        self._store_url = config.get('rdf.store_url')

    def update(self, update_message):
        #log.debug("Query: %s" % update_message)
        if self._store_url is None:
            log.warn("No 'rdf.store_url' is given in config, cannot update triple store.")
            return
        url = urljoin(self._store_url, '/update/')
        data = 'update=' + quote_plus(update_message)
        fh = urlopen(url, data=data)
        log.debug("Response: %s" % fh.read())
        fh.close()

    def delete_triples(self, graph):
        subjects = []
        for i, s in zip(count(), set(graph.subjects())):
            subjects.append("<%s> ?c%sa ?c%sb" % (s, i, i))
        return " . \n".join(subjects)

    def update_package(self, package, operation):
        graph = pkg_produce(package)
        # TODO: this is not a proper update
        insert = graph.serialize(format="nt")
        delete = self.delete_triples(graph)
        if operation == DomainObjectOperation.new:
            self.update("INSERT DATA { %s }" % insert)
        elif operation == DomainObjectOperation.changed:
            self.update("DELETE DATA { %s }" % delete)
            self.update("INSERT DATA { %s }" % insert)
            #q = "MODIFY DELETE { %s } INSERT { %s }" % (delete, insert)
        elif operation == DomainObjectOperation.deleted:
            self.update("DELETE DATA { %s }" % delete)
        #log.debug("SPARQL Update: %s" % q)

    def notify(self, entity, operation):
        if isinstance(entity, Package):
            self.update_package(entity, operation)


