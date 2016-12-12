#!/usr/bin/env python

from lxml import html
import requests

def getQNH(area='Area 60:', url='http://www.bom.gov.au/aviation/forecasts/area-qnh/'):
    r = requests.get(url)
    tree = html.fromstring(r.content)

    dt = tree.xpath('//dt[contains(text(), "' + area + '")]')[0]

    dd = dt.getnext()
    qnh = dd.text
    print qnh
    return qnh
