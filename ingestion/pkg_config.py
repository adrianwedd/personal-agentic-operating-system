ALLOWED_NODE_TYPES = [
    "Person",
    "Company",
    "Project",
    "Document",
]

ALLOWED_EDGE_TYPES = [
    "works_on",
    "communicates_with",
    "mentions",
]

SCHEMA_CONSTRAINTS = [
    "CREATE CONSTRAINT IF NOT EXISTS person_id FOR (p:Person) REQUIRE p.id IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS company_id FOR (c:Company) REQUIRE c.id IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS project_id FOR (p:Project) REQUIRE p.id IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS document_id FOR (d:Document) REQUIRE d.id IS UNIQUE",
]
