from flask import Flask
import json, os, re, hashlib,datetime
from collections import defaultdict
from flask import request, session, redirect,url_for, render_template
import random
import gdbm
import psycopg2
from psycopg2.extensions import QuotedString
from stop_words import stop_words
app = Flask(__name__)
app.secret_key = '\xe9\x83\x88v\x97\x16\xe1\x06r\xa3+\xd0W\xfb\xea\xa4L\x06LW\xe0\xca\xff\x8a'
words = gdbm.open('/home/nat/code/punsearch/words.db')
rhymes = gdbm.open('/home/nat/code/punsearch/rhymes.db')
#words = gdbm.open('/home/gaertner/code/punsearch/words.db')
#rhymes = gdbm.open('/home/gaertner/code/punsearch/rhymes.db')
connection = psycopg2.connect(user='postgres',password='postgres',dbname='word_pop')

class interval(tuple):
    def contains(self,f):
        return f >= self[0] and f < self[1]
def better_weighted_choice(pop_list):
    total = float(sum(map(lambda x: x[1],pop_list)))
    so_far = 0
    intervals = []
    for pl in pop_list:
        intervals.append(interval((so_far,so_far+pl[1]/total)))
        so_far += pl[1]/total
    chooser = random.random()
    i = len(intervals)/2
    ma = len(intervals)
    mi = 0
    while not intervals[i].contains(chooser):
        if chooser > intervals[i][1]:
            mi = i+1
            i = i+(ma+1-i)/2
        else:
            ma = i-1
            i = mi+(i-mi)/2
    return pop_list[i][0]

def weighted_choice(pop_list):
    pop_list.sort(key=lambda x: x[1])
    length = len(pop_list)
    choice_list = []
    for i in range(length):
        choice_list += [pop_list[i]]*(i+1)
    return random.choice(choice_list)[0]

def get_rhyme(word):
    cursor = connection.cursor()
    word = word.upper()
    try:
        key, syllables = words[word].split()
    except:
        return word.lower()
    rhyme_words = [(re.match(r'(?P<rhyme>[^(]+)\(?.*',rhyme).groupdict()['rhyme'],words[rhyme].split()[1]) for rhyme in rhymes[key].split()]
    rhyme_words = [rw[0] for rw in rhyme_words if rw[1] == syllables and rw[0].lower() not in stop_words]
    if word in rhyme_words:
        rhyme_words.pop(rhyme_words.index(word))
    rhyme_pop = []
    for rw in rhyme_words:
        cursor.execute("select popularity from word_pop_sum where word={rw}".format(rw=QuotedString(rw.lower()).getquoted()))
        res = cursor.fetchall()
        if len(res) > 0:
            rhyme_pop.append((rw,res[0][0]))
        else:
            rhyme_pop.append((rw,1))
    if len(rhyme_words) > 0:
        return better_weighted_choice(rhyme_pop).lower()
    return word.lower()

@app.route('/', methods=['GET','POST'])
def main():
    if request.method == 'POST':
        if len(request.data) > 0:
            data = dict([(s.split('=')[0],s.split('=')[1]) for s in request.data.split('&')])
        elif request.form.has_key('query'):
            data = request.form
        else:
            return 500
        query = data['query']
	cursor = connection.cursor()
	address = request.remote_addr
        cursor.execute('insert into query_log(address,query) values({address},{query});'.format(address=QuotedString(address).getquoted(),query=QuotedString(query).getquoted()))
        connection.commit()
        r_query = []
        query = query.split()
        idx = range(len(query))
        idx_no_stop = filter(lambda i: query[i] not in stop_words,idx)
        if len(idx_no_stop) > 0:
            num_rhymes = random.randint(1,len(idx_no_stop))
            print num_rhymes
            random.shuffle(idx)
            for n in idx_no_stop[:num_rhymes]:
                query[n] = get_rhyme(query[n])
        return redirect('https://www.google.com/search?q={query}'.format(query='+'.join(query)))
    else:
        return render_template('punsearch.html')

if __name__ == "__main__":
    app.run()
