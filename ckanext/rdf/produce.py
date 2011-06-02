import logging
from urllib import quote

from pprint import pformat

from vocab import Graph, URIRef, Literal, BNode
from vocab import DC, DCAT, FOAF, OWL, RDF, RDFS, UUID, VOID, OPMV, SKOS, REV, SCOVO, XSD, LICENSES

from util import parse_date

log = logging.getLogger(__name__)

def pkg_produce(pkg):
    return dict_produce(pkg.as_dict())

def dict_produce(data):
    uri = data['ckan_url'] if 'ckan_url' in data else BNode()
    rec = Graph(identifier=uri)
    rec.remove((None, None, None))

    rec.add((uri, RDF.type, DCAT.Dataset))
    rec.add((uri, OWL.sameAs, UUID[data["id"]]))
    rec.add((uri, DC.identifier, Literal(data["name"])))

    if data["url"] is not None and data["url"].strip():
        rec.add((uri, FOAF.homepage, URIRef(data["url"].strip())))

    if data["title"] is not None:
        rec.add((uri, RDFS.label, Literal(data["title"])))
        rec.add((uri, DC.title, Literal(data["title"])))
    else:
        rec.add((uri, RDFS.label, Literal(data["name"])))

    if data["notes"] is not None:
        rec.add((uri, DC["description"], Literal(data["notes"])))

    if data["license_id"] is not None:
        rec.add((uri, DC["rights"], LICENSES[data["license_id"]]))

    author = BNode()
    if data["author"] or data["author_email"]:
        rec.add((uri,DC.creator, author))
    if data["author"]:
        rec.add((author,FOAF.name, Literal(data["author"])))
    if data["author_email"]:
        rec.add((author,FOAF.mbox, URIRef("mailto:" + data["author_email"])))

    maintainer = BNode()
    if data["maintainer"] or data["maintainer_email"]:
        rec.add((uri,DC.contributor, maintainer))
    if data["maintainer"]:
        rec.add((maintainer,FOAF.name, Literal(data["maintainer"])))
    if data["maintainer_email"]:
        rec.add((maintainer,FOAF.mbox, URIRef("mailto:" + data["maintainer_email"])))

    for tag in data["tags"]:
        rec.add((uri, DCAT.keyword, Literal(tag)))

    if "ratings_average" in data and data["ratings_average"] is not None:
        rec.add((uri,REV.rating,
                 Literal(data["ratings_average"], datatype=XSD.float)))

    for rdata in data["resources"]:
        _process_resource(rec, uri, rdata)

    for k,v in data["extras"].items():
        _process_extra(rec, uri, k, v)

    for rdata in data["relationships"]:
        _process_relationship(rec, uri, rdata)

    ## TODO handle groups and version
    return rec

def _process_resource(rec, uri, rdata):
    if rdata["format"] == "api/sparql":
        ## RDF datasets with SPARQL endpoints are marked so by LOD
        rec.add((uri, RDF["type"], VOID["Dataset"]))
        rec.add((uri, VOID["sparqlEndpoint"], URIRef(rdata["url"])))
    elif rdata["format"] == "meta/rdf-schema":
        rec.add((uri, RDF["type"], VOID["Dataset"]))
        rec.add((uri, VOID["vocabulary"], URIRef("http://www.w3.org/2000/01/rdf-schema#")))
    elif rdata["format"] == "meta/void":
        rec.add((uri, RDF["type"], VOID["Dataset"]))
        rec.add((uri, VOID["vocabulary"], VOID[""]))
    elif rdata["format"] == "meta/owl":
        rec.add((uri, RDF["type"], VOID["Dataset"]))
        rec.add((uri, VOID["vocabulary"], OWL[""]))
    elif rdata["format"] in ("application/x-ntriples", "application/x-nquads", "application/rdf+xml", "text/n3", "text/turtle"):
        rec.add((uri, RDF["type"], VOID["Dataset"]))
        dump = URIRef(rdata["url"])
        rec.add((uri, VOID["dataDump"], dump))
        format = _format(rdata["format"])
        rec.add((dump, DC["format"], format.identifier))
        rec += format
    elif rdata["format"] in ("example/rdf+xml", "example/n3", "example/ntriples", "example/turtle", "example/rdfa"):
        if rdata["url"]:
            example = URIRef(rdata["url"])
            rec.add((uri, VOID["exampleResource"], example))
            format = _format(rdata["format"])
            rec.add((example, DC["format"], format.identifier))
            rec += format
            if rdata["description"]:
                rec.add((example, RDFS["label"], Literal(rdata["description"])))
    else:
        resource = BNode()
        rec.add((uri, DCAT["distribution"], resource))
        rec.add((resource, RDF["type"], DCAT["Distribution"]))
        if rdata["url"]:
            rec.add((resource, DCAT["accessURL"], URIRef(rdata["url"])))
        if rdata["format"]:
            format = _format(rdata["format"])
            rec.add((resource, DC["format"], format.identifier))
            rec += format
        if rdata["description"]:
            rec.add((resource, RDFS["label"], Literal(rdata["description"])))

def _format(format):
    g = Graph()
    g.add((g.identifier, RDF.type, DC.IMT))
    g.add((g.identifier, RDF.value, Literal(format)))
    g.add((g.identifier, RDFS.label, Literal(format)))
    return g

def _process_extra(rec, uri, key, value):
    if isinstance(value, basestring):
        value = value.strip()
        lval = value.lower()
        if "unknown" in lval or "not specified" in lval:
            value = None
    if value is None or value == '':
            return

    if key.startswith("links:"):
        _process_linkset(rec, uri, key, value)
    elif key == "triples":
        rec.add((uri, RDF["type"], VOID["Dataset"]))
        rec.add((uri, VOID["triples"], Literal(int(value)))) 
    elif key == "shortname":
        rec.add((uri, RDFS["label"], Literal(value)))
    elif key == "license_link":
        rec.add((uri, DC["rights"], URIRef(value)))
    elif key == "date_created":
        rec.add((uri, DC["created"], Literal(value)))
    elif key == "date_published":
        rec.add((uri, DC["available"], Literal(value)))
    elif key == "date_listed":
        rec.add((uri, DC["available"], Literal(value)))
    elif key == "update_frequency":
        freq = BNode()
        rec.add((uri, DC["accrualPeriodicity"], freq))
        rec.add((freq, RDF["value"], Literal(value)))
        rec.add((freq, RDFS["label"], Literal(value)))
    elif key == "unique_id":
        rec.add((uri, DC["identifier"], Literal(value)))
    elif key in ("geospatial_coverage", "geographic_coverage", "geographical_coverage"):
        rec.add((uri, DC["spatial"], Literal(value)))
    elif key == "temporal_coverage":
        rec.add((uri, DC["temporal"], Literal(value)))
    elif key in ("precision", "granularity", "temporal_granularity",
                 "geospatial_granularity", "geographic_granularity", "geographical_granularity"):
        rec.add((uri, DCAT["granularity"], Literal(value)))
    elif key in ("date_released",):
        rec.add((uri, DC["issued"], parse_date(value)))
    elif key in ("date_modified", "date_updated"):
        rec.add((uri, DC["modified"], parse_date(value)))
    elif key in ("agency", "department"):
        dept = BNode()
        rec.add((uri, DC["source"], dept))
        rec.add((dept, RDFS["label"], Literal(value)))
    elif key == "import_source":
        rec.add((uri, DC["source"], Literal(value)))
    elif key == "external_reference":
        rec.add((uri, SKOS["notation"], Literal(value)))
    elif key == "categories":
        if isinstance(value, (list, tuple)): pass
        elif isinstance(value, basestring): value = value.split(',')
        else: value = [value]
        for cat in [x.strip() for x in value]:
           rec.add((uri, DCAT["theme"], Literal(cat)))
    else:
        extra = BNode()
        rec.add((uri, DC.relation, extra))
        rec.add((extra, RDF.value, Literal(value)))
        #TODO Is this correct?
        #rec.add((extra, RDF.label, Literal(key)))
        rec.add((extra, RDFS["label"], Literal(key)))

def _process_relationship(self, rec, uri, rdata):
    pass

def _process_linkset(rec, uri, key, value):
    _unused, target = key.split(":")
    target = self.pkg_uri({ "name" : target })
    linkset = BNode()
    rec.add((uri, VOID["subset"], linkset))
    rec.add((linkset, RDF["type"], VOID["Linkset"]))
    rec.add((linkset, VOID["subjectTarget"], uri))
    rec.add((linkset, VOID["objectTarget"], target))
    count = BNode()
    rec.add((linkset, VOID["triples"], Literal(int(value))))




