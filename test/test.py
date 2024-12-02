from enum import Enum
import sqlparse
from dataclasses import dataclass
from typing import List, Optional
import re
from pprint import pprint


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
class Reference:
    table: str
    column: str
    cascade: bool


@dataclass
class Attribute:
    name: str
    is_primary: bool
    is_nullable: bool
    reference: Optional[Reference]


@dataclass
class Table:
    name: str
    attributes: List[Attribute]


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


# def parse_create_table(sql: str) -> Table:
#     # Extract the table name
#     table_name_match = re.search(r"CREATE\s+TABLE\s+\[(\w+)\]", sql, re.IGNORECASE)
#     if not table_name_match:
#         raise ValueError("Table name not found")
#     table_name = table_name_match.group(1)

#     # Extract column definitions (stop before constraints)
#     column_matches = re.findall(
#         r"^\s*\[(\w+)\]\s+([\w\s\(\),]+?)(?:,|\n\s*CONSTRAINT|\n\s*\))",  # Match columns only
#         sql,
#         re.MULTILINE | re.DOTALL,
#     )

#     # Regex to match the fields within PRIMARY KEY clause
#     primary_key_match = re.search(
#         r"PRIMARY\s+KEY\s*\(\s*(?:\[\s*([\w\s]+)\s*\]\s*,?\s*)+\)", sql, re.IGNORECASE
#     )

#     primary_keys = []
#     if primary_key_match:
#         # Find all matches within the PRIMARY KEY clause
#         matches = re.findall(r"\[\s*([\w\s]+)\s*\]", primary_key_match.group())
#         primary_keys = [key.strip() for key in matches]

#     # Extract foreign keys
#     foreign_key_matches = re.findall(
#         r"FOREIGN\s+KEY\s+\(\[(\w+)\]\)\s+REFERENCES\s+\[(\w+)\]\s+\(\[(\w+)\]\)(?:.*?ON\s+DELETE\s+CASCADE)?",
#         sql,
#         re.IGNORECASE,
#     )
#     foreign_keys = {
#         fk[0]: Reference(
#             fk[1],  # Referenced table
#             fk[2],  # Referenced column
#             bool(
#                 re.search(
#                     rf"FOREIGN KEY \(\[{fk[0]}\]\).*?ON DELETE CASCADE",
#                     sql,
#                     re.IGNORECASE,
#                 )
#             ),  # Cascade check
#         )
#         for fk in foreign_key_matches
#     }

#     # Parse attributes
#     attributes = []
#     for column in column_matches:
#         column_name = column[0]
#         column_definition = column[1]

#         # Check if column is nullable
#         is_nullable = "NOT NULL" not in column_definition

#         # Check if column is primary key
#         is_primary = column_name in primary_keys

#         # Get references
#         references = []
#         if column_name in foreign_keys:
#             references.append(foreign_keys[column_name])

#         attributes.append(
#             Attribute(
#                 name=column_name,
#                 is_primary=is_primary,
#                 is_nullable=is_nullable,
#                 references=references,
#             )
#         )

#     return Table(name=table_name, attributes=attributes)


def parse_create_table(sql: str) -> Table:
    # Extract the table name
    table_name_match = re.search(r"CREATE\s+TABLE\s+(\[\w+\]|\w+)", sql, re.IGNORECASE)
    if not table_name_match:
        raise ValueError("Table name not found")
    table_name = table_name_match.group(1).strip("[]")

    # Extract column definitions
    # column_matches = re.findall(
    #     r"^\s*\[(\w+)\]\s+([\w\s\(\),]+?)(?:,|\n\s*CONSTRAINT|\n\s*\))",
    #     sql,
    #     re.MULTILINE | re.DOTALL,
    # )
    column_matches = re.findall(
        r"^\s*\[(\w+)\]\s+([\w\s\(\),]+?)(?:,|\n\s*CONSTRAINT|\n\s*\))",
        sql,
        re.MULTILINE | re.DOTALL,
    )
    print(column_matches)

    # # Regex to match the fields within PRIMARY KEY clause
    # primary_key_match = re.search(
    #     r"PRIMARY\s+KEY\s*\(([\s\[\],\w]+)\)", sql, re.IGNORECASE
    # )

    # primary_keys = []
    # if primary_key_match:
    #     matches = re.findall(r"\[(\w+)\]", primary_key_match.group(1))
    #     primary_keys = [key.strip() for key in matches]

    # # Extract foreign keys
    # foreign_key_matches = re.findall(
    #     r"FOREIGN\s+KEY\s+\(\[(\w+)\]\)\s+REFERENCES\s+\[(\w+)\]\s+\(\[(\w+)\]\)(?:\s+ON\s+DELETE\s+CASCADE)?",
    #     sql,
    #     re.IGNORECASE,
    # )
    # foreign_keys = {
    #     fk[0]: Reference(
    #         table=fk[1],
    #         column=fk[2],
    #         cascade=bool(re.search(r"ON\s+DELETE\s+CASCADE", sql, re.IGNORECASE)),
    #     )
    #     for fk in foreign_key_matches
    # }

    # # Parse attributes
    # attributes = []
    # for column in column_matches:
    #     column_name = column[0]
    #     column_definition = column[1]

    #     # Check if column is nullable
    #     is_nullable = "NOT NULL" not in column_definition.upper()

    #     # Check if column is primary key
    #     is_primary = column_name in primary_keys

    #     # Get references
    #     reference = foreign_keys.get(column_name, None)

    #     attributes.append(
    #         Attribute(
    #             name=column_name,
    #             is_primary=is_primary,
    #             is_nullable=is_nullable,
    #             reference=reference,
    #         )
    #     )

    # return Table(name=table_name, attributes=attributes)


def get_tables(sql: str) -> List[Table]:
    with open(sql, "r") as f:
        return [
            parse_create_table(statement)
            for statement in get_create_table_statements(f.read())
        ]


def extract_relationships(tables: List[Table]) -> List[RelationShip]:
    """
    Extracts relationships between tables based on their attributes.

    Args:
        tables (List[Table]): A list of parsed tables.

    Returns:
        List[RelationShip]: A list of relationships with detailed attributes.
    """
    relationships = []
    relation_counts = dict()

    for table in tables:
        for attribute in table.attributes:
            # If the attribute references other tables, process its relationships
            if attribute.reference:
                # Define the relationship key for counting
                relation_key = (table.name, attribute.reference.table)
                relation_counts[relation_key] = relation_counts.get(relation_key, 0) + 1

                # Determine the relationship name
                relationship_name = f"{table.name}__{attribute.reference.table}{relation_counts[relation_key] if relation_counts[relation_key] > 1 else ""}"

                # Determine if the relationship is identifying
                # A relationship is identifying if the foreign key is part of the primary key
                is_identifying = attribute.is_primary

                # Determine the existence constraint
                if not attribute.is_nullable and attribute.reference.cascade:
                    existence = EXISTENCE.BOTH
                elif not attribute.is_nullable:
                    existence = EXISTENCE.LEFT
                elif attribute.reference.cascade:
                    existence = EXISTENCE.RIGHT
                else:
                    existence = EXISTENCE.NON

                # Determine cardinality
                # Use multi-column relationships and unique constraints if available
                if attribute.is_primary:
                    cardinality = CARDINALITY.ONE_TO_ONE
                elif any(attr.is_primary for attr in table.attributes):
                    cardinality = CARDINALITY.MANY_TO_ONE
                else:
                    cardinality = CARDINALITY.ONE_TO_MANY

                # Create the relationship
                relationship = RelationShip(
                    left=table.name,
                    right=attribute.reference.table,
                    name=relationship_name,
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


# tables = get_tables("test2.sql")
# relationships = extract_relationships(tables)

# import pprint

# pprint.pprint(tables)
# pprint.pprint(relationships)

# v = get_dot(tables, relationships)
# with open("test3.dot", "w") as f:
#     f.write(v)


get_tables("test2.sql")

tables = [
    Table(
        "employee",
        [
            Attribute("id", True, False, None),
            Attribute(
                "dep_id",
                True,
                False,
                Reference("department", "id", False),
            ),
            Attribute(
                "managed_dep_id",
                False,
                True,
                Reference("department", "id", False),
            ),
        ],
    ),
    Table(
        "department",
        [
            Attribute("id", True, False, None),
        ],
    ),
]
# relationships = extract_relationships(tables)
# v = get_dot(tables, relationships)
# with open("test3.dot", "w") as f:
#     f.write(v)
