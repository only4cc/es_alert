import sys
import datetime

# 1553742660

def prono_mnav(time_epoch):
    ep = float(time_epoch)
    # convierte de epoch a hora
    v = datetime.datetime.fromtimestamp(ep).strftime('%Y-%m-%d %H:%M:%S')
    tt = int( v[14:16] )
    t = (tt % 24)

    minimo = 3000   # Minimo de llamadas 
    matimo = 100000 # Matimo de llamadas
    valor  = 0      # Valor de llamadas simulado a la hora
    
    if ( t >= 3 and t <= 9):
        valor = minimo
    
    if ( t > 9 and t <= 12 ):
        a = (matimo-minimo)/3 
        b = -4*(matimo-minimo) + matimo  
        valor = ( (a * t) + b )
    
    if ( t > 12 and t <= 20 ):
        valor = matimo 

    if ( t > 20 and t < 24 ):
        a = (minimo-matimo)/7           # -11000
        b = (matimo - 20/7 * (minimo-matimo)) #60000
        valor = ( (a * t) + b )
    
    if ( t >= 0 and t <= 3):
        a = (minimo-matimo)/7 
        b =  minimo - 3*(minimo-matimo)/7
        valor = ( (a * t) + b )
        
    return valor



if __name__ == '__main__':
    if ( len(sys.argv) == 2 ):
        time  = sys.argv[1]    
    else:
        print( "Error:", sys.argv[0]," requiere el parametro time en epoch.")
        exit()

    pronostico = prono_mnav(time)
    print(pronostico, end =" ")