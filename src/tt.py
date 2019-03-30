'''
from subprocess import Popen, PIPE
 
process = Popen(['mnav_total.sh'], stdout=PIPE, stderr=PIPE)
stdout, stderr = process.communicate()
print stdout
'''

import os
print (os.popen("bash /home/es_alert/src/mnav_total.sh").read())

