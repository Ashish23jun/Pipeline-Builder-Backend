from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000/", "https://frontend-indol-kappa-34.vercel.app/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PipelineData(BaseModel):
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]

@app.get('/')
def read_root():
    return {'Ping': 'Pong'}

def is_dag(nodes: List[Dict], edges: List[Dict]) -> bool:
    """
    Determines if the graph is a Directed Acyclic Graph (DAG)
    Uses DFS with color-based cycle detection

    Algorithm:
    - White (0): Node not visited
    - Gray (1): Node being processed (in current DFS path)
    - Black (2): Node fully processed

    If we encounter a gray node during DFS, we found a cycle
    """

    graph = {node['id']: [] for node in nodes}

    for edge in edges:
        source = edge.get('source')
        target = edge.get('target')
        if source in graph:
            graph[source].append(target)


    colors = {node['id']: 0 for node in nodes}

    def has_cycle(node_id: str) -> bool:
        """DFS to detect cycle"""
        colors[node_id] = 1 

        for neighbor in graph.get(node_id, []):
            if neighbor not in colors:
                continue

            if colors[neighbor] == 1: 
                return True

            if colors[neighbor] == 0: 
                if has_cycle(neighbor):
                    return True

        colors[node_id] = 2  
        return False


    for node in nodes:
        if colors[node['id']] == 0: 
            if has_cycle(node['id']):
                return False 

    return True 

@app.post('/pipelines/parse')
def parse_pipeline(pipeline: PipelineData):
    """
    Parses the pipeline and returns:
    - num_nodes: Number of nodes in the pipeline
    - num_edges: Number of edges in the pipeline
    - is_dag: Whether the pipeline forms a Directed Acyclic Graph
    """
    num_nodes = len(pipeline.nodes)
    num_edges = len(pipeline.edges)
    is_dag_result = is_dag(pipeline.nodes, pipeline.edges)

    return {
        'num_nodes': num_nodes,
        'num_edges': num_edges,
        'is_dag': is_dag_result
    }
