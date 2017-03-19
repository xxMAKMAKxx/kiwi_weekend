#!/bin/python
# -*- coding: UTF-8 -*-
from grab import Grab
import re
import json
from collections import OrderedDict
from flask import Flask, render_template, request, redirect, abort
from redis import StrictRedis
import hashlib
import time


class pepeComunicator():

    def pepeComuncator(self):
        return self

    def removeMultipleNewLines(self, string):
        string = re.sub('\n\s*\n', '\n', string)
        string = re.sub(re.compile('^\n*\s*', re.MULTILINE), '', string)
        string = re.sub('\n$', '', string)
        return string.split('\n')

    def getGrabPepeObject(self, input_string):
        g = Grab()
        g.go('http://pep8online.com/checkresult', post={'code': input_string}, headers={'Content-Type':'application/x-www-form-urlencoded', 'Accept': 'text/html,json', 'Host':'pep8online.com'})
        return g

    def getArrayOfErrors(self, g):
        results = g.css_list('tr.tr-result')
        array_or_errors = []
        list_of_fields = ['code', 'line', 'column', 'error_msg']
        for i in range(0, len(results)):
            array_or_errors.append(OrderedDict(zip(list_of_fields, self.removeMultipleNewLines(results[i].text_content()))))
        return array_or_errors

    def arrayToJson(self, _array):
        return json.dumps(_array)


class getRedis():

    redis_config_default = {'host': '146.185.172.28', 'password': 'asorGYGAhJ1ybSCrWc2l5h8mKYk', 'port': 6379}
    def __init__(self, redis_config):
        if(redis_config == None):
            self.redis = StrictRedis(**self.redis_config_default)
        else:
            self.redis = StrictRedis(**redis_config)

class dogeDefender():

    def basicChecks(self, request):
        if not(request.user_agent.platform == 'win' or request.user_agent.platform == 'linux' or request.user_agent.platform == 'macos'):
            return False
        else:
            return True
    def fromGetChecker(self, request):
        if (len(request.form.getlist('from_get')) > 0):
            if (request.form.getlist('from_get')[0] == 'True'):
                return True
            else:
                return False

def main():
    input_string = 'print (AsdasdSA)\ndef test1():'
    communicator = pepeComunicator()
    print(communicator.arrayToJson(communicator.getArrayOfErrors(communicator.getGrabPepeObject(input_string))))





if __name__ == "__main__": main()
else:
    app = Flask(__name__)
    app.config['PROPAGATE_EXCEPTIONS'] = True
    communicator = pepeComunicator()
    redis = getRedis(None)
    defender = dogeDefender()


    @app.route('/')
    def index_default():
        return redirect('/check_pep8', code=302)

    @app.route('/check_pep8', methods=['GET', 'POST'])
    def check_pep8():
        m_hash = hashlib.md5()
        if request.method == 'POST':
            #check from get
            if(not defender.fromGetChecker(request)):
                abort(403)
            #redis check key
            m_hash.update(request.form.getlist('input_code')[0])
            if(redis.redis.get(m_hash.hexdigest()) == None):
                print('V redisu jsem teda tenhle input nenasel...')
                array_of_errors = communicator.getArrayOfErrors(communicator.getGrabPepeObject((request.form.getlist('input_code'))[0]))
                if (request.args.get('ignored_codes')):
                    ignored_codes = request.args.get('ignored_codes').split(',')
                    for item in array_of_errors:
                        if(item['code'] in ignored_codes):
                            array_of_errors.remove(item)
                returnString = communicator.arrayToJson(array_of_errors)
                redis.redis.set(m_hash.hexdigest(), returnString)
                return render_template("results.html", results=json.loads(returnString))
            else:
                print('V redisu jsem ho nasel a je: '+redis.redis.get(m_hash.hexdigest()))
                return render_template("results.html", results=json.loads((redis.redis.get(m_hash.hexdigest()))))
        elif request.method == 'GET':
            with open('ip.log', 'a') as ip_log_file:
                if(request.remote_addr != None and request.user_agent.platform != None):
                    ip_log_file.write("IP: "+request.remote_addr+" accessed at "+time.ctime()+" from "+request.user_agent.platform+'\n')
                else:
                    ip_log_file.write("IP: " + request.remote_addr + " accessed at " + time.ctime()+'\n')

            if(not defender.basicChecks(request)):
                abort(403)
            #maintanence check
            if(redis.redis.get("jesmakovappkavmaintanence") == 'True'):
                return '<h1>Application is in maintanence, please come back later.</h1>'
            #process requests
            if (request.args.get('ignored_codes')):
                return render_template('pep8_get.html', ignored_codes_html='?ignored_codes='+request.args.get('ignored_codes'))
            else:
                return render_template('pep8_get.html')
