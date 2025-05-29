# OpenSearch Quick Reference

A brief overview of Amazon OpenSearch (and Elasticsearch-compatible engines), key concepts, and common terminology.

---

## What is OpenSearch?

OpenSearch is a distributed search and analytics engine, forked from Elasticsearch. It provides:

- **Full-text search** (keyword, phrase, fuzzy, wildcard)  
- **Structured queries** (term, range, geo)  
- **Aggregations & metrics** (counts, histograms, percentiles)  
- **Vector search** (k-NN / neural embeddings)  
- **Scalability & resilience** via sharding and replication  
- **Extensible plugins** for security, alerting, SQL, and more  

---

## Core Concepts & Terminology

| Concept        | What it is                                           | What we call it in SQL world     |
|----------------|------------------------------------------------------|----------------------------------|
| **Cluster**    | One or more nodes working together                   | -                                |
| **Node**       | A single JVM instance in the cluster                 | Server / instance                |
| **Index**      | A “table” of documents                               | Table                            |
| **Document**   | A single JSON object in an index                     | Row / record                     |
| **Field**      | A key/value within a document                        | Column                           |
| **Shard**      | A horizontal slice of an index (for scale)           | Partition                        |
| **Replica**    | A copy of a shard (for fault-tolerance)              | Standby / replica                |
| **Mapping**    | Schema definition for document fields                | DDL (CREATE TABLE …)             |
| **Analyzer**   | Pipeline for tokenizing & normalizing text           | Text functions + lexers          |
| **Query DSL**  | JSON-based language to express searches & filters    | SQL WHERE / JOIN / GROUP BY      |
| **Bulk API**   | Batch insert/update/delete operations                | Bulk INSERT / COPY               |
| **Scroll API** | Retrieve large result sets in sequential batches     | Cursor / OFFSET / FETCH          |

---

## Benefits of Using OpenSearch

- **Speed**: Distributed inverted index + caching  
- **Flexibility**: Schema-on-read; dynamic mappings  
- **Scalability**: Automatic sharding & replication  
- **Versatility**: Full-text, structured, and vector search in one engine  
- **Ecosystem**: Rich plugins for security, SQL, alerting, graphs  
- **Managed Options**: AWS OpenSearch Service & Serverless  

---

## Basic Operations

### 1. Create an Index

```bash
PUT /contracts_meta
{
  "settings": {
    "number_of_shards":   3,
    "number_of_replicas": 1
  },
  "mappings": {
    "properties": {
      "contract_id": { "type": "keyword" },
      "title":       { "type": "text"    },
      "expiry":      { "type": "date"    },
      "full_text":   { "type": "text"    }
    }
  }
}
