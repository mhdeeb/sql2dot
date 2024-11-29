import sqlparse


def extract_definitions(token_list):
    definitions = []
    tmp = []
    par_level = 0
    for token in token_list.flatten():
        if token.is_whitespace:
            continue
        elif token.match(sqlparse.tokens.Punctuation, "("):
            par_level += 1
            continue
        if token.match(sqlparse.tokens.Punctuation, ")"):
            if par_level == 0:
                break
            else:
                par_level -= 1
        elif token.match(sqlparse.tokens.Punctuation, ","):
            if par_level == 1:
                if tmp:
                    definitions.append(tmp)
                tmp = []
        else:
            tmp.append(token)
    if tmp:
        definitions.append(tmp)
    return definitions


def get_data(path):
    with open(path, "r") as f:
        tables = dict()
        for parsed in sqlparse.parsestream(f):
            par = parsed.token_next_by(i=sqlparse.sql.Identifier)[1]
            if par:
                table = par.get_name().strip("[]")
                par = parsed.token_next_by(i=sqlparse.sql.Parenthesis)[1]
                if par:
                    columns = extract_definitions(par)

                    for column in columns:
                        if table not in tables:
                            tables[table] = [[t.value.strip("[]") for t in column]]
                        else:
                            tables[table].append([t.value.strip("[]") for t in column])
    return tables


def get_constraint(r):
    r = r.copy()
    while len(r) and r[0].upper().find("KEY") == -1:
        r.pop(0)
    if r[0].upper() == "KEY":
        r[0] = "f"
        while len(r) and r[1].upper().find("REFERENCES") == -1:
            r.pop(1)
        r.pop(1)
        r = r[:2] + [any(map(lambda x: x.upper() == "CASCADE", r))]
    else:
        r[0] = "p"
    return r


def get_attributes(attr):
    result = dict()
    for k, v in attr.items():
        at = []
        co = []
        for r in v:
            if r[0].upper() != "CONSTRAINT":
                at.append(r[0])
            else:
                co.append(get_constraint(r))
        result[k] = at, co
    return result


def get_s(result):
    def add_a():
        def get_pri_text(a, const):
            if a in list(filter(lambda x: x[0] == "p", const))[0][1:]:
                return f"<<U>{a}</U>>"
            return f'"{a}"'

        return "\n\n".join(
            [
                "\n".join(
                    [
                        f"    {table}__{a} [label = {get_pri_text(a, const)};];"
                        for a in atter
                    ]
                )
                for table, (atter, const) in result.items()
            ]
        )

    def add_e():
        return "\n    ".join([f"{i};" for i in result.keys()])

    def add_r():
        return ""

    def add_c():
        r = []
        for k, (v, co) in result.items():
            r.append(
                f'  subgraph {k} {{{"".join([f"\n    {k} -- {k}__{i};" for i in v])}\n  }}'
            )
        return "\n\n".join(r)

    r = f"""
graph ER {{
  fontname = "Helvetica,Arial,sans-serif";
  label = "Drug Database ERD";
  fontsize = 24;
  layout = neato;
  overlap = "scale";
  node [fontname = "Helvetica,Arial,sans-serif";];
  edge [fontname = "Helvetica,Arial,sans-serif";];

  subgraph relationships {{
    node [shape = diamond; fillcolor = "#7a7af3"; style = "rounded,filled"; color = black;];

    {add_r()}
  }}

  subgraph entities {{
    node [shape = box; fillcolor = "#43ce43"; style = "filled"; color = black;];

    {add_e()}
  }}

  subgraph attributes {{
    node [shape = ellipse; fillcolor = "#ff3d3d"; style = filled; color = black;];

{add_a()}
  }}

{add_c()}
}}
    """

    return r


with open("test.dot", "w") as f:
    f.write(get_s(get_attributes(get_data("test.sql"))))