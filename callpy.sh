pgm_par=$*
#echo $pgm_par

docker run -t -i --rm --network="host" --name python_img \
                                  -v '/home/es_alert/cfg/config.yml:/src/config.yml':ro \
                                  -v '/home/es_alert/src:/src':ro \
                                  -v '/home/es_alert/log:/log':rw \
                                  es_alert:latest python $pgm_par

#python:3.7-alpine python src/$pgm_par



