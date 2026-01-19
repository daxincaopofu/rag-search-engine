#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path

# Ensure project root is on sys.path so the 'search' package can be imported when running this script directly
sys.path.append(str(Path(__file__).resolve().parents[1]))

from search.keyword_search import SearchMovies


def main() -> None:
    parser = argparse.ArgumentParser(description="Keyword Search CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    search_parser = subparsers.add_parser("search", help="Search movies using BM25")
    search_parser.add_argument("query", type=str, help="Search query")

    args = parser.parse_args()

    match args.command:
        case "search":
            print(f"Searching for: {args.query}")
            with SearchMovies("data/movies.json") as keywordSearch:
                query_result = keywordSearch.query(args.query, 5)
                for i, title in enumerate(query_result):
                    print(f"{i+1}. {title}")
        case _:
            parser.print_help()


if __name__ == "__main__":
    main()
