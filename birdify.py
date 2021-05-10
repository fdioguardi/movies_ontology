from json import load
from rdflib.namespace import OWL, RDF
from rdflib import Namespace, Graph, Literal


def main():
    with open("movie.json") as movie_file:
        tree = load(movie_file)

    knowledge_graph = Graph()
    knowledge_graph.namespace_manager.bind("", movie_ontology)
    graph_from_tree(
        tree,
        None,
        Namespace("https://schema.org/"),
        Namespace(
            "https://raw.githubusercontent.com/fdioguardi/"
            + "scenarios_ontology/master/movie.ttl#"
        ),
        knowledge_graph,
    )


print(knowledge_graph.serialize(format="turtle").decode("utf-8"))


def graph_from_tree(node, parent_node, schema, movie_ontology, knowledge_graph):
    if not isinstance(node, dict):
        return Literal(node)

    node.pop("@context", None)
    if "@type" in node.keys():
        individual = name_individual(node, parent_node, movie_ontology)
        knowledge_graph.add(
            (individual, RDF.type, schema[node["@type"]])
        )

    add_children(node, schema, knowledge_graph, individual)

    return individual


def name_individual(node, parent, base_iri):
    tipo = node["@type"]
    iri = ""
    if tipo in ["Person", "Movie", "Organization", "VideoObject", "AggregateRating", "Country"]:
        iri = base_iri[node['name'].replace(" ", "_")]
    elif tipo == "Review":
        iri = base_iri["review_" + node['author']['name'].replace(" ", "_") + "_" + node['dateCreated'].replace(" ", "_")]
    elif tipo == "Rating":
        iri = base_iri["rating_" + name_individual(parent, None, base_iri)]
    else:
        iri = base_iri["thumbnail_" + node["contentUrl"].replace(" ", "_")]
    return iri


def add_children(node, schema, knowledge_graph, individual):
    for key, value in node.items():
        if isinstance(value, list):
            for element in valor:
                knowledge_graph.add(
                    (individual, schema[key], graph_from_tree(element))
                )
        else:
            knowledge_graph.add(
                (individual, schema[key], graph_from_tree(valor))
            )


if __name__ == "__main__":
    main()
