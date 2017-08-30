import requests
import xmltodict
from lxml import etree
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import config
from codec.templates import survey, register, last, dial

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

codec_username = config.codec_username
codec_password = config.codec_password


def get_status(host):
    url = 'http://{}/getxml?location=/Status/Standby'.format(host)
    try:
        response = requests.get(url, verify=False, timeout=2, auth=(codec_username, codec_password))
        xmlstr = response.content
        root = etree.fromstring(xmlstr)
        status = root.xpath('//Status/Standby/State/text()')[0]
        return(status)
    except:
        return("Down")

def get_sip(host):
    url = 'http://{}/getxml?location=/Status/SIP/Registration'.format(host)
    try:
        response = requests.get(url, verify=False, timeout=2, auth=(codec_username, codec_password))
        xmlstr = response.content
        root = etree.fromstring(xmlstr)
        status = root.xpath('//Status/SIP/Registration/Status/text()')[0]
        return(status)
    except:
        return("Down")

def send_survey(host):
    url = 'http://{}/putxml'.format(host)
    payload = survey
    headers = {'Content-Type': 'text/xml'}
    try:
        requests.post(url, data=payload, verify=False, timeout=2, headers=headers, auth=(codec_username, codec_password))
        return("Sent survey to: " + host)
    except:
        return("Failed survey to host: " + host)

def send_register(host):
    url = 'http://{}/putxml'.format(host)
    payload = register
    headers = {'Content-Type': 'text/xml'}
    try:
        requests.post(url, data=payload, verify=False, timeout=2, headers=headers, auth=(codec_username, codec_password))
        return("Feedback registered for: " + host)
    except:
        return("Failed to register host: " + host)

def get_people(host):
    data = "N/A"
    return data

def get_loss(host):
    url = 'http://{}/getxml?location=/Status/MediaChannels'.format(host)
    response = requests.get(url, verify=False, timeout=2, auth=(codec_username, codec_password))
    xml_dict = xmltodict.parse(response.content)
    try:
        check = xml_dict["Status"]["MediaChannels"]
        if check != "None":
            channels = xml_dict["Status"]["MediaChannels"]["Call"]["Channel"]
            for channel in channels:
                if "Video" in channel.keys() and channel["Video"]["ChannelRole"] == "Main":
                    direction = channel["Direction"]
                    if direction == "Incoming":
                        lossin = float(channel["Netstat"]["Loss"])
                        pksin = float(channel["Netstat"]["Packets"])
                    else:
                        lossout = float(channel["Netstat"]["Loss"])
                        pksout = float(channel["Netstat"]["Packets"])
            totalin = lossin/pksin
            totalout = lossout/pksout
            if ((totalin > 5) or (totalout > 5)):
                video = "Yes"
            else:
                video = "No"
        else:
            video = "N/A"
    except:
        video = "N/A"
    try:
        check = xml_dict["Status"]["MediaChannels"]
        if check != "None":
            channels = xml_dict["Status"]["MediaChannels"]["Call"]["Channel"]
            for channel in channels:
                if "Audio" in channel.keys() and channel["Type"] == "Audio":
                    direction = channel["Direction"]
                    if direction == "Incoming":
                        lossin = float(channel["Netstat"]["Loss"])
                        pksin = float(channel["Netstat"]["Packets"])
                    else:
                        lossout = float(channel["Netstat"]["Loss"])
                        pksout = float(channel["Netstat"]["Packets"])
            totalin = lossin / pksin
            totalout = lossout / pksout
            if ((totalin > 5) or (totalout > 5)):
                audio = "Yes"
            else:
                audio = "No"
        else:
            audio = "N/A"
    except:
        audio = "N/A"
    return video, audio

def get_diag(host):
    url = 'http://{}//getxml?location=/Status/Diagnostics'.format(host)
    try:
        diagresponse = requests.get(url, verify=False, timeout=2, auth=(codec_username, codec_password))
        xmlstr = diagresponse.content
        root = etree.fromstring(xmlstr)
        diag = root.xpath('//Status/Diagnostics/Message/Description/text()')
        if len(diag) == 0:
            diag = "None"
        else:
            diag = root.xpath('//Status/Diagnostics/Message/Description/text()')
        return (diag)
    except:
        return("None")

def get_last(host):
    url = 'http://{}/putxml'.format(host)
    payload = last
    headers = {'Content-Type': 'text/xml'}
    try:
        lastcallfromcodec = requests.post(url, data=payload, verify=False, timeout=2, headers=headers, auth=(codec_username, codec_password))
        xmlstr = lastcallfromcodec.text
        root = etree.fromstring(xmlstr)
        callinfo = root.xpath('//Entry/RemoteNumber/text()')[0]
        callinfo += ", " + root.xpath('//Entry/StartTime/text()')[0]
        duration = int(float(root.xpath('//Entry/Duration/text()')[0])/60)
        callinfo += ", " + str(duration)
        callinfo += ", " + root.xpath('//Entry/Video/Incoming/PacketLossPercent/text()')[0]
        callinfo += "/" + root.xpath('//Entry/Video/Outgoing/PacketLossPercent/text()')[0]
        callinfo += ", " + root.xpath('//Entry/Audio/Incoming/PacketLossPercent/text()')[0]
        callinfo += "/" + root.xpath('//Entry/Audio/Outgoing/PacketLossPercent/text()')[0]
        return (callinfo)
    except:
        return ("Failed getting last call info")

def send_dial(host):
    url = 'http://{}/putxml'.format(host)
    payload = dial.format(support_number)
    headers = {'Content-Type': 'text/xml'}
    try:
        dialresponsefromcodec = requests.post(url, data=payload, verify=False, timeout=2, headers=headers, auth=(codec_username, codec_password))
        if dialresponsefromcodec.ok:
            return ("Successfully sent dial command to codec")
        else:
            return ("problem sending dial command - error was {}".format(dialresponsefromcodec.text))
    except:
        return ("Timed out. Problem sending command")
