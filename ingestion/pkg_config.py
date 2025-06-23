ALLOWED_NODE_TYPES = {"Person", "Company", "Project"}
ALLOWED_EDGE_TYPES = {"MENTIONS", "WORKS_ON", "EMPLOYED_AT"}

# Cypher constraints
SCHEMA_CONSTRAINTS = [
    "CREATE CONSTRAINT IF NOT EXISTS FOR (p:Person) REQUIRE p.email IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Company) REQUIRE c.domain IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (pr:Project) REQUIRE pr.name IS UNIQUE",
]

def install_constraints(tx):
    for stmt in SCHEMA_CONSTRAINTS:
        tx.run(stmt)
