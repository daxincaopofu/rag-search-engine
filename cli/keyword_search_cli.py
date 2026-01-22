#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path

# Ensure project root is on sys.path so the 'search' package can be imported when running this script directly
sys.path.append(str(Path(__file__).resolve().parents[1]))

from search.keyword_search import SearchMovies, InvertedIndex


def main() -> None:
    parser = argparse.ArgumentParser(description="Keyword Search CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    search_parser = subparsers.add_parser("search", help="Search movies using BM25")
    search_parser.add_argument("query", type=str, help="Search query")

    search_parser = subparsers.add_parser("build", help="Build movie index")

    search_parser = subparsers.add_parser(
        "tf", help="Get the term frequency of a doc + term combination"
    )
    search_parser.add_argument("docId", type=str, help="Document Id")
    search_parser.add_argument("term", type=str, help="Search term")

    search_parser = subparsers.add_parser("idf", help="Get the IDF of a term")
    search_parser.add_argument("term", type=str, help="Search term")

    args = parser.parse_args()
    MovieIndex = InvertedIndex(debug=False)

    match args.command:
        case "search":
            print("Loading movie index")
            MovieIndex.load()
            print(f"Searching for: {args.query}")
            results = []
            for tok in MovieIndex.transform_query(args.query):
                results += MovieIndex.get_documents(tok)
                if len(results) >= 5:
                    for docid in results[:5]:
                        document = MovieIndex.docmap.get(docid, {})
                        print(document.get("title"), document.get("id"))
                    exit(0)
            print("Not enough results found")
            exit(1)
        case "tf":
            print("Loading movie index")
            MovieIndex.load()
            print(f"Term Frequency for docId: {args.docId}, term: {args.term}")
            print(MovieIndex.get_tf(int(args.docId), args.term))

        case "idf":
            print("Loading movie index")
            MovieIndex.load()
            print(
                f"Inverse document frequency of '{args.term}': {MovieIndex.get_idf(args.term):.2f}"
            )

        case "build":
            print(f"Building movie index")
            MovieIndex.build("data/movies.json", "data/stopwords.txt")
            print(f"Saving index to cache: {len(MovieIndex.index)} documents")
            MovieIndex.save()
        case _:
            parser.print_help()


if __name__ == "__main__":
    main()
