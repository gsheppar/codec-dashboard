import os
import requests
from lxml import etree
from templates import message, dial, last


def send_message(messagefromspark):
    codec_username = os.getenv("CODEC_USERNAME")
    codec_password = os.getenv("CODEC_PASSWORD")
    words = messagefromspark.text.split()  # ['@bot', 'send', '192.168.1.204', 'hello']
    msg_to_codec = " ".join(words[3:])
    print(msg_to_codec)
    host = words[2]
    url = 'http://{}/putxml'.format(host)
    payload = message.format(msg_to_codec)
    headers = {'Content-Type': 'text/xml'}
    responsefromcodec = requests.post(url, data=payload, headers=headers, auth=(codec_username, codec_password))
    if responsefromcodec.ok:
        return("Successfully sent message to codec")
    else:
        return("problem sending message - error was {}".format(responsefromcodec.text))


def get_whoami(message):
    codec_username = os.getenv("CODEC_USERNAME")
    codec_password = os.getenv("CODEC_PASSWORD")
    host = message.text.split()[-1]
    url = 'http://{}/status.xml'.format(host)
    response = requests.get(url, auth=(codec_username, codec_password))
    xmlstr = response.content
    root = etree.fromstring(xmlstr)
    hostname = root.xpath('//Status/UserInterface/ContactInfo/Name/text()')[0]
    model = root.xpath('//Status/SystemUnit/ProductId/text()')[0]
    version = root.xpath('//Status/SystemUnit/Software/Version/text()')[0]
    serialnum = root.xpath('//Status/SystemUnit/Hardware/Module/SerialNumber/text()')[0]
    mac = root.xpath('//Status/Network/Ethernet/MacAddress/text()')[0]
    speed = root.xpath('//Status/Network/Ethernet/Speed/text()')[0]
    ipaddr = root.xpath('//Status/Network/IPv4/Address/text()')[0]
    ipmask = root.xpath('//Status/Network/IPv4/SubnetMask/text()')[0]
    ipgw = root.xpath('//Status/Network/IPv4/Gateway/text()')[0]
    cdpneighbor = root.xpath('//Status/Network/CDP/Address/text()')[0]
    cdpplatform = root.xpath('//Status/Network/CDP/Platform/text()')[0]
    cdpneighborport = root.xpath('//Status/Network/CDP/PortID/text()')[0]

    r2s = "##here you go...\n"
    response2spark = "* Hostname: {}\n * Model: {}, Version: {}, SerialNumber: {}\n * IPAddr: {}, Mask: {}, GW: {}, MacAddr: {}\n * This device is connected {} to switch {} ({}) on {}.".format(hostname,model,version,serialnum,ipaddr,ipmask,ipgw,mac,speed,cdpneighbor,cdpplatform,cdpneighborport)
    return(r2s + response2spark)


def get_diag(message):
    codec_username = os.getenv("CODEC_USERNAME")
    codec_password = os.getenv("CODEC_PASSWORD")
    host = message.text.split()[-1]
    url = 'http://{}//getxml?location=/Status/Diagnostics'.format(host)
    diagresponse = requests.get(url, auth=(codec_username, codec_password))
    xmlstr = diagresponse.content
    root = etree.fromstring(xmlstr)
    diag = root.xpath('//Status/Diagnostics/Message/Description/text()')
    if len(diag) == 0:
        diag = "None"
    else:
        diag = root.xpath('//Status/Diagnostics/Message/Description/text()')
    diagresponse2spark = "Current Alarms for this device: {}".format(diag)
    return(diagresponse2spark)


def send_dial(dialfromspark):
    codec_username = os.getenv("CODEC_USERNAME")
    codec_password = os.getenv("CODEC_PASSWORD")
    words = dialfromspark.text.split() # ['@bot', 'dial', '192.168.1.204', 'loopback@cisco.com']
    dial_number = words[3]
    print(dial_number)
    host = words[2]
    url = 'http://{}/putxml'.format(host)
    payload = dial.format(dial_number)
    headers = {'Content-Type': 'text/xml'}
    try:
        params = {'timeout': '2'}
        dialresponsefromcodec = requests.post(url, data=payload, headers=headers, auth=(codec_username, codec_password), params=params)

        if dialresponsefromcodec.ok:
            return("Successfully sent dial command to codec")
        else:
            return("problem sending dial command - error was {}".format(dialresponsefromcodec.text))
    except:
        return ("Timed out. Problem sending command")


def get_last(lastcallfromspark):
    codec_username = os.getenv("CODEC_USERNAME")
    codec_password = os.getenv("CODEC_PASSWORD")
    # long way
    # message_text = lastcallfromspark.text
    # words = message_text.split()
    words = lastcallfromspark.text.split()  # ['@bot', 'last', '192.168.1.204', '5']
    lastcall = words[3]
    print("Call history requested: ", lastcall)
    host = words[2]
    urlstr = 'http://{}/putxml'
    url = urlstr.format(host)
    payload = last.format(lastcall)
    headers = {'Content-Type': 'text/xml'}
    try:
        params = {'timeout': '2'}
        lastcallfromcodec = requests.post(url, data=payload, headers=headers, auth=(codec_username, codec_password), params=params)

        if lastcallfromcodec.ok:
            messageback = lastcallfromcodec.text
            return(messageback)
        else:
            messageback = lastcallfromcodec.text
            return(messageback)
    except:
        messageback = "Timed out. Problem sending command"
        return (messageback)
