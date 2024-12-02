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
            f'  subgraph connections {{\n    edge [ len = 4; fontsize=30; ];\n{"".join([f"\n    {relationship.left} -- {relationship.name} [ headlabel = \"{relationship.cardinality.value[0]}\";{' color = "black:invis:black"' if relationship.existence.value & 1 else ""}];\n    {relationship.right} -- {relationship.name} [ headlabel = \"{relationship.cardinality.value[1]}\";{' color = "black:invis:black"' if relationship.existence.value & 2 else ""}];" for relationship in relationships])}\n  }}'
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
# Foo -- Bar [color = "black:invis:black"]
