from dataclasses import dataclass
from enum import Enum
import sqlparse
from sqlparse.sql import Parenthesis, Identifier
from typing import List, Optional


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


def parse_until_conditions(parsed_sql, conditions):
    """
    Iterates through tokens in a parsed SQL statement, stopping for multiple conditions in sequence.

    Args:
        parsed_sql: The parsed SQL statement (output of sqlparse.parse).
        conditions: A list of condition functions, each returning True for the target token.

    Returns:
        A list of tokens that matched the conditions, in the order of the conditions.
    """
    matched_tokens = []
    current_condition_index = 0

    for token in parsed_sql:
        if current_condition_index >= len(conditions):
            break
        # print([token], [token.ttype])
        condition = conditions[current_condition_index]
        if condition(token):
            matched_tokens.append(token)
            current_condition_index += 1

    return matched_tokens


def get_lines(parenthesis):
    """
    Extracts definitions from a parenthesis-enclosed list.
    Strips the outermost parentheses.
    """
    definitions = []
    tmp = []
    par_level = 0
    outer_parenthesis_stripped = False

    for token in parenthesis.flatten():
        if token.is_whitespace:
            continue

        if token.match(sqlparse.tokens.Punctuation, "("):
            if not outer_parenthesis_stripped:
                # Skip the first outer opening parenthesis
                outer_parenthesis_stripped = True
                continue
            par_level += 1
            tmp.append(token.value)  # Include inner opening parentheses
            continue

        if token.match(sqlparse.tokens.Punctuation, ")"):
            if par_level > 0:
                par_level -= 1
                tmp.append(token.value)  # Include inner closing parentheses
                continue
            else:
                # Skip the outermost closing parenthesis
                break

        if token.match(sqlparse.tokens.Punctuation, ",") and par_level == 0:
            # End the current definition only if not within nested parentheses
            if tmp:
                definitions.append(tmp)
                tmp = []
            continue

        # Add the token to the current definition
        tmp.append(token.value)

    # Append the last accumulated tokens if any
    if tmp:
        definitions.append(tmp)

    return definitions


def get_create_table(statment):
    if statment.get_type() != "CREATE":
        return None
    tokens = parse_until_conditions(
        statment,
        [
            lambda token: token.is_keyword and token.value == "TABLE",
            lambda token: isinstance(token, Identifier),
            lambda token: isinstance(token, Parenthesis),
        ],
    )
    if len(tokens) != 3:
        return None

    return tokens[1].value, get_lines(tokens[2])


def get_columns(lines):
    columns = []
    constraints = []
    for line in lines:
        if line[0].upper() not in ["PRIMARY KEY", "FOREIGN", "CONSTRAINT"]:
            columns.append(line)
        else:
            constraints.append(line)
    return columns, constraints


def process_columns(columns):
    attributes = []
    for column in columns:
        name = column[0].strip("[]")
        is_primary = "PRIMARY KEY" in column
        is_nullable = not is_primary and "NOT NULL" not in column
        reference = None
        if "REFERENCES" in column:
            ref = column[column.index("REFERENCES") + 1 :]
            ref_table = ref[0].strip("[]")
            column = ref[2].strip("[]")
            cascade = "ON DELETE CASCADE" in " ".join(ref).upper()
            reference = Reference(ref_table, column, cascade)

        attributes.append(Attribute(name, is_primary, is_nullable, reference))

    return attributes


def process_constraints(constraints):
    result = []
    for constraint in constraints:
        is_primary = False
        if constraint[0] == "PRIMARY KEY":
            constraint = constraint[1:]
            is_primary = True
        elif constraint[0] == "FOREIGN":
            constraint = constraint[2:]
            is_primary = False
        elif constraint[2] == "PRIMARY KEY":
            constraint = constraint[3:]
            is_primary = True
        else:
            constraint = constraint[4:]
            is_primary = False

        if is_primary:
            keys = tuple([i.strip("[]") for i in constraint[1::2]])
            result.append([keys])
        else:
            ref_loc = constraint.index("REFERENCES")
            ref1 = constraint[:ref_loc]
            keys = tuple([i.strip("[]") for i in ref1[1::2]])
            ref2 = constraint[ref_loc + 1 :]
            ref_table = ref2[0].strip("[]")
            ref_columns = tuple(
                [
                    i.strip("[]")
                    for i in ref2[ref2.index("(") + 1 : ref2.index(")")][::2]
                ]
            )
            cascade = "ON DELETE CASCADE" in " ".join(ref2).upper()
            result.append([keys, Reference(ref_table, ref_columns, cascade)])

    return result


def parse_table_sql(sql: str) -> List[Table]:
    tables = []

    with open(sql, "r") as f:
        statments = sqlparse.parse(f.read())
        for statment in statments:
            table = get_create_table(statment)
            if table:
                table_name = table[0].strip("[]")
                columns, constraints = get_columns(table[1])

                cols = process_columns(columns)
                cons = process_constraints(constraints)

                for con in cons:
                    if len(con) == 1:
                        for attr in con[0]:
                            for col in cols:
                                if col.name == attr:
                                    col.is_primary = True
                                    col.is_nullable = False
                    else:
                        for i, attr in enumerate(con[0]):
                            for col in cols:
                                if col.name == attr:
                                    if not col.reference:
                                        col.reference = Reference(
                                            con[1].table,
                                            con[1].column[i],
                                            con[1].cascade,
                                        )
                                    else:
                                        raise ValueError("Constraint already defined")

                tables.append(Table(table_name, cols))

    return tables


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
  scale = 2;
  node [fontname = "Helvetica,Arial,sans-serif";];
  edge [fontname = "Helvetica,Arial,sans-serif"; len = 3;];

  subgraph relationships {{
    node [shape = diamond; fillcolor = "#7a7af3"; style = "rounded,filled"; color = black; width=1; height=1; ];

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


tables = parse_table_sql("test.sql")
relationships = extract_relationships(tables)
v = get_dot(tables, relationships)

with open("test3.dot", "w") as f:
    f.write(v)