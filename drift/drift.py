# DRIFT is Decentralized Resource Identity & Trust Framework created by Slava Tykhonov (https://github.com/4tykhonov) 
# DRIFT is a decentralized identity and trust layer that propagates traceable context — like sessions, prompts, user metadata, and spans — across AI tools and services in event-driven environments like Model Context Protocol (MCP).
# Features:
# Assigning DIDs to all entities (sessions, prompts, users, tools)
# Using public/private key cryptography for signing/verifying events
# Providing a consistent metadata structure for events and services
# Supporting verifiable logs and lineage in distributed systems

import requests
import json
from datetime import datetime
from dotenv import load_dotenv
import os
import json
import requests
import uuid
import logging
import re
import ollama
from primitives import entities
from rdflib import Graph, BNode, URIRef, RDF, Namespace, Literal, SKOS, OWL
import random

class InfraDID:
    def __init__(self, DID_url):
        self.DID_url = f"{DID_url}/1.0/create?method=oyd"
        self.headers = {'content-type': 'application/json'}
        self.collection = None
        self.session_id = None
        self.endpoint = None
        self.model = None
        self.compute_time = None
        self.confidence = None
        self.source = None
        self.type = None
        self.value = None
        self.query = None
        self.result = None
        self.structured_result = None
        self.prompt = None
        self.metadata = None
        self.language = None
        self.datasets = {}
        self.datetime = datetime.now()
        self.start_datetime = None
        self.end_datetime = None
        self.tags = []
        self.prompt = None
        self.sparqlmuse_url = None

        self.result = """
        [{'Type': 'Person', 'Value': 'Don Felder'}, {'Type': 'Person', 'Value': 'Don Henley'}, {'Type': 'Person', 'Value': 'Glenn Frey'}, {'Type': 'Categories', 'Value': 'Music'}, {'Type': 'Categories', 'Value': 'Song'}, {'Type': 'Item', 'Value': 'Eagles'}, {'Type': 'Time', 'Value': '1976'}]
        """

        self.q = """
        song written and composed by Don Felder, Don Henley and Glenn Frey; originally recorded by Eagles and released 1976
        """

    def recognize_parameters(self, parameters):
        # Function to replace placeholders in the prompt
        def replace_placeholder(match):
            key = match.group(1)  # Get the parameter name without the braces
            return parameters.get(key, f"{{{{{key}}}}}")  # Return the value or the original placeholder if not found

        # Use regex to find all {{parameter}} patterns
        self.prompt = re.sub(r'\{\{(.*?)\}\}', replace_placeholder, self.prompt)
        return self.prompt

    def create_payload(self):
        data = {}
        did_document = { "datetime": self.datetime }
        if self.collection:
            did_document["collection"] = self.collection
        if self.session_id:
            did_document["session_id"] = self.session_id
        if self.endpoint:
            did_document["endpoint"] = self.endpoint
        if self.model:
            did_document["model"] = self.model
        if self.compute_time:
            did_document["compute_time"] = self.compute_time
        if self.confidence:
            did_document["confidence"] = self.confidence
        if self.source:
            did_document["source"] = self.source
        if self.type:
            did_document["type"] = self.type
        if self.value:
            did_document["value"] = self.value
        if self.query:
            did_document["query"] = self.query
        if self.result:
            did_document["result"] = self.result
        if self.query:
            did_document["query"] = self.query
        if self.prompt:
            did_document["resource"] = self.prompt
        if self.result:
            did_document["result"] = self.result
        if self.model:
            did_document["model"] = self.model
        if self.endpoint:
            did_document["endpoint"] = self.endpoint
        if self.metadata:
            did_document["metadata"] = self.metadata
        if self.language:
            did_document["language"] = self.language
        if self.datasets:
            did_document["datasets"] = self.datasets
        if self.tags:
            did_document["tags"] = self.tags
        data['didDocument'] = did_document 
        return json.dumps(data)

    # MCP primitives registry
    def register_tool(self, tool_name, tool_description, tool_parameters):
        self.tools[tool_name] = {
            "description": tool_description,
            "parameters": tool_parameters
        }
        return self

    def register_dataset(self, dataset_name, dataset_description, dataset_parameters):
        self.datasets[dataset_name] = {
            "description": dataset_description,
            "parameters": dataset_parameters
        }
        return self
    
    def register_model(self, model_name, model_description, model_parameters):
        self.models[model_name] = {
            "description": model_description,
            "parameters": model_parameters
        }
        return self

    def register_prompt(self, prompt_name, prompt_description, prompt_provenance, variables):
        self.prompts[prompt_name] = {
            "description": prompt_description,
            "provenance": prompt_provenance,
            "variables": variables
        }
        return self

    def load_prompt(self, prompt_file):
        with open(prompt_file, 'r') as file:
            self.prompt = file.read()
            if self.query:
                self.prompt = self.recognize_parameters({"query": self.query})
        return self.prompt

    def get_prompt(self):
        return self.prompt

    def set_session_id(self, session_id):
        self.session_id = session_id
        return self

    def set_model(self, model):
        self.model = model
        return self

    def set_compute_time(self, compute_time):
        self.compute_time = compute_time
        return self

    def set_confidence(self, confidence):
        self.confidence = confidence
        return self

    def set_endpoint(self, endpoint):
        self.endpoint = endpoint
        return self

    def set_source(self, source):
        self.source = source
        return self

    def create_did(self):
        payload = str(self.create_payload())
        r = requests.post(self.DID_url, data=payload, headers=self.headers)
        return r.text

    def set_start_datetime(self):
        self.start_datetime = datetime.now()
        return self

    def set_end_datetime(self):
        self.end_datetime = datetime.now()
        return self

    def set_sparqlmuse(self, sparqlmuse_url):
        self.sparqlmuse_url = sparqlmuse_url
        return self

    def get_compute_time(self):
        if not self.end_datetime:
            self.end_datetime = datetime.now()
        self.compute_time = self.end_datetime - self.start_datetime
        self.compute_time = self.compute_time.total_seconds()
        return self.compute_time

    def set_prompt(self, prompt):
        self.prompt = prompt
        return self

    def set_prompt(self, prompt):
        self.prompt = prompt
        return self

    def set_query(self, q):
        self.query = q
        return self

    def set_result(self, result):
        self.result = result
        return self

    def set_model(self, model):
        self.model_name = model
        return self

    def set_datetime(self, datetime):
        self.datetime = datetime
        return self

    def set_headers(self, headers):
        self.headers = headers
        return self

    def set_DID_url(self, DID_url):
        self.DID_url = DID_url
        return self

    def get_did(self):
        return self.create_did()

    def get_model(self):
        return self.model_name

    def get_structured_result(self):
        return self.structured_result

    def print_structured_result(self):
        return json.dumps(self.structured_result, indent=4)

    def set_structured_result(self, structured_result):
        self.structured_result = structured_result
        return self

class InfraModel:
    def __init__(self, did):
        self.did = did
        self.endpoint = did.endpoint
        self.model_name = did.model_name
        self.primitives = {}
        self.context = []
        self.schema_context = {} 

    def query_ollama(self, prompt):
        s = requests.Session()
        output=''
        self.did.set_start_datetime()
        with s.post("%s/api/generate" % self.endpoint, json={'model': self.model_name, 'prompt': prompt}, stream=True) as r:
            for line in r.iter_lines():
                if line:
                    j = json.loads(line)
                    if "response" in j:
                        output = output +j["response"]
            print(output)
            self.structured_result = self.get_structured_result(output)
            self.did.set_structured_result(self.structured_result)
            self.did.set_end_datetime()
            self.did.get_compute_time()
            return output

    def get_model(self):
        return self.model

    def get_primitives(self):
        for primitive_name in entities:
            #    "PART OF BODY": {
            #      "alias": [ "part", "body", "organ", "organism", "organism"],
            #      "description": "Parts of the body, organs, organisms, organisms",
            #      "relationship": "PART OF BODY"
            #    },
            primitive_uri = f"https://schema.org/{primitive_name.replace(' ', '_').lower()}"
            print(primitive_uri)
            for alias in entities[primitive_name]["alias"]:
                self.primitives[alias.lower()] = primitive_uri
            if "keywords" in entities[primitive_name]:
                self.schema_context[primitive_name.lower()] = entities[primitive_name]["keywords"]
            #else:
            #    self.schema_context[primitive_name] = entities[primitive_name]["alias"]
        return self.primitives

    def set_ontology(self, result):
        self.primitives = self.get_primitives()
        print(self.primitives)
        enriched_result = []
        for entity in result:
            if entity["Type"].lower() in self.primitives:
                entity["uri"] = self.primitives[entity["Type"].lower()]
            #else:
            #    entity["uri"] = f"https://schema.org/{entity['Type'].lower()}"
            enriched_result.append(entity)
        return enriched_result

    def get_structured_result(self, response_text, DEBUG=False):
        self.DEBUG = False
        if DEBUG:
            self.DEBUG = DEBUG
        """
        Extract CSV data from the LLM response text and convert to a list of dictionaries.
        """
        if self.DEBUG:
            print("\nDebug - Original response:", response_text)

        # Find CSV content in the response (between possible markdown code blocks)
        csv_content = response_text.strip()

        # Check if the response is wrapped in markdown code blocks
        if "```csv" in response_text:
            start_idx = response_text.find("```csv") + 6
            end_idx = response_text.find("```", start_idx)
            if end_idx != -1:
                csv_content = response_text[start_idx:end_idx].strip()
        elif "```" in response_text:
            start_idx = response_text.find("```") + 3
            end_idx = response_text.find("```", start_idx)
            if end_idx != -1:
                csv_content = response_text[start_idx:end_idx].strip()
        if self.DEBUG:
            print("\nDebug - CSV content after extraction:", csv_content)
        # Parse CSV data
        entities = []
        try:
            # Simple line-by-line parsing
            lines = [line.strip() for line in csv_content.split('\n') if line.strip()]

            # If first line doesn't contain header, add it
            if lines and not ('Type' in lines[0] and 'Value' in lines[0]):
                lines.insert(0, "Type,Value")

            # Parse each line manually
            header = lines[0].split(',')
            for line in lines[1:]:
                parts = line.split(',', 2)  # Split only on first comma
                if len(parts) == 3:
                    entities.append({
                        'Type': parts[0].strip(),
                        'Value': parts[1].strip().replace('"', '')
                    })
                    self.context.append(parts[1].strip().replace('"', ''))
                elif len(parts) == 2:
                    entities.append({
                        'Type': parts[0].strip(),
                        'Value': parts[1].strip().replace('"', '')
                    })
                    self.context.append(parts[1].strip().replace('"', ''))
                else:
                    print(f"Error parsing: {line}")

            if self.DEBUG:
                print("\nDebug - Parsed entities:", entities)

        except Exception as e:
            if self.DEBUG:
                print(f"Error parsing: {e}")

        return entities

    def get_ontology(self, q=False, uid=1):
        g = Graph()
        SPARQLMUSE = False
        if self.did.sparqlmuse_url:
            SPARQLMUSE = True
        g.bind("schema", "https://schema.org/")
        bnode = BNode()
        g.add((bnode, RDF.type, SKOS.Concept))
        if q:   
            g.add((bnode, SKOS.note, Literal(q)))
        #g.add((bnode, SKOS.prefLabel, Literal(f"Block {uid}")))
        for element in self.structured_result:
            conceptURI = None
            print(element)
            #{'Type': 'Person', 'Value': 'Edward Witten', 'uri': 'https://schema.org/person'}
            #s, p, o = rdflib.URIRef(element["uri"]), rdflib.RDF.type, rdflib.URIRef(element["Value"])
            if 'uri' in element:
                subject = URIRef(element["uri"].replace(' ', '_'))
                rdf_type = URIRef(f"https://schema.org/{element['Type'].replace(' ', '_')}")  # e.g., schema:Person
                bnode_int = BNode() 
                if SPARQLMUSE:
                    self.main_context = self.context
                    if element["Type"].lower() in self.schema_context:
                        self.main_context = self.schema_context[element["Type"].lower()]
                    concept = self.get_sparqlmuse_concept(element["Value"], self.main_context)
                    if concept:
                        conceptURI = URIRef(concept['uri'])
                        g.add((bnode_int, SKOS.closeMatch, conceptURI))
                        g.add((bnode_int, SKOS.altLabel, Literal(concept['label'])))
                g.add((bnode, subject, bnode_int))
                #g.add((subject, RDF.type, rdf_type))
                #g.add((subject, SKOS.closeMatch, bnode_int))
                g.add((bnode_int, SKOS.hiddenLabel, Literal(element["Value"])))
                #g.add((bnode_int, SKOS.altLabel, Literal(element["Value"]))) 
                if conceptURI:
                    g.add((bnode_int, SKOS.closeMatch, conceptURI))
            else:
                print(f"No URI found for {element}")
#            g.add((s, p, o)) 
        g.serialize(destination="ontology.ttl", format="turtle")
        return g

    def get_sparqlmuse_concept(self, term, context, language="en", format="json"):
        extraquery = '%20'.join(context)
        term = term.replace(' ', '%20')
        url = f"{self.did.sparqlmuse_url}/wikilink/?term={term}&context={extraquery}&language={language}&format={format}"
        print(f"sparqlmuse url: {url}")
        try:
            r = requests.get(url)
            if 'url' in r.json():
                concept = {}
            concept['uri'] = r.json()['url']
            concept['label'] = r.json()['label']
            return concept
        except Exception as e:
            print(f"Error getting sparqlmuse concept: {e}")
            return None

# Run tests
if __name__ == "__main__":
    did = InfraDID(DID_url)
    query = "Welcome to Dataverse®, the open source software platform designed for sharing, finding, citing, and preserving research data. Developed by the Dataverse team at the Institute for Quantitative Social Science and the Dataverse community, our platform makes it easy for research organizations to host, manage, and share their data with the world."
    did.set_query(query)
    did.set_model("gemma3:4b")
    print(did.compute_time)
    did.set_endpoint(ollama_url)
    did.set_sparqlmuse(sparqlmuse_url)
    did.load_prompt("utils/prompts/nlp_gemma4b.txt")
    print(did.get_prompt())
    #print(did.create_did())
    infra = InfraModel(did)
    infra.query_ollama(did.get_prompt())
    infra.set_ontology(did.get_structured_result())
    print(infra.get_primitives())
    print(did.print_structured_result())
    print(did.compute_time)
    print(infra.get_ontology(query))
    print(' '.join(infra.context))
    print(infra.schema_context)
