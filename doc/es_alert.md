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
   __tenant__: (ES en caso de variables propias de Elasticsearch)
   
   
   __varname__: Id. la Variable de Interes
   
   
   __variable_desc__: Descripción de la Variable
   
   __query__: Query a Ejecutar para obtener el valor de la variable
   
   __prono_type__: (F:Basado en Formula, D:Discreto)
   
   __lapse__: (eventualmente sirve para definir la iteracion, i.e. entrada en el cron) 
   
   __formula__: Formula para Pronosticar
   
   __umbral_type__: (P:Porcentual o F:Fijo)
   
   __umbral_factor_1__:  factor para calcular el 1er umbral ej. 1.01 que permite calcular el umbral inferior y superior en un instante: Umbral_1 = valor estimado de la variable +/- umbral_factor_1 * valor_estimado 
   
   __umbral_factor_2__ (idem)

   __umbral_factor_3__ (idem)


**var_def**

### Valores Historicos
   tenant: 
   
   varname: 
   
   value: valor medido
   
   timestamp: cuando ocurrió la medición, en segundos “epoch”
   
**var_hist**

### Pronosticos

**var_prono**







