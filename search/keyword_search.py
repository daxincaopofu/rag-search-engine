#!/usr/bin/env python3

import json
from collections import namedtuple
import string
from functools import reduce
from nltk.stem import PorterStemmer


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

    def __init__(self, filepath, stopwords_fp):
        self.filepath = filepath
        self.stopwords_fp = stopwords_fp
        self.stopwords = set()
        self.movies = {}
        self.stemmer = PorterStemmer()

    def __enter__(self):
        with open(self.filepath) as file:
            try:
                movies_json = json.load(file)
            except Exception:
                return
            self.movies = movies_json["movies"]

        with open(self.stopwords_fp) as file:
            for line in file.read().splitlines():
                self.stopwords.add(line)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __transform_text(self, text):
        # Transform query and title
        transforms = [
            ("lowercase", lambda x: x.lower()),
            ("remove_punctuation", remove_punctuation),
            ("tokenize_text", self.__tokenize_text),
            (
                "remove_stopwords",
                lambda tokens: [self.__remove_stopwords(text) for text in tokens],
            ),
            ("remove_empty", lambda tokens: [token for token in tokens if token]),
            ("stem", lambda tokens: [self.stemmer.stem(token) for token in tokens]),
        ]

        transformed_text = reduce(lambda x, y: y[1](x), transforms, text)
        return transformed_text

    def __tokenize_text(self, text):
        return [x for x in text.split(" ") if x]

    def __remove_stopwords(self, text):
        return text if text not in self.stopwords else ""

    def query(self, query, limit=5, debug=False):
        movie = namedtuple("Movie", ["id", "title"])
        results = []

        query_tokens = self.__transform_text(query)
        # print(query_tokens)

        for id, item in enumerate(self.movies):
            if debug and id % 100 == 0:
                print(item)
            title = item["title"]
            title_tokens = self.__transform_text(title)

            any_match = False
            for query_token in query_tokens:
                for title_token in title_tokens:
                    if query_token in title_token:
                        any_match = True
                        if debug:
                            print(f"Found {query} in {item["title"]}")
                        break
                if any_match:
                    break
            if any_match:
                results.append(movie(item["id"], item["title"]))
        results.sort(key=lambda x: x[0])
        return [res[1] for res in results][:limit]
