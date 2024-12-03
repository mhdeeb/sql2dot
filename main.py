from sql2dot import parse_table_sql, extract_relationships, create_erd_graph
from os import path
from pathlib import Path

import argparse


class CommandLine:
    """
    CommandLine class to handle command-line arguments for source and destination files.
    Provides help functionality.
    """

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description="Generate ER diagrams from SQL table definitions."
        )
        self.parser.add_argument(
            "--source",
            "-s",
            required=True,
            help="Path to the source SQL file containing table definitions.",
        )
        self.parser.add_argument(
            "--output",
            "-o",
            required=False,
            help="Path to the output file (excluding extension).",
        )
        self.parser.add_argument(
            "--print",
            "-p",
            help="Print the dot file to the console.",
            action=argparse.BooleanOptionalAction,
        )
        self.args = self.parser.parse_args()

    @property
    def source(self):
        return self.args.source

    @property
    def output(self):
        return self.args.output

    @property
    def print_message(self):
        return self.args.print


if __name__ == "__main__":
    app = CommandLine()
    source_file = app.source
    formats = ["png", "pdf", "svg"]

    if app.output:
        output_file = app.output
    else:
        output_file = path.join("out", Path(source_file).stem)

    tables = parse_table_sql(source_file)
    relationships = extract_relationships(tables)

    graph = create_erd_graph(tables, relationships)

    for format in formats:
        graph.render(output_file + ".dot", outfile=output_file + "." + format)

    if app.print_message:
        with open(output_file + ".dot", "r") as f:
            print(f.read())
