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


def graph_from_tree(
    node, parent_node, schema, movie_ontology, knowledge_graph
):
    if not isinstance(node, dict):
        return Literal(node)

    node.pop("@context", None)
    if "@type" in node.keys():
        individual = name_individual(node, parent_node, movie_ontology)
        knowledge_graph.add((individual, RDF.type, schema[node["@type"]]))

    add_children(node, schema, movie_ontology, knowledge_graph, individual)

    return individual


def name_individual(node, parent, base_iri):
    if node["@type"] in [
        "Person",
        "Movie",
        "Organization",
        "VideoObject",
        "AggregateRating",
        "Country",
    ]:
        iri = node["name"]

    elif node["@type"] == "Review":
        iri = "review_" + node["author"]["name"] + "_" + node["dateCreated"]

    elif node["@type"] == "Rating":
        iri = "rating_" + name_individual(parent, None, base_iri)

    else:
        iri = "thumbnail_" + node["contentUrl"]

    return base_iri[iri.replace(" ", "_")]


def add_children(node, schema, movie_ontology, knowledge_graph, individual):
    for key, value in node.items():
        if isinstance(value, list):
            for element in valor:
                knowledge_graph.add(
                    (
                        individual,
                        schema[key],
                        graph_from_tree(
                            element,
                            node[key],
                            schema,
                            movie_ontology,
                            knowledge_graph,
                        ),
                    )
                )
        else:
            knowledge_graph.add(
                (
                    individual,
                    schema[key],
                    graph_from_tree(
                        value,
                        node[key],
                        schema,
                        movie_ontology,
                        knowledge_graph,
                    ),
                )
            )


if __name__ == "__main__":
    main()
