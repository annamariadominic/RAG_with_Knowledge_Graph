import os
import re
import logging
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATA_PATH = "data_md"
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# Configure logging
logging.basicConfig(level=logging.INFO)

# Neo4j connection class
class Neo4jConnection:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def query(self, query, parameters=None):
        with self._driver.session() as session:
            result = session.run(query, parameters)
            return [record for record in result]

# Extract entities and relationships from Markdown
def parse_markdown(file_path):
    nodes = []
    relationships = []

    with open(file_path, 'r') as f:
        content = f.read()

    # Extract meaningful company name
    company_match = re.search(r'^\#\s*(.+)', content, re.MULTILINE)
    if company_match:
        company_name = re.sub(r'^\d+\s+', '', company_match.group(1).strip())  # Remove numerical prefixes
        nodes.append({"type": "Company", "name": company_name})
        logging.info(f"Company Found: {company_name}")

    # Extract Products
    product_matches = re.findall(r'\- Product:\s*(.+)', content)
    for product in product_matches:
        product_name = re.sub(r'^\d+\s+', '', product.strip())  # Remove numerical prefixes
        nodes.append({"type": "Product", "name": product_name})
        relationships.append({"type": "PRODUCES", "source": company_name, "target": product_name})
        logging.info(f"Product Found: {product_name}")

    # Extract Markets
    market_matches = re.findall(r'\- Market:\s*(.+)', content)
    for market in market_matches:
        market_name = re.sub(r'^\d+\s+', '', market.strip())  # Remove numerical prefixes
        nodes.append({"type": "Market", "name": market_name})
        relationships.append({"type": "OPERATES_IN", "source": company_name, "target": market_name})
        logging.info(f"Market Found: {market_name}")

    # Extract Strategies
    strategy_matches = re.findall(r'\- Strategy:\s*(.+)', content)
    for strategy in strategy_matches:
        strategy_name = re.sub(r'^\d+\s+', '', strategy.strip())  # Remove numerical prefixes
        nodes.append({"type": "Strategy", "name": strategy_name})
        relationships.append({"type": "IMPLEMENTED_BY", "source": strategy_name, "target": company_name})
        logging.info(f"Strategy Found: {strategy_name}")

    return nodes, relationships



# Process all Markdown files
def process_files(data_path):
    all_nodes = []
    all_relationships = []

    for file in os.listdir(data_path):
        if file.endswith(".md") or file.endswith(".txt"):
            file_path = os.path.join(data_path, file)
            logging.info(f"Processing file: {file_path}")
            nodes, relationships = parse_markdown(file_path)
            all_nodes.extend(nodes)
            all_relationships.extend(relationships)

    return all_nodes, all_relationships

# Generate Cypher commands dynamically
def generate_cypher(nodes, relationships):
    cypher_commands = []

    # Create nodes
    for node in nodes:
        cypher_commands.append(f'MERGE (n:{node["type"]} {{name: "{node["name"]}"}})')

    # Create relationships
    for rel in relationships:
        cypher_commands.append(f'''
            MATCH (a {{name: "{rel["source"]}"}}), (b {{name: "{rel["target"]}"}})
            MERGE (a)-[:{rel["type"]}]->(b)
        ''')

    return cypher_commands

# Insert data into Neo4j
def insert_into_neo4j(connection, commands):
    for command in commands:
        try:
            connection.query(command)
        except Exception as e:
            logging.error(f"Error executing command: {command}\n{e}")

# Main execution
if __name__ == "__main__":
    conn = Neo4jConnection(uri=NEO4J_URI, user=NEO4J_USER, password=NEO4J_PASSWORD)

    try:
        nodes, relationships = process_files(DATA_PATH)
        cypher_commands = generate_cypher(nodes, relationships)
        insert_into_neo4j(conn, cypher_commands)
        logging.info("Knowledge graph successfully updated!")
    finally:
        conn.close()




# WITHOUT ANY SCHEMA
# import os
# import re
# import logging
# from neo4j import GraphDatabase
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# DATA_PATH = "data_md"
# NEO4J_URI = os.getenv("NEO4J_URI")
# NEO4J_USER = os.getenv("NEO4J_USER")
# NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# # Configure logging
# logging.basicConfig(level=logging.INFO)

# # Neo4j connection class
# class Neo4jConnection:
#     def __init__(self, uri, user, password):
#         self._driver = GraphDatabase.driver(uri, auth=(user, password))

#     def close(self):
#         self._driver.close()

#     def query(self, query, parameters=None):
#         with self._driver.session() as session:
#             result = session.run(query, parameters)
#             return [record for record in result]

# # Extract entities and relationships from Markdown
# def parse_markdown(file_path):
#     entities = []
#     relationships = []

#     with open(file_path, 'r') as f:
#         content = f.read()

#     # Extract headers as potential node types or properties
#     headers = re.findall(r'^(#+)\s*(.+)$', content, re.MULTILINE)
#     for level, heading in headers:
#         if len(level) == 1:  # Top-level headers -> Entities
#             entities.append({"type": "Entity", "name": heading.strip()})
#         elif len(level) == 2:  # Second-level headers -> Relationships
#             relationships.append({"type": "Relationship", "name": heading.strip()})

#     # Extract bullet points as properties or connections
#     bullets = re.findall(r'^\-\s+(.+)$', content, re.MULTILINE)
#     for bullet in bullets:
#         entities.append({"type": "Property", "name": bullet.strip()})

#     return entities, relationships

# # Process all Markdown files
# def process_files(data_path):
#     all_entities = []
#     all_relationships = []

#     for file in os.listdir(data_path):
#         if file.endswith(".md") or file.endswith(".txt"):
#             file_path = os.path.join(data_path, file)
#             logging.info(f"Processing file: {file_path}")
#             entities, relationships = parse_markdown(file_path)
#             all_entities.extend(entities)
#             all_relationships.extend(relationships)

#     return all_entities, all_relationships

# # Generate Cypher commands dynamically
# def generate_cypher(entities, relationships):
#     cypher_commands = []

#     for entity in entities:
#         if entity["name"]:
#             cypher_commands.append(f'MERGE (n:{entity["type"]} {{name: "{entity["name"]}"}})')

#     for rel in relationships:
#         if rel["name"]:
#             cypher_commands.append(f'CREATE (r:Relationship {{type: "{rel["name"]}"}})')

#     return cypher_commands

# # Insert data into Neo4j
# def insert_into_neo4j(connection, commands):
#     for command in commands:
#         try:
#             connection.query(command)
#         except Exception as e:
#             logging.error(f"Error executing command: {command}\n{e}")

# # Main execution
# if __name__ == "__main__":
#     conn = Neo4jConnection(uri=NEO4J_URI, user=NEO4J_USER, password=NEO4J_PASSWORD)

#     try:
#         entities, relationships = process_files(DATA_PATH)
#         cypher_commands = generate_cypher(entities, relationships)
#         insert_into_neo4j(conn, cypher_commands)
#         logging.info("Knowledge graph successfully created!")
#     finally:
#         conn.close()
