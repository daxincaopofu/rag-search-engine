#!/usr/bin/env python3

import json
from collections import namedtuple
import string
from functools import reduce


def remove_punctuation(text):
    """
    Removes all punctuation from a given string.

    Args:
        text (str): The input string with punctuation.

    Returns:
        str: The new string with all punctuation removed.
    """
    # Create a translation table that maps every punctuation character to None (removal)
    translator = str.maketrans("", "", string.punctuation)

    # Use the translate method to apply the mapping
    return text.translate(translator)


class SearchMovies:

    def __init__(self, filepath):
        self.filepath = filepath
        self.movies = None

    def __enter__(self):
        with open(self.filepath) as file:
            try:
                movies_json = json.load(file)
            except Exception:
                return
            self.movies = movies_json["movies"]
            return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __transform_text(self, text):
        # Transform query and title
        transforms = [
            ("lowercase", lambda x: x.lower()),
            ("remove_punctuation", remove_punctuation),
        ]

        transformed_text = reduce(lambda x, y: y[1](x), transforms, text)
        return transformed_text

    def query(self, query, limit=5, debug=False):
        movie = namedtuple("Movie", ["id", "title"])
        results = []

        for id, item in enumerate(self.movies):
            if debug and id % 100 == 0:
                print(item)
            if self.__transform_text(query) in self.__transform_text(item["title"]):
                if debug:
                    print(f"Found {query} in {item["title"]}")
                results.append(movie(item["id"], item["title"]))
        results.sort(key=lambda x: x[0])
        return [res[1] for res in results][:limit]
