from enum import Enum
import sqlparse
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple
import re


class EXISTENCE(Enum):
    NON = 0
    LEFT = 1
    RIGHT = 2
    BOTH = 3


class CARDINALITY(Enum):
    ONE_TO_ONE = ("1", "1")
    ONE_TO_MANY = ("1", "N")
    MANY_TO_ONE = ("N", "1")


@dataclass
class RelationShip:
    left: str
    right: str
    name: str
    is_identifying: bool
    existence: EXISTENCE
    cardinality: CARDINALITY


@dataclass
class Attribute:
    name: str
    is_primary: bool
    is_nullable: bool
    references: List[Tuple[str, str, bool]]


@dataclass
class Table:
    name: str
    attributes: List[Attribute]


def parse_create_table(sql: str) -> Table:
    # Extract the table name
    table_name_match = re.search(r"CREATE\s+TABLE\s+\[(\w+)\]", sql, re.IGNORECASE)
    if not table_name_match:
        raise ValueError("Table name not found")
    table_name = table_name_match.group(1)

    # Extract column definitions (stop before constraints)
    column_matches = re.findall(
        r"^\s*\[(\w+)\]\s+([\w\s\(\),]+?)(?:,|\n\s*CONSTRAINT|\n\s*\))",  # Match columns only
        sql,
        re.MULTILINE | re.DOTALL,
    )

    # Regex to match the fields within PRIMARY KEY clause
    primary_key_match = re.search(
        r"PRIMARY\s+KEY\s*\(\s*(?:\[\s*([\w\s]+)\s*\]\s*,?\s*)+\)", sql, re.IGNORECASE
    )

    primary_keys = []
    if primary_key_match:
        # Find all matches within the PRIMARY KEY clause
        matches = re.findall(r"\[\s*([\w\s]+)\s*\]", primary_key_match.group())
        primary_keys = [key.strip() for key in matches]

    # Extract foreign keys
    foreign_key_matches = re.findall(
        r"FOREIGN\s+KEY\s+\(\[(\w+)\]\)\s+REFERENCES\s+\[(\w+)\]\s+\(\[(\w+)\]\)(?:.*?ON\s+DELETE\s+CASCADE)?",
        sql,
        re.IGNORECASE,
    )
    foreign_keys = {
        fk[0]: (
            fk[1],  # Referenced table
            fk[2],  # Referenced column
            bool(
                re.search(
                    rf"FOREIGN KEY \(\[{fk[0]}\]\).*?ON DELETE CASCADE",
                    sql,
                    re.IGNORECASE,
                )
            ),  # Cascade check
        )
        for fk in foreign_key_matches
    }

    # Parse attributes
    attributes = []
    for column in column_matches:
        column_name = column[0]
        column_definition = column[1]

        # Check if column is nullable
        is_nullable = "NOT NULL" not in column_definition

        # Check if column is primary key
        is_primary = column_name in primary_keys

        # Get references
        references = []
        if column_name in foreign_keys:
            references.append(foreign_keys[column_name])

        attributes.append(
            Attribute(
                name=column_name,
                is_primary=is_primary,
                is_nullable=is_nullable,
                references=references,
            )
        )

    return Table(name=table_name, attributes=attributes)


def get_create_table_statements(sql: str):
    """
    Extract only the CREATE TABLE statements from a multi-statement SQL script.

    Args:
        sql (str): The input SQL script.

    Returns:
        List[str]: A list of CREATE TABLE statements.
    """
    # Parse and split SQL into individual statements
    parsed_statements = sqlparse.split(sql)

    # Filter statements to include only CREATE TABLE
    create_table_statements = [
        sqlparse.format(stmt, strip_comments=True).strip()
        for stmt in parsed_statements
        if stmt.strip().upper().startswith("CREATE TABLE")
    ]
    return create_table_statements


# Foo -- Bar [color = "black:invis:black"]
# def extract_definitions(token_list):
#     definitions = []
#     tmp = []
#     par_level = 0
#     for token in token_list.flatten():
#         if token.is_whitespace:
#             continue
#         elif token.match(sqlparse.tokens.Punctuation, "("):
#             par_level += 1
#             continue
#         if token.match(sqlparse.tokens.Punctuation, ")"):
#             if par_level == 0:
#                 break
#             else:
#                 par_level -= 1
#         elif token.match(sqlparse.tokens.Punctuation, ","):
#             if par_level == 1:
#                 if tmp:
#                     definitions.append(tmp)
#                 tmp = []
#         else:
#             tmp.append(token)
#     if tmp:
#         definitions.append(tmp)
#     return definitions


# def get_data(path):
#     with open(path, "r") as f:
#         tables = dict()
#         for parsed in sqlparse.parsestream(f):
#             par = parsed.token_next_by(i=sqlparse.sql.Identifier)[1]
#             if par:
#                 table = par.get_name().strip("[]")
#                 par = parsed.token_next_by(i=sqlparse.sql.Parenthesis)[1]
#                 if par:
#                     columns = extract_definitions(par)

#                     for column in columns:
#                         if table not in tables:
#                             tables[table] = [[t.value.strip("[]") for t in column]]
#                         else:
#                             tables[table].append([t.value.strip("[]") for t in column])
#     return tables


# def get_constraint(r):
#     r = r.copy()
#     while len(r) and r[0].upper().find("KEY") == -1:
#         r.pop(0)
#     if r[0].upper() == "KEY":
#         r[0] = "f"
#         while len(r) and r[1].upper().find("REFERENCES") == -1:
#             r.pop(1)
#         r.pop(1)
#         r = r[:2] + [any(map(lambda x: x.upper() == "CASCADE", r))]
#     else:
#         r[0] = "p"
#     return r


# def get_attributes(attr):
#     result = dict()
#     for k, v in attr.items():
#         at = []
#         co = []
#         for r in v:
#             if r[0].upper() != "CONSTRAINT":
#                 at.append((r[0], "NOT NULL" not in " ".join(r).upper()))
#             else:
#                 co.append(get_constraint(r))
#         result[k] = at, co
#     return result


# def get_s(result):
#     def add_a():
#         def get_pri_text(a, const):
#             if a in list(filter(lambda x: x[0] == "p", const))[0][1:]:
#                 return f"<<U>{a}</U>>"
#             return f'"{a}"'

#         return "\n\n".join(
#             [
#                 "\n".join(
#                     [
#                         f"    {table}__{a} [label = {get_pri_text(a, const)};];"
#                         for (a, _) in attr
#                     ]
#                 )
#                 for table, (attr, const) in result.items()
#             ]
#         )

#     def add_e():
#         weak = " [peripheries = 2;]"
#         t = dict()
#         for k, (_, const) in result.items():
#             w = False
#             for c in const:
#                 if c[0] == "f" and c[2]:
#                     t[k] = True
#                     w = True
#                     break
#             if not w:
#                 t[k] = False

#         return "\n    ".join([f"{i}{weak if t[i] else ''};" for i in result.keys()])

#     def get_names():
#         relationships = [
#             ((table, c[1]), c[2])
#             for table, (_, const) in result.items()
#             for c in const
#             if c[0] == "f"
#         ]
#         res = []
#         c = dict()
#         for relationship in relationships:
#             if relationship[0] in c:
#                 c[relationship[0]] += 1
#             else:
#                 c[relationship[0]] = 0
#             res.append(
#                 (
#                     relationship,
#                     f"{relationship[0][0]}__{relationship[0][1]}{c[relationship[0]] + 1 if c[relationship[0]] > 0 else ""}",
#                 )
#             )
#         return res

#     def add_r():
#         return "\n".join(
#             [
#                 f"    {n[1]}{' [peripheries = 2;]' if n[0][1] else ""};"
#                 for n in get_names()
#             ]
#         )

#     def add_c():
#         r = []
#         for table, (attr, _) in result.items():
#             r.append(
#                 f'  subgraph {table} {{{"".join([f"\n    {table} -- {table}__{a};" for (a, _) in attr])}\n  }}'
#             )
#         r.append(
#             f'  subgraph connections {{\n    edge [ len = 4; ];\n{"".join([f"\n    {t[0]} -- {n};\n    {t[1]} -- {n};" for (t, _), n in get_names()])}\n  }}'
#         )
#         return "\n\n".join(r)

#     r = f"""graph ERD {{
#   fontname = "Helvetica,Arial,sans-serif";
#   label = "FBMINI ERD";
#   fontsize = 24;
#   layout = neato;
#   scale = 1.5;
#   node [fontname = "Helvetica,Arial,sans-serif";];
#   edge [fontname = "Helvetica,Arial,sans-serif"; len = 3;];

#   subgraph relationships {{
#     node [shape = diamond; fillcolor = "#7a7af3"; style = "rounded,filled"; color = black;];

# {add_r()}
#   }}

#   subgraph entities {{
#     node [shape = box; fillcolor = "#43ce43"; style = "filled"; color = black;];

#     {add_e()}
#   }}

#   subgraph attributes {{
#     node [shape = ellipse; fillcolor = "#ff3d3d"; style = filled; color = black;];

# {add_a()}
#   }}

# {add_c()}
# }}
#     """

#     return r


def get_tables(sql: str) -> List[Table]:
    with open(sql, "r") as f:
        return [
            parse_create_table(statement)
            for statement in get_create_table_statements(f.read())
        ]


def extract_relationships(tables: List[Dict[str, Any]]) -> List[RelationShip]:
    relationships = []
    relation_counts = dict()
    for table in tables:
        for attribute in table.attributes:
            if attribute.references:
                for ref_table, ref_column, cascade in attribute.references:
                    relation = (table.name, ref_table)
                    if relation in relation_counts:
                        relation_counts[relation] += 1
                    else:
                        relation_counts[relation] = 0
                    is_identifying = cascade
                    existence = (
                        EXISTENCE.BOTH if not attribute.is_nullable else EXISTENCE.RIGHT
                    )
                    cardinality = (
                        CARDINALITY.ONE_TO_ONE
                        if attribute.is_primary
                        else CARDINALITY.MANY_TO_ONE
                    )
                    relationship = RelationShip(
                        left=table.name,
                        right=ref_table,
                        name=f"{table.name}__{ref_table}{relation_counts[relation] + 1 if relation_counts[relation] else ""}",
                        is_identifying=is_identifying,
                        existence=existence,
                        cardinality=cardinality,
                    )
                    relationships.append(relationship)
    return relationships


def get_dot(tables: List[Table], relationships: List[RelationShip]):
    def add_a():
        return "\n\n".join(
            [
                "\n".join(
                    [
                        f"    {table.name}__{attribute.name} [label = {f"<<U>{attribute.name}</U>>" if attribute.is_primary else f'"{attribute.name}"'};];"
                        for attribute in table.attributes
                    ]
                )
                for table in tables
            ]
        )

    def add_e():
        weak = " [peripheries = 2;]"
        entities = []
        for table in tables:
            for relationship in relationships:
                if table.name == relationship.left:
                    entities.append((table.name, True))
                    break
            entities.append((table.name, False))

        return "\n    ".join(
            [f"{name}{weak if is_weak else ''};" for name, is_weak in entities]
        )

    def add_r():
        return "\n".join(
            [
                f"    {relationship.name}{' [peripheries = 2;]' if relationship.is_identifying else ""};"
                for relationship in relationships
            ]
        )

    def add_c():
        r = []
        for table in tables:
            r.append(
                f'  subgraph {table.name} {{{"".join([f"\n    {table.name} -- {table.name}__{attribute.name};" for attribute in table.attributes])}\n  }}'
            )
        r.append(
            f'  subgraph connections {{\n    edge [ len = 4; ];\n{"".join([f"\n    {relationship.left} -- {relationship.name};\n    {relationship.right} -- {relationship.name};" for relationship in relationships])}\n  }}'
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


tables = get_tables("test.sql")
relationships = extract_relationships(tables)

v = get_dot(tables, relationships)
with open("test2.dot", "w") as f:
    f.write(v)
