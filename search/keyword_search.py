#!/usr/bin/env python3

import json
from collections import namedtuple, defaultdict, Counter
import string
from functools import reduce
from nltk.stem import PorterStemmer
from typing import List
import pickle
import os


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


class InvertedIndex:

    def __init__(self, cache_dir: str = "./cache"):
        self.cache_dir = cache_dir
        self.index = defaultdict(list)
        self.docmap = defaultdict(str)
        self.term_frequencies = defaultdict(Counter)
        self.stopwords = set()
        self.stemmer = PorterStemmer()

    def tokenize_query(self, query: str) -> List[str]:
        return self.__transform_text(query)

    def __transform_text(self, text: str) -> List[str]:
        # Text Pre-processing
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
        return transformed_text  # pyright: ignore[reportReturnType]

    def __tokenize_text(self, text: str) -> List[str]:
        return [x for x in text.split(" ") if x]

    def __remove_stopwords(self, text: str) -> str:
        return text if text not in self.stopwords else ""

    def __add_document(self, doc_id: int, text: str) -> None:
        tokens = self.__transform_text(text)
        for tok in tokens:
            self.index[tok].append(doc_id)
            self.term_frequencies[doc_id][tok] += 1

    def get_documents(self, term: str) -> List[int]:
        doc_ids = self.index.get(term, [])
        return sorted(doc_ids)

    def get_tf(self, doc_id: int, term: str) -> int:
        tokens = self.__tokenize_text(term)
        if len(tokens) != 1:
            raise ValueError("Term can only have a single token")
        return self.term_frequencies.get(doc_id, Counter()).get(tokens[0], 0)

    def load(self) -> None:
        try:
            with open(f"{self.cache_dir}/index.pkl", "rb") as file:
                self.index = pickle.load(file)
            with open(f"{self.cache_dir}/docmap.pkl", "rb") as file:
                self.docmap = pickle.load(file)
            with open(f"{self.cache_dir}/term_frequencies.pkl", "rb") as file:
                self.term_frequencies = pickle.load(file)
            return
        except Exception as e:
            print("Unable to use cache")
            raise (e)

    def build(self, filepath: str, stopwords_filepath: str) -> None:

        try:
            with open(stopwords_filepath) as file:
                for line in file.read().splitlines():
                    self.stopwords.add(line)
        except Exception as e:
            print(f"Unable to read in stopwords from {stopwords_filepath}")
            print(e)

        with open(filepath) as file:
            try:
                movies = json.load(file)["movies"]
            except Exception:
                return

            for item in movies:
                self.__add_document(
                    int(item["id"]), item["title"] + " " + item["description"]
                )
                self.docmap[int(item["id"])] = item

    def save(self) -> None:
        os.makedirs(self.cache_dir, exist_ok=True)

        if self.index:
            with open(f"{self.cache_dir}/index.pkl", "wb") as file:
                pickle.dump(self.index, file)
        if self.docmap:
            with open(f"{self.cache_dir}/docmap.pkl", "wb") as file:
                pickle.dump(self.docmap, file)
        if self.term_frequencies:
            with open(f"{self.cache_dir}/term_frequencies.pkl", "wb") as file:
                pickle.dump(self.term_frequencies, file)


class SearchMovies:
    """
    MVP implementation without indexing (very inefficient as we have to scan through the documents each time)
    """

    def __init__(self, filepath: str, stopwords_filepath: str):
        self.filepath = filepath
        self.stopwords_fp = stopwords_filepath
        self.stopword = set([])
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
        # Text Pre-processing
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
