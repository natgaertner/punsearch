from ersatzpg.ersatzpg import ersatz
from word_pop import dbload_conf
import os
for l in filter(lambda x: x.endswith('_lite'),os.listdir('word_pop')):
    print l
    dbload_conf.POP_LOAD['filename'] = '/home/nat/code/punsearch/word_pop/'+l
    ersatz.new_process_copies(dbload_conf)
