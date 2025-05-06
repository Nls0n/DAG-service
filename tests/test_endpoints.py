import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import Graphs
from sqlalchemy.orm import Session
from app.database import engine


client = TestClient(app)

@pytest.fixture
def last_graph_id():
    session = Session(engine)
    last_graph = session.query(Graphs).order_by(Graphs.id.desc()).first()
    session.close()
    if not last_graph:
        pytest.skip("No graphs in database")
    return last_graph.id

@pytest.mark.parametrize(
    "nodes, edges, status_code", [
        ([
             {"name": "a"},
             {"name": "b"},
             {"name": "c"},
             {"name": "d"}
         ],
         [
             {"source": "a", "target": "c"},
             {"source": "b", "target": "c"},
             {"source": "c", "target": "d"}
         ],
         201),  # Correct DAG
        ([
             {"name": "a"},
             {"name": "b"},
             {"name": "c"},
             {"name": "e"}
         ],
         [
             {"source": "a", "target": "c"},
             {"source": "b", "target": "c"},
             {"source": "c", "target": "d"}
         ],
         400  # Incorrect nodes
         ),
        ([
             {"name": "a"},
             {"name": "b"},
             {"name": "c"},
             {"name": "d"}
         ],
         [
             {"source": "a", "target": "c"},
             {"source": "b", "target": "c"},
             {"source": "c", "target": "d"},
             {"source": "c", "target": "a"}
         ],
         400  # Graph is not a DAG
         ),
        ([
             {"name": "a"},
             {"name": "b"},
             {"name": "c"},
             {"name": "1"}
         ],
         [
             {"source": "a", "target": "c"},
             {"source": "b", "target": "c"},
             {"source": "c", "target": "d"}
         ],
         400  # number in node.name. Incorrect format
         ),
        ([
             'name: a',
             'name: b',
             'name: c',
             'name: d'
         ],
         [
             {"source": "a", "target": "c"},
             {"source": "b", "target": "c"},
             {"source": "c", "target": "d"}
         ],
         422  # node names format is unprocessable
         )]
)
def test_create_graph_api_graph__post(nodes, edges, status_code):
    response = client.post('/api/graph', json={"nodes": nodes, "edges": edges})
    assert response.status_code == status_code, f'Awaited {status_code=}, real - {response.status_code}'



def generate_test_cases1(last_graph_id):
    return [
        # (path, last_graph_id, expected_status)
        ('/api/graph/', '0', 404),
        ('/api/graph/', last_graph_id, 200),
        ('/api/graph/', last_graph_id, 200),
        ('/api/graph/', '-1', 404),
        ('/api/graph/', 'a', 422),
    ]
def test_read_graph_api_graph__graph_id___get(last_graph_id):
    for path, id, status_code in generate_test_cases1(last_graph_id):
        response = client.get(f'{path}{id}/')
        assert response.status_code == status_code, f'Awaited {status_code=}, real - {response.status_code}'


def generate_test_cases2(last_graph_id):
    return [
        # (path, last_graph_id, expected_status)
        ('/api/graph/', '0', 404),
        ('/api/graph/', last_graph_id, 200),
        ('/api/graph/', last_graph_id, 200),
        ('/api/graph/', '-1', 404),
        ('/api/graph/', 'a', 422),
    ]
def test_get_adjacency_list_api_graph__graph_id__adjacency_list_get(last_graph_id):
    for path, id, status_code in generate_test_cases2(last_graph_id):
        response = client.get(f'{path}{id}/adjacency_list')
        assert response.status_code == status_code, f'Awaited {status_code=}, real - {response.status_code}'



def test_get_reverse_adjacency_list_api_graph__graph_id__reverse_adjacency_list_get(last_graph_id):
    for path, id, status_code in generate_test_cases2(last_graph_id):
        response = client.get(f'{path}{id}/reverse_adjacency_list')
        assert response.status_code == status_code, f'Awaited {status_code=}, real - {response.status_code}'



def generate_test_cases3(last_graph_id):
    return [
        # (path, graph_id, node, expected_status)
        ('/api/graph/', 'abc', 'a', 422),
        ('/api/graph/', '-1', 'a', 404),
        ('/api/graph/', '-1', 'a', 404),
        ('/api/graph/', last_graph_id, '5', 404),
        ('/api/graph/', last_graph_id, 'b', 204),
        ('/api/graph/', last_graph_id, 'c', 204),
        ('/api/graph/', last_graph_id, 'd', 204),
        ('/api/graph/', last_graph_id, 'a', 204)
    ]

def test_delete_node_api_graph__graph_id__node__node_name__delete(last_graph_id):
    for path, graph_id, node, expected_status in generate_test_cases3(last_graph_id):
        response = client.delete(f'{path}{graph_id}/node/{node}/')
        assert response.status_code == expected_status, (
            f'Awaited status {expected_status}, got {response.status_code}'
        )
