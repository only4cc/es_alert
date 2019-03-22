#
# Parametros:
#  var  = tenant varname : obtenido desde iteracion
#
#  SEGUNDOS_DIA=86400  Periodo a Generar en Segundos
#  FROM_DUMMY=0        Dummy (pero debe ir este parametro)
#  LAPSO=600 Lapso de cada cuantos segundos se generara un pronostico
#

SEGUNDOS_DIA=86400
FROM_DUMMY=0
LAPSO=600

#curl -XGET http://10.33.32.107:9200/var_def/_search  -H 'Content-Type: application/json' -d'
#{
#  "query": {
#   "match_all": {}
#  },
#  "_source" : ["tenant", "varname"]
#}'

# Obtiene todas las vraiables 
TMPFILE=/tmp/iterador.txt
rm $TMPFILE
`docker run --rm --network="host" --name itera_get_var -v /home/es_alert/cfg/config.yml:/src/config.yml:ro \
es_alert:latest /usr/local/bin/python get_all_vars.py > $TMPFILE`

# Ejecuta pronostico para cada una de las variables
input="$TMPFILE"
while IFS= read -r var
do
    echo 
    echo "$var"
    docker run --rm --network="host" --name gen_prono -v /home/es_alert/cfg/config.yml:/src/config.yml:ro \
es_alert:latest sh gen_prono.sh $var $FROM_DUMMY ${SEGUNDOS_DIA} $LAPSO
done < "$input"
exit

# Para una sola variable ...
#docker run --rm --network="host" --name gen_prono -v /home/es_alert/cfg/config.yml:/src/config.yml:ro \
#es_alert:latest sh gen_prono.sh $TENANT $VARNAME $FROM_DUMMY ${SEGUNDOS_DIA} $LAPSO



