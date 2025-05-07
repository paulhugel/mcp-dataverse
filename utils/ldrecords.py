import json
import requests
import rdflib
import re

known_keywords = {}

def split_on_and_or(text):
    # Split on ' and ' or ' or ', case-insensitive, with spaces
    parts = re.split(r'\b(and|or|-|the)\b', text, flags=re.IGNORECASE)
    
    # Group into (content, connector) pairs
    result = []
    current = ''
    for i, part in enumerate(parts):
        part = part.strip()
        if part.lower() in ['and', 'or', '-', 'the']:
#            result.append((current.strip(), part.lower()))
            if len(current.strip()) > 2:
                result.append(current.strip())
            current = ''
        else:
            current += ' ' + part
    if current.strip():
        result.append((current.strip(), None))  # Last chunk with no connector

    result.append(text)
    return result

def prepare_candidates(candidate):
    # Split the candidate string on multiple delimiters: ',', 'and', 'or', and '-'
    candidates = split_on_and_or(candidate)
    return candidates

def wikilink(conceptID, context, rankingweights='rankingweights'):
    conceptID = conceptID.replace(' ', '+')
    context = context.replace(' ', '+')
    url = 'https://sparqlmuse.now.museum/wikilink/?term=' + conceptID + '&context=' + context + '&format=json&language=en&rankingweights=' + rankingweights
    response = requests.get(url)
    data = response.json()
    print(data)
    if 'url' in data:
        url = re.search(r'(https://www.wikidata.org/wiki/.*?)\s', data['url']).group(1)
        return url
    else:
        return None

def wiki_concept_stats(conceptID, is_sparql=False):
    sparql_query = """
SELECT (COUNT(*) AS ?refCount)
WHERE {
  ?subject ?predicate wd:""" + conceptID + """ 
}
"""
    if is_sparql:
        url = 'https://query.wikidata.org/sparql'
        headers = {
            'Accept': 'application/json'
        }
        response = requests.get(url, headers=headers, params={'query': sparql_query})
    else:
        url = 'https://www.wikidata.org/w/api.php?action=wbgetentities&ids=' + query + '&format=json'
        response = requests.get(url)

    return response.json()

def graphreader(query, voc):

    for candidate in prepare_candidates(query):
        print(candidate)
        g = rdflib.Graph()
        url = 'http://10.147.18.186:8012/graph/?query=' + str(candidate) + '&format=turtle'
        try:
            response = requests.get(url)
            g.parse(data=response.text, format='turtle')
        except:
            print("Error parsing", candidate)
    
        # Dictionary to hold grouped triples by Wikidata ID
        grouped_triples = {}

        # Iterate over each triple in the graph
        for subj, pred, obj in g:
            # Convert subject to string to use as a key
            wikidata_id = str(subj)
            
            # Initialize the list if the Wikidata ID is not already in the dictionary
            if wikidata_id not in grouped_triples:
                grouped_triples[wikidata_id] = []
            
            # Append the predicate-object pair to the list for this Wikidata ID
            grouped_triples[wikidata_id].append((str(pred), str(obj)))

        for wikidata_id, triples in grouped_triples.items():
            print(wikidata_id)
            if not wikidata_id in known_keywords:
                if 'Organization' in str(triples):
                    print(triples) #['Organization'])
                    vocitem = {}
                    for triple in triples:
                        if 'label' in triple[0]:
                            thiskeyword = triple[1]
                            vocitem['https://dataverse.org/schema/citation/producerName'] = triple[1]
                        if 'type' in triple[0]:
                            vocitem['https://dataverse.org/schema/citation/producerType'] = triple[1]
                        vocitem['https://dataverse.org/schema/citation/producerURI'] = wikidata_id
                    if not thiskeyword in known_keywords:
                        voc["https://dataverse.org/schema/citation/producer"] = vocitem
                        known_keywords[thiskeyword] = True
                if 'Certification' in str(triples):
                    print(triples) #['Organization'])
                    vocitem = {}
                    for triple in triples:
                        if 'label' in triple[0]:
                            vocitem['https://dataverse.org/schema/citation/keywordValue'] = triple[1]
                            thiskeyword = triple[1]
                        if 'type' in triple[0]:
                            vocitem['https://dataverse.org/schema/citation/keywordVocabulary'] = triple[1]
                        vocitem['https://dataverse.org/schema/citation/keywordVocabularyURI'] = wikidata_id
                    if not 'https://dataverse.org/schema/citation/keyword' in voc:
                        voc["https://dataverse.org/schema/citation/keyword"] = []
                    if not thiskeyword in known_keywords:
                        voc["https://dataverse.org/schema/citation/keyword"].append(vocitem)
                        known_keywords[thiskeyword] = True
    return g, voc

def ldrecord(data, countries):
    voc = {}
    voc['http://purl.org/dc/terms/title'] = data['title']
    g, voc = graphreader(data['title'], voc)
    #print(g.serialize(format='turtle'))
    voc["https://dataverse.org/schema/core#restrictions"] = "No restrictions"
    if 'subject' in data:
        voc['http://purl.org/dc/terms/subject'] = data['subject']
    else:
        voc['http://purl.org/dc/terms/subject'] = "Medicine, Health and Life Sciences"
    creator = {}
    creator['https://dataverse.org/schema/citation/authorName'] = 'DANS' #data['authors'][0]['name']
    if 'affiliation' in data['authors'][0]:
        if isinstance(data['authors'][0]['affiliation'], list):
            creator['https://dataverse.org/schema/citation/authorAffiliation'] = data['authors'][0]['affiliation'][0]
        else:
            creator['https://dataverse.org/schema/citation/authorAffiliation'] = 'DANS' #data['authors'][0]['affiliation']
    voc['http://purl.org/dc/terms/creator'] = creator
    contact = {}
    if 'email' in data['contact']:
        contact['https://dataverse.org/schema/citation/datasetContactEmail'] = data['contact']['email']
    else:
        contact['https://dataverse.org/schema/citation/datasetContactEmail'] = 'dans@dans.knaw.nl'
    if 'name' in data['contact']:
        contact['https://dataverse.org/schema/citation/datasetContactName'] = data['contact']['name']
    voc['https://dataverse.org/schema/citation/datasetContact'] = contact
    desc = {}
    desc['https://dataverse.org/schema/citation/dsDescriptionValue'] = data['text']
    voc['https://dataverse.org/schema/citation/dsDescription'] = desc
    #if 'image' in data:
    #    voc['https://schema.org/distribution'] = data['image']
    if 'language' in data:
        if data['language'] in countries:
            voc['https://dataverse.org/schema/citation/productionPlace'] = [ countries[data['language']] ]
#    voc['http://schema.org/license#name'] = 'CC0'
    voc['http://schema.org/license'] = 'http://creativecommons.org/publicdomain/zero/1.0'
    voc['http://purl.org/dc/terms/license'] = 'CC0'
    voc['http://purl.org/dc/terms/rights'] = 'Creative Commons CC-BY 3.0 (unported) http://creativecommons.org/licenses/by/3.0/'
    voc['http://schema.org/creativeWorkStatus'] = 'RELEASED'

    keywords = []
    keyword= {}
    alltags = []
    data['tags'] = ['PDF', 'Certification']
    if 'tags' in data:
        alltags = data['tags']#.split(', ')
    else:
        tags = data['text']
        for tag in {tag.strip("#") for tag in tags.split() if tag.startswith("#")}:
            alltags.append(tag)

    for tag in alltags:
        #print(tag)
        keyword= {}
        keyword['https://dataverse.org/schema/citation/keywordValue'] = tag
        if not tag in known_keywords:
            keyword['https://dataverse.org/schema/citation/keywordTermURI'] = wikilink(tag, data['title'])
            #'http://www.wikidata.org/entity/Q42332'
            keyword['https://dataverse.org/schema/citation/keywordVocabulary'] = 'WikiData'
            keyword['https://dataverse.org/schema/citation/keywordVocabularyURI'] = 'https://www.wikidata.org/wiki/'
            if not 'https://dataverse.org/schema/citation/keyword' in voc:
                voc["https://dataverse.org/schema/citation/keyword"] = []
            voc["https://dataverse.org/schema/citation/keyword"].append(keyword)
    #keyword['https://dataverse.org/schema/citation/'] = 'covidart'
    #keywords.append(keyword)
    #keyword['https://dataverse.org/schema/citation/keywordValue'] = 'covidartmuseum'
    #keywords.append(keyword)
    if keywords:
        voc['https://dataverse.org/schema/citation/keyword'] = keywords
    return voc

if __name__ == "__main__":
    query = "2028-02-27 - DANS Data Station Archaeology in the Netherlands - CoreTrustSeal Requirements 2020-2022"
    query = "2028-03-18 - Finnish Biodiversity Information Facility - CoreTrustSeal Requirements 2023-2025"
    #query = "Finnish Biodiversity Information Facility"
    #query = "2026-04-17 - CLARINO Bergen Centre - CoreTrustSeal Requirements 2020-2022"
    query = "2027-11-29 - The CLARIN Centre at the University of Copenhagen - CoreTrustSeal Requirements 2020-2022"
    query = "Calcium carbonate and water pyrolysis measurements suggest minor adjustment to the VPDB and VSMOW-SLAP δ18O scale relation."
    g, voc = graphreader(query, {})
    print(g.serialize(format='turtle'))
    print(voc)
    for conceptID in ['Q170072', 'Q55']:
        result = wiki_concept_stats(conceptID, is_sparql=True)
        print(conceptID, result['results']['bindings'][0]['refCount']['value'])
    print(wikilink('Certification', 'Certification'))
    q = "2027-11-29 - The CLARIN Centre at the University of Copenhagen - CoreTrustSeal Requirements 2020-2022"
    print(prepare_candidates(q))