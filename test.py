import sqlparse
from collections import Counter

# Foo [peripheries = 2]
# Foo -- Bar [color = "black:invis:black"]
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
        weak = " [peripheries = 2;]"
        t = dict()
        for k, (_, const) in result.items():
            w = False
            for c in const:
                if c[0] == "f" and c[2]:
                    t[k] = True
                    w = True
                    break
            if not w:
                t[k] = False

        return "\n    ".join([f"{i}{weak if t[i] else ''};" for i in result.keys()])

    def get_names():
        relationships = [
            (table, c[1])
            for table, (_, const) in result.items()
            for c in const
            if c[0] == "f"
        ]
        res = []
        counts = Counter(relationships)
        for count in counts:
            for i in range(counts[count]):
                res.append(((count[0], count[1]), f"{count[0]}__{count[1]}{i if i > 0 else ""}"))
        return res

    def add_r():
        return "\n".join([f"    {n[1]};" for n in get_names()])

    def add_c():
        r = []
        for k, (v, co) in result.items():
            r.append(
                f'  subgraph {k} {{{"".join([f"\n    {k} -- {k}__{i};" for i in v])}\n  }}'
            )
        r.append(
            f'  subgraph connections {{\n    edge [ len = 4; ];\n{"".join([f"\n    {t[0]} -- {n};\n    {t[1]} -- {n};" for t, n in get_names()])}\n  }}'
        )
        return "\n\n".join(r)

    r = f"""graph ERD {{
  fontname = "Helvetica,Arial,sans-serif";
  label = "FBMINI ERD";
  fontsize = 24;
  layout = neato;
  scale = 1.5;
  node [fontname = "Helvetica,Arial,sans-serif";];
  edge [fontname = "Helvetica,Arial,sans-serif"; len = 3;];

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


v = get_s(get_attributes(get_data("test.sql")))
with open("test.dot", "w") as f:
    f.write(v)
