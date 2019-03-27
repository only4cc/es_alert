NODOES=192.168.161.101
INDEXNAME=be-mnav-2019\*
curl --silent  -XPOST "http://$NODOES:9200/$INDEXNAME/_search?size=0" -H 'Content-Type: application/json' -d'
{
    "aggs": {
        "range": {
            "date_range": {
                "field": "date",
                "format": "yyyy-MM-dd HH",
                "ranges": [
                    { "to": "now+0H/H" }, 
                    { "from": "now-1H/H" } 
                ]
            }
        }
    }
}' \
| python -m json.tool \
| grep '\"total\"' \
| tail -1 \
| sed 's/\"total\"://' \
| sed 's/ //g' 
