import streamlit as st
from dotenv import load_dotenv
from neo4j import GraphDatabase
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
import os

from query_helpers import query_vector_db, query_knowledge_graph

# Load environment variables
load_dotenv()

# Neo4j credentials
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# Vector database path
CHROMA_PATH = "chroma"

# Updated LLM prompt templates
PROMPT_TEMPLATE = """
Use the following document context to answer the question. Provide a response with actionable insights and examples.

Context:
{context}
-------------------------------------------------------------
Question:
{question}
"""

KG_PROMPT_TEMPLATE = """
The following context includes broad document insights and structured knowledge graph relationships. 
Use these structured relationships to validate, refine, or enhance the broader context. Ensure the knowledge graph data adds context, nuance, and deeper understanding where relevant, but avoid prioritizing it over the broader insights unless explicitly necessary. Provide a strategic and detailed response with actionable insights and examples.

Context:
{context}
-------------------------------------------------------------
Question:
{question}
"""

DIFFERENCE_ANALYSIS_PROMPT = """
Here are two responses to the same question:

Response 1:
{response_1}

Response 2:
{response_2}

Analyze the differences between the two responses based on their approach, depth, and focus. Consider the following criteria in your analysis:

1. What type of insights each response emphasizes (e.g., specific details, broader trends, strategic context).
2. The level of detail and examples provided in each response.
3. How each response aligns with different potential use cases (e.g., operational decision-making, strategic planning, or high-level analysis).
4. Any unique strengths or perspectives in each response.

Summarize the key differences in their approach without stating which is "better." Focus on how the responses cater to different needs or use cases.
"""

class Neo4jConnection:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def query(self, query, parameters=None):
        with self._driver.session() as session:
            result = session.run(query, parameters)
            return [record for record in result]

# Generate LLM response
def generate_llm_response(context, question, is_kg=False):
    prompt_template = ChatPromptTemplate.from_template(KG_PROMPT_TEMPLATE if is_kg else PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context, question=question)
    model = ChatOpenAI()
    return model.predict(prompt)

def categorize_query(query_text):
    """
    Categorizes the query as 'specific' or 'broad' based on predefined keywords or patterns.
    """
    specific_keywords = ["sustainability goals", "specific product", "specific strategy"]
    broad_keywords = ["markets", "competitors", "strategic positioning", "overview", 'conservation', 'trend', 'trends', 'growth']
    
    # Check for specific keywords
    if any(keyword in query_text.lower() for keyword in specific_keywords):
        return "specific"
    
    # Check for broad keywords
    if any(keyword in query_text.lower() for keyword in broad_keywords):
        return "broad"
    
    # Default to 'specific' if no match
    return "specific"

def refine_query_with_kg(query_text, graph_results):
    # Extract additional keywords or phrases from the knowledge graph results
    additional_context = [f"{r['source']} -[{r['relationship']}]-> {r['target']}" for r in graph_results]
    refined_query = f"{query_text}. Also include context about: {'; '.join(additional_context)}"
    return refined_query


def combine_contexts(vector_context, graph_context):
    combined_context = (
        f"Broader Document Insights:\n{vector_context}\n\n"
        f"---\n\n"
        f"Structured Knowledge Graph Insights:\n{graph_context}\n\n"
        f"---\n\n"
        f"Use the structured relationships to validate or refine the broader insights."
    )
    return combined_context

def analyze_differences(response_1, response_2):
    prompt_template = ChatPromptTemplate.from_template(DIFFERENCE_ANALYSIS_PROMPT)
    prompt = prompt_template.format(response_1=response_1, response_2=response_2)
    model = ChatOpenAI()
    return model.predict(prompt)

def main():
    st.title("LLM Response Comparison with Dynamic KG Utilization")
    st.markdown("This app intelligently decides how to utilize the knowledge graph based on the query type.")

    if "query_text" not in st.session_state:
        st.session_state.query_text = "What are Xylem's sustainability goals?"

    col1, col2 = st.columns([3, 1])
    with col1:
        query_text = st.text_input("Enter your query", st.session_state.query_text, key="query_input")

        if st.button("Compare Responses"):
            with st.spinner("Processing your query..."):
                # Step 1: Categorize the query
                query_type = categorize_query(query_text)

                # Step 2: Query vector database
                vector_results = query_vector_db(query_text)
                vector_context = "\n\n---\n\n".join([doc.page_content for doc, _ in vector_results]) if vector_results else "No relevant documents found."

                neo4j_conn = Neo4jConnection(uri=NEO4J_URI, user=NEO4J_USER, password=NEO4J_PASSWORD)
                try:
                    if query_type == "broad":
                        # Step 3: Broad query approach: Combine KG and vector contexts directly
                        graph_results = query_knowledge_graph(neo4j_conn, query_text)
                        graph_context = "\n".join([f"Source: {r['source']} → {r['relationship']} → Target: {r['target']}" for r in graph_results]) if graph_results else "No relevant insights found."
                        combined_context = (
                            f"Broader Document Insights:\n{vector_context}\n\n"
                            f"---\n\n"
                            f"Structured Knowledge Graph Insights:\n{graph_context}\n\n"
                            f"---\n\n"
                            f"Use the structured relationships to validate or refine the broader insights."
                        )
                        response_with_kg = generate_llm_response(combined_context, query_text, is_kg=True)
                    else:
                        # Step 4: Specific query approach: Use KG to refine VB query
                        graph_results = query_knowledge_graph(neo4j_conn, query_text)
                        refined_query = refine_query_with_kg(query_text, graph_results) if graph_results else query_text
                        refined_vector_results = query_vector_db(refined_query)
                        refined_vector_context = "\n\n---\n\n".join([doc.page_content for doc, _ in refined_vector_results]) if refined_vector_results else "No relevant documents found."
                        response_with_kg = generate_llm_response(refined_vector_context, query_text, is_kg=True)
                finally:
                    neo4j_conn.close()

                # Generate response without KG
                response_without_kg = generate_llm_response(vector_context, query_text)

                # Analyze differences
                analysis = analyze_differences(response_without_kg, response_with_kg)

                # Display results
                st.subheader("Comparison Results")
                response_col1, response_col2 = st.columns(2)
                with response_col1:
                    st.subheader("Without Knowledge Graph")
                    st.write(response_without_kg)
                with response_col2:
                    st.subheader("With Knowledge Graph")
                    st.write(response_with_kg)

                st.subheader("Analysis of Differences")
                st.write(analysis)

    with col2:
        st.subheader("Example Questions")
        example_questions = [
            "What are Xylem's sustainability goals?",
            "How is North America driving growth in the water infrastructure market?",
            
            "What are the future growth opportunities for Franklin Electric?",
            "How is Franklin Electric contributing to water conservation?",
            "What products are produced by Gorman-Rupp?",
            "What strategies are implemented by Xylem?",
            "What are the major trends in the industrial pump market?",
            
            
            
        ]
        for i, question in enumerate(example_questions):
            if st.button(question, key=f"example_{i}"):
                st.session_state.query_text = question

if __name__ == "__main__":
    main()
