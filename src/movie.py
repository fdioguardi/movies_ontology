from rdflib import Namespace, Graph, Literal
from rdflib.namespace import OWL, RDF
from src.birdify import graph_from_tree
from urllib.parse import urlsplit
from w3lib.url import is_url


class Movie(object):
    def __init__(self, json_dl):
        self.data = json_dl

    def to_graph(self):
        graph = Graph()
        graph.namespace_manager.bind(
            "",
            Namespace(
                "https://raw.githubusercontent.com/fdioguardi/"
                + "movies_ontology/master/movie.ttl#"
            ),
        )
        graph_from_tree(
            self.data,
            None,
            Namespace("https://schema.org/"),
            Namespace(
                "https://raw.githubusercontent.com/fdioguardi/"
                + "movies_ontology/master/movie.ttl#"
            ),
            graph,
      )
        return graph

    def normalize(self, source_url):
        self.data = self.standarize_keys()
        self.data = self.remove_null_values(self.data)

        if not "@type" in self.data.keys():
            self.data["@type"] = "Movie"

        if "url" in self.data.keys():
            self.data = self.complete_urls(self.data, source_url)

        self.remove_data(
            [
                "@id",
                "dateCreated",
                "dateModified",
                "datePublished",
                "url",
                "hasPart",
            ]
        )

        return self

    def complete_urls(self, value, url):
        if not isinstance(value, dict):
            return value

        if "url" in value.keys():
            if not self.is_valid_url(value["url"]):
                splitted_url = urlsplit(url)
                valid_url = (
                    splitted_url[0] + "://" + splitted_url[1] + value["url"]
                )
                if self.is_valid_url(valid_url):
                    value["url"] = valid_url

        for k, v in value.items():
            if isinstance(v, list):
                new_list = []
                for element in v:
                    new_list.append(self.complete_urls(element, url))
            else:
                value[k] = self.complete_urls(v, url)

        return value

    def is_valid_url(self, url):
        return is_url(url) and (not " " in url)

    def remove_null_values(self, value):
        if isinstance(value, list):
            return [
                self.remove_null_values(val)
                for val in value
                if self.is_valid_value(val)
            ]
        elif isinstance(value, dict):
            return {
                key: self.remove_null_values(val)
                for key, val in value.items()
                if self.is_valid_value(val)
            }
        else:
            return value

    def is_valid_value(self, value):
        return (value is not None) and (value != "")

    def standarize_keys(self):
        problematic_keys = [("actor", "actors"), ("url", "mainEntityOfPage")]

        for pair in problematic_keys:
            standard_key, key = pair
            if key in self.data:
                self.data[standard_key] = self.data.pop(key)

        return self.data

    def remove_data(self, keys_to_remove):
        for key in keys_to_remove:
            if key in self.data.keys():
                del self.data[key]

        return self
