import os
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

# Query the vector database
def query_vector_db(query_text, chroma_path="chroma"):
    """
    Queries the vector database for relevant context based on the query text.
    """
    embedding_function = OpenAIEmbeddings()
    db = Chroma(persist_directory=chroma_path, embedding_function=embedding_function)
    results = db.similarity_search_with_relevance_scores(query_text, k=1)
    return results

# Query the knowledge graph
def query_knowledge_graph(neo4j_conn, query_text):
    cypher_query = """
    // 1. Relationships involving Companies and their Products, Markets, or Strategies
    MATCH (c:Companies)-[rel]->(n)
    RETURN c.name AS source, type(rel) AS relationship, n.name AS target
    UNION
    // 2. Relationships involving Products and Markets or End Markets
    MATCH (p:Products)-[rel]->(m:Market)
    RETURN p.name AS source, type(rel) AS relationship, m.name AS target
    UNION
    MATCH (p:Products)-[rel]->(e:End_Market)
    RETURN p.name AS source, type(rel) AS relationship, e.name AS target
    UNION
    // 3. Relationships involving Strategies and their Goals
    MATCH (s:Strategy)-[rel]->(g:Goal)
    RETURN s.name AS source, type(rel) AS relationship, g.name AS target
    UNION
    // 4. Competitor relationships between Companies
    MATCH (c1:Companies)-[rel:COMPETES_WITH]->(c2:Companies)
    RETURN c1.name AS source, type(rel) AS relationship, c2.name AS target
    UNION
    // 5. Relationships involving Companies and their Regions
    MATCH (c:Companies)-[rel]->(r:Regions)
    RETURN c.name AS source, type(rel) AS relationship, r.name AS target
    UNION
    // 6. Relationships involving Markets and Segments
    MATCH (m:Market)-[rel]->(s:Segments)
    RETURN m.name AS source, type(rel) AS relationship, s.name AS target
    UNION
    // 7. General relationships between Strategies and Companies
    MATCH (s:Strategy)-[rel:IMPLEMENTED_BY]->(c:Companies)
    RETURN s.name AS source, type(rel) AS relationship, c.name AS target
    UNION
    // 8. Contributions to Goals
    MATCH (g:Goal)-[rel:CONTRIBUTES_TO]->(e:End_Market)
    RETURN g.name AS source, type(rel) AS relationship, e.name AS target
    LIMIT 100;


    """
    results = neo4j_conn.query(cypher_query, {"query": query_text})
    return results