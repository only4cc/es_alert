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
   tenant: (ES en caso de variables propias de Elasticsearch)
   
   
   varname: Id. la Variable de Interes
   
   
   variable_desc: Descripción de la Variable
   
   query: Query a Ejecutar para obtener el valor de la variable
   
   prono_type: (F:Basado en Formula, D:Discreto)
   
   lapse: (eventualmente sirve para definir la iteracion, i.e. entrada en el cron) 
   
   formula: Formula para Pronosticar
   
   umbral_type: (P:Porcentual o F:Fijo)
   
   umbral_factor_1:  factor para calcular el 1er umbral ej. 1.01 que permite calcular el umbral inferior y superior en un instante: Umbral_1 = valor estimado de la variable +/- umbral_factor_1 * valor_estimado 
   
   umbral_factor_2 (idem)
   

**var_def**

### Valores Historicos
   tenant: 
   
   varname: 
   
   value: valor medido
   
   timestamp: cuando ocurrió la medición, en segundos “epoch”
   
**var_hist**

### Pronosticos

**var_prono**







