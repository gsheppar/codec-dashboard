import csv
import datetime
import json
import os
import smtplib
import threading

from flask import request, make_response, Flask, render_template

import config

bot = Flask(__name__)

from codec.actions import get_status, send_survey, send_register, get_last, get_sip, get_people, get_loss, get_diag, send_dial

codec_username= config.codec_username
codec_password= config.codec_password
email_user= config.email_user
email_pwd= config.email_pwd
email_dest = config.email_dest
email_server = config.email_server

path=os.path.abspath(os.curdir)
log = path + "/message_log.txt"

###############################

def get_rooms():
    with open('codec/codec.json') as data_file:
        data = json.load(data_file)
    return data

def get_surveys():
    now = datetime.datetime.now()
    now_str = now.strftime("%Y-%m")
    surveycsv = 'survey/Feedback-{}.csv'.format(now_str)
    surveyjson = 'survey/Feedback-{}.json'.format(now_str)
    with open(surveycsv) as f:
        reader = csv.DictReader(f, skipinitialspace=True)
        rows = list(reader)
    with open(surveyjson, 'w') as data_file:
        data_file.write(json.dumps(rows, sort_keys=True, indent=4, separators=(',', ': ')))
    with open(surveyjson) as data_file:
        data = json.load(data_file)
    return data

@bot.route('/')
def hello():
    return dashboard()

@bot.route('/rooms', methods=['GET','POST'])
def rooms():
    if request.method == 'GET':
        return render_template('rooms.html')
    elif request.method == 'POST':
        rooms = get_rooms()
        return render_template('rooms.html', rooms=rooms)

@bot.route('/surveys', methods=['GET', 'POST'])
def surveys():
    if request.method == 'GET':
        return render_template('surveys.html')
    elif request.method == 'POST':
        surveys = get_surveys()
        return render_template('surveys.html', surveys=surveys)

@bot.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    sytemsdown = 0
    activecalls = 0
    occupiedrooms = 0
    diagerrors = "No"
    roomnum = 0
    packetloss = "N/A"
    with open('codec/codec.json') as data_file:
        data = json.load(data_file)
    for codec in data:
        roomnum += 1
        if (codec['NetworkAlert'] == "Yes" or codec['SIPAlert'] == "Yes"):
            sytemsdown += 1
        if (codec['Occupied'] == "Yes"):
            occupiedrooms += 1
        if (codec['Call'] == "Yes"):
            activecalls += 1
        if (codec['Diag'] == "Errors"):
            diagerrors = "Yes"
    return render_template('dashboard.html', systemsdown=sytemsdown, activecalls=activecalls, occupiedrooms=occupiedrooms, diagerrors=diagerrors, packetloss=packetloss, roomnum=roomnum)

@bot.route('/surveygraph', methods=['GET', 'POST'])
def surveygraph():
    numexcellent = 0
    numgood = 0
    numpoor = 0
    numnone = 0
    now = datetime.datetime.now()
    now_str = now.strftime("%Y-%m")
    surveyjson = 'survey/Feedback-{}.json'.format(now_str)
    with open(surveyjson) as data_file:
        data = json.load(data_file)
    for codec in data:
        if (codec['Quality'] == "Excellent"):
            numexcellent += 1
        if (codec['Quality'] == "Good"):
            numgood += 1
        if (codec['Quality'] == "Poor"):
            numpoor += 1
        if (codec['Quality'] == "No response"):
            numnone += 1
    return render_template('surveygraph.html', numexcellent=numexcellent, numgood=numgood, numpoor=numpoor, numnone=numnone)

###############################

@bot.route('/codec', methods=['POST'])
def receivepostfromcodec():
    f = open(log, "a")
    f.write("\n")
    f.write(request.data)
    now = datetime.datetime.now()
    now_str = now.strftime("%Y-%m")
    surveycsv = 'survey/Feedback-{}.csv'.format(now_str)
    if not os.path.exists(surveycsv):
        outFile = open(surveycsv, 'w')
        outFile.write("SystemName, Quality, Booked, Call Number, Start Time, Duration, Out Video Loss, In Video Loss")
        outFile.close()
        print "Create new csv survey file"
    # Call Connection and codec check
    try:
        data = json.loads(request.data)
        action = data['Status']['Call'][0]['Status']['Value']
        newunit = "Yes"
        print("Received status call: {}".format(action))
        if action == "Connected":
            host = data['Status']['Identification']['IPAddress']['Value']
            name = data['Status']['Identification']['SystemName']['Value']
            with open('codec/codec.json', 'r') as data_file:
                data = json.load(data_file)
            for codec in data:
                 if (codec['SystemName'] == name):
                    codec["Call"] = "Yes"
                    codec["IP"] = host
                    newunit = "No"
                 if (codec['IP'] == host):
                    codec["Call"] = "Yes"
                    codec["SystemName"] = name
                    newunit = "No"
            if newunit == "Yes":
                print "New unit found"
                entry = {"Booked": "N/A", "Call": "Yes", "Diag": "None", "DiagAlert": "No", "IP": host,
                         "NetworkAlert": "No", "Occupied": "No", "Packetloss": "No", "People": "N/A",
                         "SIP": "Registered", "SIPAlert": "No", "Status": "Standby",
                         "SystemName": name}
                data.append(entry)
                print json.dumps(data)
            with open('codec/codec.json', 'w') as data_file:
                data_file.write(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))
    except Exception as e:
        print "Request did not contain any action type: Call Connected"
    # Send Survey
    try:
        data = json.loads(request.data)
        action = data['Event']['CallDisconnect']['CauseType']['Value']
        print("Received status call: {}".format(action))
        if (action == "LocalDisconnect" or action == "RemoteDisconnect"):
            host = data['Event']['Identification']['IPAddress']['Value']
            print send_survey(host)
    except Exception as e:
        print "Request did not contain any action type: Send Survey"
    # Widget clicked
    try:
        data = json.loads(request.data)
        widget = data['Event']['UserInterface']['Extensions']['Widget']['Action']['WidgetId']['Value']
        action = data['Event']['UserInterface']['Extensions']['Widget']['Action']['Type']['Value']
        host = ip = data['Event']['Identification']['IPAddress']['Value']
        if (widget == "widget_1" and action == "clicked"):
            send_dial(host)
    except Exception as e:
        print "Request did not contain any action type: Widget Clicked"
    # Survey Feedback
    try:
        data = json.loads(request.data)
        action = data['Event']['UserInterface']['Message']['Prompt']['Response']['FeedbackId']['Value']
        ip = data['Event']['Identification']['IPAddress']['Value']
        host = data['Event']['Identification']['SystemName']['Value']
        booked = "N/A, "
        if (action == "1"):
            response = data['Event']['UserInterface']['Message']['Prompt']['Response']['OptionId']['Value']
            callinfo = get_last(ip)
            outFilecsv = open(surveycsv, 'a')
            if (response == "1"):
                calldetail = host + ", " + "Excellent, " + booked + callinfo
                outFilecsv.write("\n")
                outFilecsv.write(calldetail)
            elif (response == "2"):
                calldetail = host + ", " + "Good, " + booked + callinfo
                outFilecsv.write("\n")
                outFilecsv.write(calldetail)
            elif (response == "3"):
                calldetail = host + ", " + "Poor, " + booked + callinfo
                outFilecsv.write("\n")
                outFilecsv.write(calldetail)
            else:
                calldetail = host + ", " + "No Response, " + booked + callinfo
                outFilecsv.write("\n")
                outFilecsv.write(calldetail)
            outFilecsv.close()
            with open('codec/codec.json', 'r') as data_file:
                data = json.load(data_file)
            for codec in data:
                if (codec['IP'] == ip):
                    codec["Call"] = "No"
            with open('codec/codec.json', 'w') as data_file:
                data_file.write(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))
        return make_response("ok")
    except Exception as e:
        print "Request did not contain any action type: Receive Survey Feedback"
        return make_response("ok")

###############################

def check_status():
    threading.Timer(30.0, check_status).start()
    with open('codec/codec.json', 'r') as data_file:
        data = json.load(data_file)
    for codec in data:
        status = get_status(codec['IP'])
        sip = get_sip(codec['IP'])
        people = get_people(codec['IP'])
        packetloss = get_loss(codec['IP'])
        diagstatus = get_diag(codec['IP'])
        codec['SIP'] = sip
        codec['Status'] = status
        codec['People'] = people
        codec['Packetloss'] = packetloss
        if (diagstatus != "None"):
            codec['Diag'] = "Errors"
        else:
            codec['Diag'] = diagstatus
        # Update if occupied
        if codec['Status'] == "Off":
            codec['Occupied'] = "Yes"
        else:
            codec['Occupied'] = "No"
        # Network and SIP alerts
        if (codec['Status'] == "Down" and codec['NetworkAlert'] == "No"):
            print "Send email now system down"
            codec['NetworkAlert'] = "Yes"
            codec['Occupied'] = "Down"
            print codec['Occupied']
            sub = codec['SystemName'] + " Down"
            bod = "System is not reachable at: https://" + codec['IP']
            send_email(sub, bod)
        elif (codec['Status'] != "Down" and codec['NetworkAlert'] == "Yes"):
            print "Send email now system up"
            codec['NetworkAlert'] = "No"
            codec['Occupied'] = "No"
            sub = codec['SystemName'] + " Up"
            bod = "System is now reachable at: https://" + codec['IP']
            send_email(sub, bod)
        elif (codec['SIP'] != "Registered" and codec['SIPAlert'] == "No"):
            if codec['NetworkAlert'] == "No":
                print "Send email now system is not registered"
                codec['SIPAlert'] = "Yes"
                sub = codec['SystemName'] + " not registered"
                bod = "System is not registered"
                send_email(sub, bod)
        elif (codec['SIP'] == "Registered" and codec['SIPAlert'] == "Yes"):
            print "Send email now system is registered"
            codec['SIPAlert'] = "No"
            sub = codec['SystemName'] + " is registered"
            bod = "System is now registered"
            send_email(sub, bod)
    with open('codec/codec.json', 'w') as data_file:
        data_file.write(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))

def codec_register():
    with open('codec/codec.json', 'r') as data_file:
        data = json.load(data_file)
    for codec in data:
        print send_register(codec['IP'])

def codec_inventory(check):
    with open('codec/codec.json', 'r') as data_file:
        data = json.load(data_file)
    for codec in data:
        if (codec['SystemName'] == check['Event']['Identification']['SystemName']['Value']):
            codec['IP'] = check['Event']['Identification']['IPAddress']['Value']

def send_email(subject, body):
    FROM = email_user
    TO = email_dest
    SUBJECT = subject
    TEXT = body
    SERVER = email_server

    # Prepare actual message
    message = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    try:
        # SMTP_SSL Example
        server_ssl = smtplib.SMTP_SSL(SERVER, 465)
        server_ssl.ehlo()  # optional, called by login()
        server_ssl.login(email_user, email_pwd)
        # ssl server doesn't support or need tls, so don't call server_ssl.starttls()
        server_ssl.sendmail(FROM, TO, message)
        # server_ssl.quit()
        server_ssl.close()
        print 'successfully sent the mail'
    except:
        print "failed to send mail"

check_status()
codec_register()

bot.run(host='0.0.0.0', port=5000)