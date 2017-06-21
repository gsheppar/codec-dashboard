import os
import requests
from lxml import etree
from templates import message


def get_diag():
    codec_username = "apiuser"
    codec_password = "apiuser"
    url = 'http://192.168.1.204/getxml?location=/Status/Diagnostics'
    response = requests.get(url,auth=(codec_username,codec_password))
    xmlstr = response.text
    root = etree.fromstring(xmlstr)
    diag = root.xpath('//Status/Diagnostics/Message/Description/text()')
    #diagresponse2spark = "here you go...{}".format(diag)
    # print(xmlstr)
    print(diag)

type(get_diag())
