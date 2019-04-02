#
# Parametros:
#  var  = tenant varname : obtenido desde iteracion
#
#  SEGUNDOSASUMAR=86400  Periodo a Generar en Segundos
#  FROMEPOCH= Fecha desde a Generar en Epoch
#  TOEPOCH= Fecha hasta a Generar en Epoch
#  LAPSO=600 Lapso de cada cuantos segundos se generara un pronostico | 600 = 10 Min
#

SEGUNDOSASUMAR=86400
FROMEPOCH=`date "+%s"`
TOEPOCH=$((FROMEPOCH+SEGUNDOSASUMAR))
LAPSO=600    

# Obtiene todas las variables para iterar
TMPFILE=/tmp/iterador.txt
rm $TMPFILE
`docker run --rm --network="host" --name itera_get_var -v /home/es_alert/cfg/config.yml:/src/config.yml:ro es_alert:latest /usr/local/bin/python get_all_vars.py > $TMPFILE`

# Ejecuta pronostico para cada una de las variables
input="$TMPFILE"
while IFS= read -r var
do

  #docker run --rm --network="host" --name gen_prono -v /home/es_alert/cfg/config.yml:/src/config.yml:ro es_alert:latest sh parm2prono.sh $var $FROM_DUMMY ${SEGUNDOS_DIA} $LAPSO

  docker run --rm --network="host" --name gen_prono \
                -v /home/es_alert/cfg/config.yml:/src/config.yml:ro \
                -v /home/es_alert/log:/log:rw \
                es_alert:latest python gen_prono.py  $var $FROMEPOCH $TOEPOCH $LAPSO

done < "$input"


# Para una sola variable ...
#docker run --rm --network="host" --name gen_prono -v /home/es_alert/cfg/config.yml:/src/config.yml:ro \
#es_alert:latest python gen_prono.py $var $FROMEPOCH $TOEPOCH $LAPSO




