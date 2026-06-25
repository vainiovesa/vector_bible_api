# Vector Bible API

## What?

Vector Bible API is a REST API that provides semantic search across multiple Bible translations. Instead of relying solely on exact word or phrase matches, it uses vector embeddings and similarity search to find verses that are conceptually related to a user's query. This allows developers to build applications that find relevant scripture from topics and natural language sentences.

## Why?

Traditional Bible APIs and text searches work well when users know a specific verse reference or the exact words they are looking for, but they often struggle when the search is based on a broader concept, topic, or question. A user might search for "leadership", "anxiety", "mathematics", or even a sentence such as "How should I respond when I am worried about the future?". Relevant passages may not contain those exact words, causing conventional keyword searches to miss them. Vector Bible API is the solution to this problem.


## How to run?

Set environment variables in a local `.env` file, then run:

```bash
docker compose up --build
```

The API will be available on `http://localhost:8000`.

### Import scripts

```bash
docker compose run --rm app python scripts/import_fi_1776.py
docker compose run --rm app python scripts/import_en_kjv.py
```

## How to use?

Example request:

```
GET http://localhost:8000/closest_matches/?query=Mathematics&translation=en_kjv&book=Job&limit=3&offset=0&max_distance=0.8
```

Example response:

```json
{
  "query": "Mathematics",
  "translation": "en_kjv",
  "book": "Job",
  "limit": 3,
  "offset": 0,
  "max_distance": 0.8,
  "matches": [
    {
      "book": "Job",
      "chapter": 38,
      "verse": 5,
      "text": "Who hath laid the measures thereof, if thou knowest? or who hath stretched the line upon it?",
      "distance": 0.7540748407080997
    },
    {
      "book": "Job",
      "chapter": 37,
      "verse": 16,
      "text": "Dost thou know the balancings of the clouds, the wondrous works of him which is perfect in knowledge?",
      "distance": 0.7556383546062414
    },
    {
      "book": "Job",
      "chapter": 38,
      "verse": 18,
      "text": "Hast thou perceived the breadth of the earth? declare if thou knowest it all.",
      "distance": 0.7662918544073322
    }
  ]
}
```

| Parameter      | Type    | Required | Default | Description |
|----------------|---------|----------|---------|-------------|
| `query`        | string  | Yes      | —       | Natural language query |
| `translation`  | string  | Yes      | —       | Bible translation code (e.g. `en_kjv`, `fi_1776`) |
| `book`         | string  | No       | —       | Book from which to search |
| `limit`        | integer | No       | 5       | Maximum number of verse matches to return |
| `offset`       | integer | No       | 0       | Pagination offset |
| `max_distance` | float   | No       | 0.75    | Maximum vector distance (lower = results more similar to the query) |
