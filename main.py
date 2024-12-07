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
            "--title",
            "-t",
            required=False,
            help="Title of the graph",
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

    @property
    def title(self):
        return self.args.title


if __name__ == "__main__":
    app = CommandLine()
    source_file = app.source
    formats = ["png", "pdf", "svg"]
    filename = Path(source_file).stem

    if app.output:
        output_file = app.output
    else:
        output_file = path.join("out", filename)

    tables = parse_table_sql(source_file)
    relationships = extract_relationships(tables)

    graph = create_erd_graph(tables, relationships, title=app.title)

    with open(output_file + ".dot", 'w') as f:
        f.write(graph.source)

    for format in formats:
        graph.render(outfile=output_file + "." + format, cleanup=True)

    if app.print_message:
        with open(output_file + ".dot", "r") as f:
            print(f.read())
