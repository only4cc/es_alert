# Parametros tenant varname ts_inicio_prono segundos_termino lapso

SEGUNDOS_DIA=86400
FROM_DUMMY=0
LAPSO=600

docker run --rm --network="host" --name gen_prono -v /home/es_alert/cfg/config.yml:/src/config.yml:ro \
es_alert:latest sh gen_prono.sh ES tot_docs $FROM_DUMMY ${SEGUNDOS_DIA} $LAPSO



