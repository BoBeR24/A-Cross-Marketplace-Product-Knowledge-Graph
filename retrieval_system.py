import json
import os
from pprint import pprint

from rdflib import Graph, SDO, Namespace, BNode, URIRef
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from sentence_transformers import CrossEncoder
from torch import sigmoid
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from transformers import logging as transformers_logging



def clear():
    print("\033[H\033[2J", end="")

def menu():
    vector_store, graph = None, None
    while True:
        choice = input("Make your choice by entering a number(you can always go back by writing `:b`):\n"
              "1. Load Graph and generate Vector Store(can take a while for large graphs)\n"
              "2. Query Graph with Similarity Search\n"
              "3. Query Graph with SPARQL\n"
              "4. Exit\n")
        clear()

        if choice == "1":
            path_to_vs = input("Path to vector store(leave blank to create a new one): ")

            if path_to_vs.strip() == ":b":
                clear()
                break

            if path_to_vs:
                vector_store, graph = load_vector_store(path_to_vs)
            else:
                graph_path = input("Enter path to your graph: ")

                if graph_path.strip() == ":b":
                    clear()
                    break

                vs_path = input("Enter path to directory where vector_store will be created(optional): ")

                if vs_path.strip() == ":b":
                    clear()
                    break

                if len(vs_path.strip()) == 0:
                    vector_store, graph = create_vector_store(graph_path)
                else:
                    vector_store, graph = create_vector_store(graph_path, vs_path)

            print("Press anything to continue...")
            input()
            clear()
            continue

        elif choice == "2":
            if vector_store is None:
                print("Vector Store not found. Load or create the Vector Store first. Press anything to continue...")
                input()
                clear()
                continue

            while True:
                query = input("Input your query: ")
                if query.strip() == ":b":
                    clear()
                    break

                results = find_semantic_match(query, vector_store)

                print_results(results)

        elif choice == "3":
            if graph is None:
                graph_path = input("Graph is not currently loaded. Specify path to the graph(leave blank to cancel):\n")
                if len(graph_path.strip()) == 0:
                    clear()
                    continue

                graph = load_graph(graph_path)

            while True:
                inp = input("Provide a path to the query file(.txt) or paste the query itself(line by line, type 'DONE' on a new line to finish):\n")
                if inp.strip() == ":b":
                    clear()
                    break

                if inp.endswith(".txt"):
                    try:
                        with open(inp, "r") as f:
                            results = graph.query(f.read())
                    except FileNotFoundError:
                        print("Query file not founded. Check the path you provided. Press anything to continue...")
                        input()
                        continue
                else:
                    lines = [inp]

                    while True:
                        line = input()
                        if line.strip() == "DONE":
                            break
                        lines.append(line)


                    query = "\n".join(lines)
                    results = graph.query(query)

                print_triples(results)
                print("Press anything to continue...")
                input()
                clear()
                break

        elif choice == "4":
            break



def load_graph(path: str) -> Graph|None:
    try:
        return Graph().parse(path)
    except FileNotFoundError:
        print("File not found. Check the path you provided")
        return None


def create_vector_store(graph_path: str, vs_save_dir: str = "./vector_store", model_name='sentence-transformers/all-mpnet-base-v2'):
    g = load_graph(graph_path)

    if not g:
        return None

    query = """
        PREFIX sdo: <https://schema.org/>
        
        SELECT ?entity ?label ?description
        WHERE
        {
        
            ?entity a sdo:Product.
            ?entity rdfs:label ?label.
            ?entity sdo:description ?description.
        }
    """

    texts_for_embedding = []
    metadata = []

    for row in g.query(query):
        entity_uri = str(row.entity)
        title = str(row.label)
        # Fallback if description is missing
        description = str(row.description) if row.description else "No description available."

        # Generate Text for Embedding (Title + Description)
        embedding_text = f"Title: {title}. Description: {description}"

        # Generate Metadata (All Triples where this entity is the subject)
        metadata_triples = []
        for s, p, o in g.triples((row.entity, None, None)):
            # Clean up the URI strings for readability
            predicate = p.split('/')[-1].split('#')[-1]
            obj = get_node_value(g, o)

            metadata_triples.append({"predicate": predicate, "object": obj})


        texts_for_embedding.append(embedding_text)
        metadata.append({
                "title": title,
                "triples": metadata_triples,
                "raw_uri": entity_uri
        })


    embedding_model = HuggingFaceEmbeddings(model_name=model_name)
    vector_store = FAISS.from_texts(texts_for_embedding, embedding=embedding_model, metadatas=metadata)

    os.makedirs(vs_save_dir, exist_ok=True)
    vector_store.save_local(vs_save_dir)

    # Save vs metadata (so we can load it later)
    meta_path = os.path.join(vs_save_dir, "graph_meta.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump({"graph_path": os.path.abspath(graph_path), "embedding_model":model_name}, f, indent=2)

    print(f"Vector store created using embedding model {embedding_model.model_name} and saved in {vs_save_dir}")

    return vector_store, g


def get_node_value(graph, node):
    """
        Handles Blank Nodes to preserve values stored in them
    """
    if isinstance(node, BNode):
        # Find all triples where this Blank Node is the subject
        sub_triples = []
        for s, p, o in graph.triples((node, None, None)):
            p_name = p.split('/')[-1].split('#')[-1]
            o_val = get_node_value(graph, o)  # Recursive call
            sub_triples.append(f"{p_name}: {o_val}")
        return "[" + ", ".join(sub_triples) + "]"

    else:
        return node


def load_vector_store(path_to_dir: str):
    meta_path = os.path.join(path_to_dir, "graph_meta.json")
    try:
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
            embedding_name = meta.get("embedding_model")
            if embedding_name is None:
                raise ValueError("Embedding model name must be provided in meta file")
    except FileNotFoundError:
        print("Vector Store was not found under specified path")
        return None, None

    embedding_model = HuggingFaceEmbeddings(model_name=embedding_name)
    vector_store = FAISS.load_local(path_to_dir, embedding_model, allow_dangerous_deserialization=True)
    print(f"Loaded FAISS index from {path_to_dir} using embedding model {embedding_name}")

    g = Graph().parse(meta.get("graph_path"))
    print(f"Loaded the graph from {meta.get("graph_path")}")

    return vector_store, g


def find_semantic_match(query: str, vector_store, top_k=3, cross_encoder_name='cross-encoder/ms-marco-MiniLM-L-6-v2'):
    results = vector_store.similarity_search(query, k=10)
    re_ranker = CrossEncoder(cross_encoder_name, activation_fn=sigmoid)

    pairs = [[query, r.page_content] for r in results]
    scores = re_ranker.predict(pairs)

    # Pair results with their new scores and sort
    scored_results = sorted(zip(results, scores), key=lambda x: x[1], reverse=True)

    return scored_results[:min(top_k, 10)]


def print_results(results):
    """
    Prints results from similarity search in a readable format
    :param results:
    :return:
    """
    console = Console()

    for i, (result, score) in enumerate(results, 1):
        meta = result.metadata

        # Create a table for the specs
        table = Table(show_header=True, header_style="bold magenta", box=None, padding=(0, 1))
        table.add_column("Property", width=20, style="cyan")
        table.add_column("Value", max_width=60)

        for t in meta.get("triples", []):
            val = t['object']
            # If it's a BNode string, make it look like a sub-list
            if val.startswith("[") and val.endswith("]"):
                val = "• " + val[1:-1].replace(", ", "\n• ")

            table.add_row(t['predicate'], val)

        # Wrap everything in a nice Panel
        header_info = f"[bold white]Product:[/bold white] {meta.get('title')}\n"
        header_info += f"[dim]URI: {meta.get('raw_uri')}[/dim]\n"
        header_info += f"[bold green]Score: {score:.4f}[/bold green]"

        console.print(Panel(table, title=f"Result #{i}", subtitle="Knowledge Graph Metadata", expand=False))

def print_triples(results):
    """
    Prints triples received from SPARQL query
    :param results:
    :return:
    """

    for result in results:
        # print(result.labels, result.description)
        for label in result.labels:
            pprint(f"{str(label)}: {str(result.get(label))}", width=60)

        print("-"*100)


if __name__ == "__main__":
    transformers_logging.set_verbosity_error()

    menu()