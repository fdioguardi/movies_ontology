from json import load
from rdflib.namespace import OWL, RDFS, RDF, XDS
from rdflib import Namespace, Graph, Literal
from src.iri_generator import IRIGenerator


def graph_from_tree(
    node, propriety_name, parent_node, schema, movie_ontology, knowledge_graph
):
    if not isinstance(node, dict):
        return generate_literal(propriety_name, node)

    node.pop("@context", None)
    individual = movie_ontology[name_individual(node, parent_node)]
    knowledge_graph.add((individual, RDF.type, schema[node["@type"]]))

    if "url" in node:
        knowledge_graph.add((individual, RDFS.seeAlso, schema[node["url"]]))

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
        if key in ["@type", "url"]:
            continue

        if isinstance(value, list):
            for element in value:
                knowledge_graph.add(
                    (
                        individual,
                        schema[key],
                        graph_from_tree(
                            element,
                            key,
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
                        key,
                        node,
                        schema,
                        movie_ontology,
                        knowledge_graph,
                    ),
                )
            )


def graph_from_tp1(json):
    graph = Graph()
    graph.namespace_manager.bind(
        "",
        Namespace(
            "https://raw.githubusercontent.com/fdioguardi/"
            + "movies_ontology/master/movie.ttl#"
        ),
    )

    schema = Namespace("https://schema.org/")
    movie_ontology = Namespace(
        "https://raw.githubusercontent.com/fdioguardi/"
        + "movies_ontology/master/movie.ttl#"
    )

    cheat_sheet = {
        "Calificación": "contentRating",
        "Director": "hasDirector",
        "Duración": "duration",
        "Género": "genre",
        "Idioma": "inLanguage",
        "Origen": "countryOfOrigin",
        "Sinopsis": "description",
        "Web Oficial": "url",
    }

    for key, value in json.items():  # recorre por movies. 1 key = 1 movie
        if "Título Original" in value.keys():
            movie_name = value.pop("Título Original")
        else:
            movie_name = key

        # agrega el nodo Movie
        movie = movie_ontology[movie_name.replace(" ", "_")]
        graph.add((movie, RDF.type, schema["Movie"]))

        # recorro la movie para agregar cada cosa
        for k, v in value.items():
            add_key_to_graph_tp1(
                graph, cheat_sheet, movie, movie_ontology, k, v, schema
            )

    return graph


def add_key_to_graph_tp1(
    graph, cheat_sheet, movie, movie_ontology, key, value, schema
):

    if key in ["Cinema La Plata", "Cinepolis"]:
        for k in value.keys():
            add_key_to_graph_tp1(
                graph, cheat_sheet, movie, movie_ontology, k, value[k], schema
            )

    elif key == "Actores":
        if isinstance(value, list):
            for v in value:
                add_entity(
                    graph, schema, movie, v, movie_ontology, "Person", "actor"
                )
        else:
            add_entity(
                graph, schema, movie, value, movie_ontology, "Person", "actor"
            )

    elif key == "Distribuidora":
        if isinstance(value, list):
            for v in value:
                add_entity(
                    graph,
                    schema,
                    movie,
                    v,
                    movie_ontology,
                    "Organization",
                    "productionCompany",
                )
        else:
            add_entity(
                graph,
                schema,
                movie,
                value,
                movie_ontology,
                "Organization",
                "productionCompany",
            )

    elif key in cheat_sheet.keys():
        if isinstance(value, list):
            for v in value:
                graph.add(
                    (
                        movie,
                        schema[cheat_sheet[key]],
                        generate_literal(cheat_sheet[key], v),
                    )
                )

        else:
            graph.add(
                (
                    movie,
                    schema[cheat_sheet[key]],
                    generate_literal(cheat_sheet[key], value),
                )
            )

    else:  # habemus horarios
        add_timetable(graph, schema, cheat_sheet, movie, movie_ontology, value)


def add_timetable(
    graph, schema, cheat_sheet, movie, movie_ontology, full_timetable
):
    for key, value in full_timetable.items():
        if isinstance(value, dict):  # es de cinepolis

            # creo el movie theater
            movie_theater = movie_ontology[key.replace(" ", "_")]
            graph.add((movie_theater, RDF.type, schema["MovieTheater"]))
            graph.add(
                (movie_theater, schema["name"], generate_literal("name", key))
            )

            for format, time_list in value.items():

                video_format = format.split(" • ")[1]

                for start_time in time_list:

                    # creo cada screening_event
                    screening_event = movie_ontology[
                        format.replace(" • ", "_") + "_" + start_time
                    ]
                    graph.add(
                        (screening_event, RDF.type, schema["ScreeningEvent"])
                    )
                    graph.add(
                        (
                            screening_event,
                            schema["videoFormat"],
                            generate_literal("videoFormat", video_format),
                        )
                    )

                    schedule = movie_ontology[start_time]
                    graph.add((schedule, RDF.type, schema["Schedule"]))
                    graph.add(
                        (
                            schedule,
                            schema["startTime"],
                            generate_literal("start_time", start_time),
                        )
                    )

                    # engancho screening_event con schedule
                    graph.add(
                        (screening_event, schema["eventSchedule"], schedule)
                    )

                    # engancho el screening_event al movie theather
                    graph.add(
                        (movie_theater, schema["event"], screening_event)
                    )

                    # engancho el screening_event con la movie
                    graph.add(
                        (screening_event, schema["workPresented"], movie)
                    )

        else:  # es de cinemalaplata
            # creo el movie theater
            movie_theater = movie_ontology[
                key.split(" - ")[0].replace(" ", "_")
            ]
            graph.add((movie_theater, RDF.type, schema["MovieTheater"]))
            graph.add(
                (
                    movie_theater,
                    schema["name"],
                    generate_literal("name", key.split(" - ")[0]),
                )
            )

            video_format = key.split(" - ")[1].replace(" ", "_")

            for show in value:
                language = show[0 : show.find(":")]
                times = show[show.find(" ") :].strip()

                for start_time in times.split(" - "):

                    # creo cada screening_event
                    screening_event = movie_ontology[
                        key.replace(" ", "_") + "_" + start_time
                    ]
                    graph.add(
                        (screening_event, RDF.type, schema["ScreeningEvent"])
                    )
                    graph.add(
                        (
                            screening_event,
                            schema["videoFormat"],
                            generate_literal("videoFormat", video_format),
                        )
                    )

                    schedule = movie_ontology[start_time]
                    graph.add((schedule, RDF.type, schema["Schedule"]))
                    graph.add(
                        (
                            schedule,
                            schema["startTime"],
                            generate_literal("startTime", start_time),
                        )
                    )

                    # engancho screening_event con schedule
                    graph.add(
                        (screening_event, schema["eventSchedule"], schedule)
                    )

                    # engancho el screening_event al movie theather
                    graph.add(
                        (movie_theater, schema["event"], screening_event)
                    )

                    # engancho el screening_event con la movie
                    graph.add(
                        (screening_event, schema["workPresented"], movie)
                    )


def add_entity(
    graph, schema, node, entity_value, movie_ontology, entity, object_property
):
    individual = movie_ontology[entity_value.replace(" ", "_")]
    graph.add((individual, RDF.type, schema[entity]))
    graph.add(
        (individual, schema["name"], generate_literal("name", entity_value))
    )
    graph.add((node, schema[object_property], individual))
    return individual


def generate_literal(data_propriety, data_value):
    "Defaults to XDS.string"
    datatypes = {
        XDS.Name: [
            "name",
        ],
        XDS.anyURI: [
            "sameAs",
        ],
        XDS.dateTime: [
            "dateCreated",
            "endTime",
            "startDate",
            "startTime",
            "uploadDate",
        ],
        XDS.double: [
            "bestRating",
            "ratingValue",
            "worstRating",
        ],
        XDS.integer: [
            "ratingCount",
            "reviewCount",
        ],
        XDS.language: [
            "inLanguage",
        ],
    }

    for xds_type, list_of_proprieties in datatypes.items():
        if data_propriety in list_of_proprieties:
            return Literal(data_value, datatype=xds_type)

    return Literal(data_value)
