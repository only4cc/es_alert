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
<<<<<<< HEAD
| sed 's/ //g' \
| sed 's/\,//g' 

=======
| sed 's/ //g' 
>>>>>>> 14497f84242fff000429a47d7da72266289b7678
