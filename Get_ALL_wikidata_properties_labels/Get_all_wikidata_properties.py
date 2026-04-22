# pip install sparqlwrapper pandas

import time
import pandas as pd
from SPARQLWrapper import SPARQLWrapper, JSON

endpoint_url = "https://query.wikidata.org/sparql"

def get_results(query):
    sparql = SPARQLWrapper(endpoint_url, agent="PropertyCollectorBot/1.0 (Python)")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()

LIMIT = 500
offset = 0
all_rows = []

while True:
    print(f"Fetching properties OFFSET={offset}")

    query = f"""
    SELECT DISTINCT ?property ?propertyLabel WHERE {{
      ?property a wikibase:Property .
      SERVICE wikibase:label {{
        bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en".
      }}
    }}
    ORDER BY ?property
    LIMIT {LIMIT}
    OFFSET {offset}
    """

    results = get_results(query)
    bindings = results["results"]["bindings"]

    if not bindings:
        break

    for result in bindings:
        prop_id = result["property"]["value"].split("/")[-1]
        prop_label = result.get("propertyLabel", {}).get("value", None)

        all_rows.append({
            "property": prop_id,
            "propertyLabel": prop_label
        })

    if len(bindings) < LIMIT:
        break

    offset += LIMIT
    time.sleep(1)

df = pd.DataFrame(all_rows).drop_duplicates(subset=["property"])
df.to_csv("ALL_wikidata_properties_labels.csv", sep=";", index=False, encoding="utf-8-sig")

print("Done.")
print(df.head(10))
print("Total properties:", len(df))