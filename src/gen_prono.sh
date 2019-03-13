#
# gen_prono.sh
# Genera pronosticos de una variable entre from y to cada frecuency segundos
# Supone que se ejecuta a las 00:00 todos los dias y genera registros para las 24 horas
# La frecuencia es en segundos (ej. 1800 es media hora)
#

DIR=/app

# Segundos de un dia
SEGUNDOSASUMAR=86400

TENANT=$1
VARNAME=$2
FRECUENCY=$3

#cd /home/es_alert/src/

# Determina la hora actual en formato YYYY-MM-DDTHH:MI
AHORA=`python $DIR/print_timestamp.py`

# Determina hora de inicio y fin de dia en base a fecha actual 
FROM=${AHORA:0:10}T00:00

# Convierte a epoch
FROMEPOCH=`python date2epoch.py $FROM`
TOEPOCH=$((FROMEPOCH+SEGUNDOSASUMAR))

echo "ejecutare gen_prono.py $TENANT $VERNAME $FROMEPOCH $TOEPOCH $FRECUENCY"

python $DIR/gen_prono.py $TENANT $VERNAME $FROM $TO $FRECUENCY

