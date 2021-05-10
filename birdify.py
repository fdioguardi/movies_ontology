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
        Namespace("https://schema.org/"),
        Namespace(
            "https://raw.githubusercontent.com/fdioguardi/"
            + "scenarios_ontology/master/movie.ttl#"
        ),
        knowledge_graph,
    )


print(knowledge_graph.serialize(format="turtle").decode("utf-8"))


def graph_from_tree(node, schema, movie_ontology, knowledge_graph):
    if not isinstance(node, dict):
        return Literal(node)

    node.pop("@context", None)

    individual = name_individual(node)

    knowledge_graph.add(
        (individual, RDF.type, schema[node.pop("@type", None)])
    )

    add_children(node, schema, knowledge_graph, individual)

    return individual


def name_individual(node):
    pass


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
