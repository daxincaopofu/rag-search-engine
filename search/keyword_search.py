#!/usr/bin/env python3

import json
from collections import namedtuple


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

    def query(self, query, limit=5):
        movie = namedtuple("Movie", ["id", "title"])
        results = []

        for id, item in enumerate(self.movies):
            # if id % 100 == 0:
            #     print(item)
            if query in item["title"]:
                # print(f"Found {query} in {item["title"]}")
                results.append(movie(item["id"], item["title"]))
        results.sort(key=lambda x: x[0])
        return [res[1] for res in results][:limit]
