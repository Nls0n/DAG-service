from fastapi import FastAPI, status, Depends, Response
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session, joinedload
from .database import engine, get_db, Base
from . import schemas
from .models import Graphs, Nodes, Edges
from .utils import *

app = FastAPI()

Base.metadata.create_all(bind=engine)


@app.get('/')
def root():
    return 'Выполненное тестовое задание'


@app.post('/api/graph', status_code=status.HTTP_201_CREATED, response_model=schemas.GraphCreateResponse)
def create_graph_api_graph__post(data: schemas.GraphCreate, db: Session = Depends(get_db)):
    """Ручка для создания графа, принимает граф в виде списка вершин и списка ребер."""
    graph = Graphs()
    nodes = {}
    if all([validate_nodes(data), validate_edges(data)]):
        if all([validate_graph(data), is_DAG(data)]):
            for node_data in data.nodes:
                node = Nodes(name=node_data.name, graph=graph)
                nodes[node_data.name] = node.name
            for edge_data in data.edges:
                source_node = nodes[edge_data.source]
                target_node = nodes[edge_data.target]
                edge = Edges(graph=graph, source=source_node, target=target_node)
                db.add(edge)
            db.add(graph)
            db.commit()
            db.refresh(graph)
            return graph
        else:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                                content=jsonable_encoder(
                                    schemas.ErrorResponse(message='Failed to add graph. It is not a DAG')))
    else:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content=jsonable_encoder(
                                schemas.ErrorResponse(message='Failed to add graph. Nodes do not follow the rules')))


@app.get('/api/graph/{graph_id}/', status_code=status.HTTP_200_OK, response_model=schemas.GraphReadResponse)
def read_graph_api_graph__graph_id___get(graph_id: int, db: Session = Depends(get_db)):
    """Ручка для чтения графа в виде списка вершин и списка ребер."""
    graph = db.query(Graphs).options(joinedload(Graphs.nodes), joinedload(Graphs.edges)).filter(
        Graphs.id == graph_id).first()

    if not graph:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content=jsonable_encoder(
                                schemas.ErrorResponse(message=f'Graph entity with id {graph_id} not found')))

    return schemas.GraphReadResponse(id=graph_id, nodes=[schemas.Node(name=node.name) for node in graph.nodes],
                                     edges=[schemas.Edge(source=edge.source,
                                                         target=edge.target) for edge in graph.edges])


@app.get('/api/graph/{graph_id}/adjacency_list', status_code=status.HTTP_200_OK,
         response_model=schemas.AdjacencyListResponse)
def get_adjacency_list_api_graph__graph_id__adjacency_list_get(graph_id: int, db: Session = Depends(get_db)):
    """
    Ручка для чтения графа в виде списка смежности.
    Список смежности представлен в виде пар ключ - значение, где
    - ключ - имя вершины графа,
    - значение - список имен всех смежных вершин (всех потомков ключа).
    """
    graph = db.query(Graphs).options(joinedload(Graphs.nodes), joinedload(Graphs.edges)).filter(
        Graphs.id == graph_id).first()
    if not graph:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=jsonable_encoder(
            schemas.ErrorResponse(message=f'Graph entity with id {graph_id} not found')))
    adjacency_list = adjacency_list_from_graph(graph)
    return schemas.AdjacencyListResponse(adjacency_list=adjacency_list)


@app.get('/api/graph/{graph_id}/reverse_adjacency_list', status_code=status.HTTP_200_OK,
         response_model=schemas.AdjacencyListResponse)
def get_reverse_adjacency_list_api_graph__graph_id__reverse_adjacency_list_get(graph_id: int,
                                                                               db: Session = Depends(get_db)):
    """
    Ручка для чтения транспонированного графа в виде списка смежности.
    Список смежности представлен в виде пар ключ - значение, где
    - ключ - имя вершины графа,
    - значение - список имен всех смежных вершин (всех предков ключа в исходном графе).
    """
    graph = db.query(Graphs).options(joinedload(Graphs.nodes), joinedload(Graphs.edges)).filter(
        Graphs.id == graph_id).first()

    if not graph:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=jsonable_encoder(
            schemas.ErrorResponse(message=f'Graph entity with id {graph_id} not found')))

    transposed_adjacency_list = reversed_adjacency_list_from_graph(graph)
    return schemas.AdjacencyListResponse(adjacency_list=transposed_adjacency_list)


@app.delete('/api/graph/{graph_id}/node/{node_name}', status_code=status.HTTP_204_NO_CONTENT)
def delete_node_api_graph__graph_id__node__node_name__delete(graph_id: int, node_name: str,
                                                             db: Session = Depends(get_db)):
    """Ручка для удаления вершины из графа по ее имени."""
    graph = db.query(Graphs).filter(Graphs.id == graph_id).first()
    if not graph:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content=jsonable_encoder(
                                schemas.ErrorResponse(message=f'Graph entity with id {graph_id} not found')))
    if node_name not in map(lambda x: x.name, graph.nodes):
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content=jsonable_encoder(schemas.ErrorResponse(
                                message=f'In graph with id {graph_id}, node with name {node_name} not found')))
    db.query(Nodes).filter((Nodes.name == node_name) & (Nodes.graph_id == graph_id)).delete()

    db.query(Edges).filter(
        ((Edges.source == node_name) | (Edges.target == node_name)) & (Edges.graph_id == graph_id)).delete()

    db.commit()

    graph = db.query(Graphs).filter(Graphs.id == graph_id).first()

    if not graph.nodes:
        db.delete(graph)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


