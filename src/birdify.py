from json import load
from rdflib.namespace import OWL, RDF
from rdflib import Namespace, Graph, Literal
from src.iri_generator import IRIGenerator


def graph_from_tree(
    node, parent_node, schema, movie_ontology, knowledge_graph
):
    if not isinstance(node, dict):
        return Literal(node)

    node.pop("@context", None)
    individual = movie_ontology[
        name_individual(node, parent_node)
    ]
    knowledge_graph.add((individual, RDF.type, schema[node["@type"]]))

    add_children(node, schema, movie_ontology, knowledge_graph, individual)

    return individual


def name_individual(node, parent):
    try:
        if node["@type"] in [
            "Person",
            "Movie",
            "VideoObject",
            "AggregateRating",
            "Country",
        ]:
            iri = node["name"]

        elif node["@type"] == "Organization":
            if "name" in node.keys():
                iri = node["name"]
            elif "url" in node.keys():
                iri = node["url"]
            else:
                iri = node["mainEntityOfPage"]

        elif node["@type"] == "Review":
            iri = (
                node["@type"]
                + "_"
                + node["author"]["name"]
                + "_"
                + node["dateCreated"]
            )

        elif node["@type"] == "Rating":
            iri = node["@type"] + "_" + name_individual(parent, None)

        elif node["@type"] == "PublicationEvent":
            iri = node["@type"] + "_" + node["startDate"]

        else:
            iri = node["@type"] + "_" + node["contentUrl"]

    except KeyError:
        iri = node["@type"] + "_" + str(IRIGenerator.get_iri(node["@type"]))

    return iri.replace(" ", "_")


def add_children(node, schema, movie_ontology, knowledge_graph, individual):
    for key, value in node.items():
        if key == "@type":
            continue

        if isinstance(value, list):
            for element in value:
                knowledge_graph.add(
                    (
                        individual,
                        schema[key],
                        graph_from_tree(
                            element,
                            node,
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
                        node,
                        schema,
                        movie_ontology,
                        knowledge_graph,
                    ),
                )
            )
