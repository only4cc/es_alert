#from subprocess import Popen, PIPE
 
#process = Popen(['mnav_total.sh'], stdout=PIPE, stderr=PIPE)
#stdout, stderr = process.communicate()
#print stdout


#import os
#print (os.popen("bash /home/es_alert/src/mnav_total.sh").read())
#
import subprocess
externo = "bash /home/es_alert/src/mnav_total.sh"
output = subprocess.check_output(externo, shell=True)
output = str(output)
print(output.rstrip())
#
