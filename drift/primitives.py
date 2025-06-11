entities = {
    "PERSON": {
      "alias": [ "human", "person"],
      "description": "People, including fictional characters",
      "relationship": "PERSON",
      "crosswalks": "authorName, authorAffiliation"
    },
    "NORP": {
      "alias": [ "nationality", "religion", "political group"],
      "description": "Nationalities or religious or political groups",
      "relationship": "NORP"
    },
    "FAC": {
      "alias": [ "building", "airport", "highway", "bridge", "facility"],
      "description": "Buildings, airports, highways, bridges, etc.",
      "relationship": "FAC"
    },
    "ORG": {
      "alias": [ "company", "agency", "institution", "organization"],
      "description": "Companies, agencies, institutions, etc.",
      "relationship": "ORG",
      "crosswalks": "authorName, authorAffiliation"
    },
    "GPE": {
      "alias": [ "country", "city", "state"],
      "keywords": ["place", "address", "city", "state", "country"],
      "description": "Countries, cities, states",
      "relationship": "GPE",
      "crosswalks": "locations"
    },
    "LOC": {
      "alias": [ "mountain", "river", "lake", "sea", "location"],
      "description": "Non-GPE locations, mountain ranges, bodies of water",
      "relationship": "LOC",
      "crosswalks": "locations"
    },
    "PRODUCT": {
      "alias": [ "product", "service", "item", "thing", "brand", "supplier"],
      "description": "Objects, vehicles, foods, etc. (not services)",
      "relationship": "PRODUCT"
    },
    "EVENT": {
      "alias": [ "hurricane", "battle", "war", "sport", "event"],
      "description": "Named hurricanes, battles, wars, sports events",
      "relationship": "EVENT"
    },
    "WORK_OF_ART": {
      "alias": [ "book", "song", "artwork", "movie", "play", "work"],
      "description": "Titles of books, songs, artworks, etc.",
      "relationship": "WORK_OF_ART"
    },
    "LAW": {
      "alias": [ "law", "regulation", "policy", "rule"],
      "description": "Named documents made into laws",
      "relationship": "LAW"
    },
    "LANGUAGE": {
      "alias": [ "language", "language", "language"],
      "description": "Any named language",
      "relationship": "LANGUAGE"
    },
    "DATE": {
      "alias": [ "date", "time", "period", "timeframe"],
      "description": "Absolute or relative dates or periods",
      "relationship": "DATE",
      "crosswalks": "date",
      "crosswalks": "dsPublicationDate"
    },
    "TIME": { 
      "alias": [ "time", "period"],
      "description": "Times smaller than a day",
      "relationship": "TIME",
      "crosswalks": "dsPublicationDate"
    },
    "PERCENT": {
      "alias": [ "percentage", "percent", "percentage"],
      "description": "Percentage (e.g., 20%)",
      "relationship": "PERCENT"
    },
    "MONEY": {
      "alias": [ "money", "currency", "price", "cost"],
      "description": "Monetary values, including unit",
      "relationship": "MONEY"
    },
    "QUANTITY": {
      "alias": [ "quantity", "amount", "size", "number"],
      "description": "Measurements, as of weight or distance",
      "relationship": "QUANTITY"
    },
    "ORDINAL": {
      "alias": [ "first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth"],
      "description": "'First', 'second', etc.",
      "relationship": "ORDINAL"
    },
    "CARDINAL": {
      "alias": [ "first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth"],
      "description": "Numerals that do not fall under another type",
      "relationship": "CARDINAL"
    },
    "PROGRAM": {
      "alias": [ "program", "project", "task", "activity"],
      "description": "Programs, projects, tasks, activities",
      "relationship": "PROGRAM"
    },
    "ACTION": {
      "alias": [ "action", "activity", "task", "procedure", "method", "algorithm"],
      "keywords": [ "action", "skill", "activity", "performing"],
      "description": "Actions, activities, tasks, procedures, methods, algorithms",
      "relationship": "ACTION"
    },
    "SCALAR": {
      "alias": [ "scalar", "number", "value", "measurement", "scale"],
      "description": "Scalar values, such as temperature, weight, or distance",
      "relationship": "SCALAR"
    },
    "PROCESS": {
      "alias": [ "process", "procedure", "method", "algorithm"],
      "description": "Processes, procedures, methods, algorithms",
      "relationship": "PROCESS"
    },
    "EVENT": {
      "alias": [ "events", "event", "occurrence", "incident", "accident"],
      "description": "Events, occurrences, incidents, accidents",
      "relationship": "EVENT"
    },
    "MOVIE": {
      "alias": [ "movie", "film", "video"],
      "keywords": [ "movie", "film", "video"],
      "description": "Movies, films, videos",
      "relationship": "MOVIE"
    },
    "WORK_OF_ART": {
      "alias": [ "book", "song", "artwork", "play", "work"],
      "description": "Titles of books, songs, artworks, etc.",
      "relationship": "WORK_OF_ART"
    },
    "METRIC": {
      "alias": [ "metric", "measurement", "scale", "unit", "metric", "measurement", "scale", "unit"],
      "description": "Metrics, measurements, scales, units",
      "relationship": "METRIC"
    },
    "ROLE": {
      "alias": [ "role", "position", "job", "title"],
      "description": "Roles, positions, jobs, titles",
      "relationship": "ROLE"
    },
    "ITEM": {
      "alias": [ "item", "thing", "object", "product", "service"],
      "description": "Items, things, objects, products, services",
      "relationship": "ITEM"
    },
    "QUESTION": {
      "alias": [ "question", "query", "inquiry", "request"],
      "description": "Questions, queries, inquiries, requests",
      "relationship": "QUESTION"
    },
    "ORGANIZATION": {
      "alias": [ "organization", "company", "agency", "institution", "organization"],
      "description": "Organizations, companies, agencies, institutions, etc.",
      "relationship": "ORGANIZATION"
    },
    "LEVEL": {
      "alias": [ "level", "grade", "rank", "class", "category", "categories"],
      "keywords": [ "science", "discipline", "grade"],
      "description": "Levels, grades, ranks, classes, categories",
      "relationship": "LEVEL"
    },
    "LOCATION": {
      "alias": [ "location", "place", "address", "city", "state", "country"],
      "keywords": ["place", "address", "city", "state", "country"],
      "description": "Locations, places, addresses, cities, states, countries",
      "relationship": "LOCATION"
    },
    "COUNTRY": {
      "alias": [ "country", "country", "country", "country", "country"],
      "keywords": ["place", "address", "city", "state", "country"],
      "description": "Countries, cities, states",
      "relationship": "COUNTRY"
    },
    "SCORE": {
      "alias": [ "score", "score", "score", "score", "score"],
      "keywords": ["result", "scored", "match", "points"],
      "description": "Scores, scores, scores, scores, scores",
      "relationship": "SCORE"
    },
    "DATE": {
      "alias": [ "date", "time", "period"],
      "description": "Absolute or relative dates or periods",
      "relationship": "DATE",
      "crosswalks": "date",
      "crosswalks": "dsPublicationDate"
    },
    "PART OF BODY": {
      "alias": [ "part of body", "part", "body", "organ", "organism", "organism"],
      "description": "Parts of the body, organs, organisms, organisms",
      "relationship": "PART OF BODY"
    },
    "BIOLOGICAL SUBSTANCE": {
      "alias": [ "substance", "material", "object", "product", "service"],
      "description": "Substances, materials, objects, products, services",
      "relationship": "BIOLOGICAL SUBSTANCE"
    },
    "ATLAS": {
      "alias": [ "atlas", "map", "chart", "diagram", "graph"],
      "description": "Atlases, maps, charts, diagrams, graphs",
      "relationship": "ATLAS"
    },
    "DATASET": {
      "alias": [ "dataset", "database", "collection", "set", "data"],
      "description": "Datasets, databases, collections, sets, data",
      "relationship": "DATASET"
    },
    "MODEL": {
      "alias": [ "model", "model", "model", "model", "model"],
      "description": "Models, models, models, models, models",
      "relationship": "MODEL"
    },
    "PROMPT": {
      "alias": [ "prompt", "prompt", "prompt", "prompt", "prompt"],
      "description": "Prompts, prompts, prompts, prompts, prompts",
      "relationship": "PROMPT"
    },
    "TOPIC": {
      "alias": [ "topic", "topic", "topic", "topic", "topic"],
      "description": "Topics, topics, topics, topics, topics",
      "relationship": "TOPIC"
    },
    "FRAMEWORK": {
      "alias": [ "framework", "framework", "framework", "framework", "framework"],
      "description": "Frameworks, frameworks, frameworks, frameworks, frameworks",
      "relationship": "FRAMEWORK"
    },
    "PROFESSION": {
      "alias": [ "profession", "profession", "profession", "profession", "profession"],
      "keywords": [ "science", "activity"],
      "description": "Professions, professions, professions, professions, professions",
      "relationship": "PROFESSION"
    },
    "SOURCE": {
      "alias": [ "source", "sources"],
      "description": "Sources, sources, sources, sources, sources",
      "relationship": "SOURCE"
    },
    "TARGET": {
      "alias": [ "target", "target", "target", "target", "target"],
      "description": "Targets, targets, targets, targets, targets",
      "relationship": "TARGET"
    },
    "ARTICLE": {
      "alias": [ "article", "articles", "legal document", "website", "webpage", "legaldocument"],
      "description": "Articles, articles, legal documents",
      "relationship": "ARTICLE"
    },
    "PROTOCOL": {
      "alias": [ "protocol", "protocol", "network", "network", "network"],
      "description": "Protocols, protocols, networks, networks, networks",
      "relationship": "PROTOCOL"
    }
}
