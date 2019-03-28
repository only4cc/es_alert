# Alertas Elasticsearch

## Objetivo
Describir en forma resumida los principales procesos y estructuras de datos utilizadas.

## Estructuras de datos
Las estructuras de datos administradas en Elasticsearch corresponden a 3 “tipos”, todos bajo el índice _criteria_:

1. **Definición de la Variable o Criterio** : almacena la definición de la variable, como se consultará

2. **Pronósticos** : los valores esperados en el tiempo y sus umbrales

3. **Valores Historicos** : los valores medidos en el tiempo

## Resúmen de Indices

### Definicion o Criterio

#### var_def

   __tenant__: (ES en caso de variables propias de Elasticsearch) 
   
   __varname__: Id. la Variable de Interes
   
   __variable_desc__: Descripción de la Variable
   
   __query__: Query a Ejecutar para obtener el valor de la variable
   
   __prono_type__: (F:Basado en Formula, D:Discreto, E:External)
   
   __lapse__: (eventualmente sirve para definir la iteracion, i.e. entrada en el cron) 
   
   __formula__: Formula para Pronosticar
   
   __external__: Programa/Script externo a Ejecutar 
   
   __umbral_type__: (P:Porcentual o F:Fijo)
   
   __umbral_factor_1__:  factor para calcular el 1er umbral ej. 1.01 que permite calcular el umbral inferior y superior en un instante: Umbral_1 = valor estimado de la variable +/- umbral_factor_1 * valor_estimado 
   
   __umbral_factor_2__ (idem)

   __umbral_factor_3__ (idem)



### Valores Historicos
#### var_hist

   __tenant__: 
   
   __varname__: 
   
   __value__: valor medido
   
   __timestamp__: cuando ocurrió la medición, en segundos “epoch”
   


### Pronosticos

#### var_prono
  __tenant__: 
   
   __varname__: 
   
   __estimated_value__: valor estimado
   
   __ts_ini__: timestamp de inicio cuando para el valor estimado, en segundos *“epoch”*

   __ts_end__: timestamp de fin cuando para el valor estimado, en segundos *“epoch”*







