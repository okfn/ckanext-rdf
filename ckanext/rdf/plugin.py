from ckan.plugins import implements, IRoutes, SingletonPlugin

class DCatApi(SingletonPlugin):
    implements(IRoutes)

    def before_map(self, route_map):
        controller = "ckanext.rdf.controllers:DCatApiController"
        route_map.connect("/rdf/package/{id}", controller=controller,
                          action="show")
        route_map.connect("/rdf/sparql", controller=controller,
                          action="sparql")
        return route_map

    def after_map(self, route_map):
        return route_map
