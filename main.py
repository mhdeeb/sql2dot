from sql2dot import parse_table_sql, extract_relationships, create_erd_graph

if __name__ == "__main__":
    tables = parse_table_sql("test/test.sql")
    relationships = extract_relationships(tables)

    graph = create_erd_graph(tables, relationships)

    file_name = "out/CIE206_FL24_T0_02ERD"
    formats = ["png", "pdf", "svg"]

    for format in formats:
        graph.render(file_name + ".dot", outfile=file_name + "." + format)
