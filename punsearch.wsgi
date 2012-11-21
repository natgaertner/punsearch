activate_this= '/home/nat/code/punsearch/bin/activate_this.py'
print 'activate this good'
execfile(activate_this, dict(__file__=activate_this))
print 'execfile good'
import getpass,os,sys
print 'name',getpass.getuser()
print os.getcwd()
print sys.path
try:
	from punsearch import app as application
except Exception as error:
	print error
print 'app import good'
import logging, sys
print 'logging import good'
logging.basicConfig(stream=sys.stderr)
print 'logging init good'
