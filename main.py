from sql2dot import parse_table_sql, extract_relationships, create_erd_graph

if __name__ == "__main__":
    output_file = "out/CIE206_FL24_T0_02ERD"
    source_file = "test/test.sql"
    formats = ["png", "pdf", "svg"]

    tables = parse_table_sql(source_file)
    relationships = extract_relationships(tables)

    graph = create_erd_graph(tables, relationships)

    for format in formats:
        graph.render(output_file + ".dot", outfile=output_file + "." + format)
