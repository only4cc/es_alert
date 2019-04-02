# Parametros tenant varname

docker run --rm --network="host" --name es_alert_2 \
       -v /home/es_alert/cfg/config.yml:/src/config.yml:ro \
       -v /home/es_alert/log:/log:rw \
       es_alert:latest python eval_all.py 



