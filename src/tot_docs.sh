curl -XPOST "http://10.33.32.107:9200/var_hist/def/_search?size=0" -H 'Content-Type: application/json' -d'
{
  "query": {
    "bool": {
      "must": [
        {"match": {"tenant": "ES"}},
        {"match": {"varname": "tot_docs"}}
      ]
    }
  },
  "_source": ["timestamp",  "tenant"]
}' \
| python -m json.tool \
| grep '\"failed\"' \
| cut -d ':' -f 2 \
| sed 's/&quot;/\"/g' \
| tail -1

