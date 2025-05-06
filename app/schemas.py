from pydantic import BaseModel


class Node(BaseModel):
    name: str


class Edge(BaseModel):
    source: str
    target: str


class GraphCreate(BaseModel):
    nodes: list[Node]
    edges: list[Edge]


class GraphReadResponse(BaseModel):
    id: int
    nodes: list[Node]
    edges: list[Edge]

    class ConfigDict:
        orm_model = True


class GraphCreateResponse(BaseModel):
    id: int


class ValidationError(BaseModel):
    loc: list[str | int]
    msg: str
    type: str


class HTTPValidationError(BaseModel):
    detail: list[ValidationError]


class AdjacencyListResponse(BaseModel):
    adjacency_list: dict[str, list[str]]

    class ConfigDict:
        orm_model = True


class ErrorResponse(BaseModel):
    message: str
