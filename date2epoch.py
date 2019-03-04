import util, sys

try:
    fecha  = sys.argv[1]
    ts    = util.get_seg_epoch_from_date(fecha)
    print("segundos Epoch para ",fecha," es ",ts)
except Exception as e:    
    print(e)
    print("Formato de entrada de la fecha es YYYY-MM-DDTHH:MM")