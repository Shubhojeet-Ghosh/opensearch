import os
from functools import lru_cache
from typing import List, Dict, Optional, Any

from opensearchpy import OpenSearch, RequestsHttpConnection, helpers
from requests.auth import HTTPBasicAuth


@lru_cache(maxsize=1)
def get_os_client() -> OpenSearch:
    """
    Returns a singleton OpenSearch client configured via environment variables:
      - OPENSEARCH_HOST
      - OPENSEARCH_PORT
      - OPENSEARCH_USER
      - OPENSEARCH_PASS
    """
    host = os.getenv("OPENSEARCH_HOST")
    port = int(os.getenv("OPENSEARCH_PORT", 443))
    user = os.getenv("OPENSEARCH_USER")
    password = os.getenv("OPENSEARCH_PASS")
    auth = HTTPBasicAuth(user, password)

    client = OpenSearch(
        hosts=[{"host": host, "port": port}],
        http_auth=auth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,
        timeout=30,
    )
    return client


def create_index_if_not_exists(index_name: str, mapping: dict, client: Optional[OpenSearch] = None) -> None:
    """
    Creates an index with the given mapping if it does not already exist.
    """
    client = client or get_os_client()
    if not client.indices.exists(index=index_name):
        client.indices.create(index=index_name, body=mapping)
        print(f"Created index '{index_name}'")
    else:
        print(f"Index '{index_name}' already exists.")


def bulk_index_metadata(index_name: str, docs: List[Dict], client: Optional[OpenSearch] = None) -> None:
    """
    Bulk indexes a list of metadata documents into the specified index.
    """
    client = client or get_os_client()
    actions = [
        {
            "_op_type": "index",
            "_index": index_name,
            "_id": doc.get("contract_id") or doc.get("id"),
            **doc
        }
        for doc in docs
    ]
    helpers.bulk(client, actions, refresh=True)
    print(f"Indexed {len(actions)} documents into '{index_name}'")


def query_index(
    index_name: str,
    query_body: Dict[str, Any],
    size: int = 10,
    client: Optional[OpenSearch] = None
) -> List[Dict]:
    """
    Runs a search against the specified index with a given Query DSL body.

    :param index_name: Name of the OpenSearch index.
    :param query_body: The DSL query body (e.g., filters, match_phrase, etc.).
    :param size:       Number of results to return (default: 10).
    :param client:     Optional OpenSearch client instance.
    :return:           List of hit _source dicts.
    """
    client = client or get_os_client()
    body = {"size": size, "query": query_body}
    resp = client.search(index=index_name, body=body)
    hits = resp.get("hits", {}).get("hits", [])
    return [hit.get("_source", {}) for hit in hits]


if __name__ == "__main__":
    client = get_os_client()
    # Health check
    health = client.cluster.health()
    print("Cluster Health:", health.get("status"))

    # Define index and mapping
    index_name = "contracts_meta"
    mapping = {
        "settings": {"number_of_shards": 1, "number_of_replicas": 0},
        "mappings": {
            "properties": {
                "contract_id": {"type": "keyword"},
                "title":       {"type": "text"},
                "parties":     {"type": "keyword"},
                "expiry":      {"type": "date"},
                "status":      {"type": "keyword"},
                "full_text":   {"type": "text"}
            }
        }
    }
    create_index_if_not_exists(index_name, mapping, client)

    # Sample docs
    sample_docs = [
        {"contract_id": "C-001", "title": "Alpha-Beta Agreement", "parties": ["Alpha","Beta"], "expiry": "2027-02-19", "status": "active", "full_text": "Indemnity clause applies."},
        {"contract_id": "C-002", "title": "Gamma Licence",     "parties": ["Gamma","XYZ"],  "expiry": "2026-09-30", "status": "signed","full_text": "Force majeure included."}
    ]
    bulk_index_metadata(index_name, sample_docs, client)

    # Test query: find docs containing 'indemnity'
    query = {"match_phrase": {"full_text": "indemnity"}}
    results = query_index(index_name, query, size=5, client=client)
    print("Query Results:")
    for doc in results:
        print(doc)
    print("Done.")
