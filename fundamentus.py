import requests
import re
from lxml.html import fragment_fromstring


def _convert_data(data):
    data = data.replace('.', '').replace(',', '.')
    try:
        return float(data)
    except ValueError:
        return data


def load_generic_data():
    html_data = requests.get('http://www.fundamentus.com.br/resultado.php')

    pattern = re.compile('<table id="resultado".*</table>', re.DOTALL)
    [table] = re.findall(pattern, html_data.text)
    page = fragment_fromstring(table)

    [thead] = page.xpath('thead')
    [tr] = thead.xpath('tr')
    headers = [th.text_content().strip() for th in tr.xpath('th')]

    [tbody] = page.xpath('tbody')


    stock_info = {
    }


    for tr in tbody.xpath('tr'):
        data = [_convert_data(i.text_content().strip()) for i in tr.xpath('td')]
        stock_data = dict(zip(headers, data))
        tick = stock_data['Papel']
        stock_info[tick] = stock_data

    return stock_info


def get_specific_data(tick):
    html_data = requests.get(f'http://www.fundamentus.com.br/detalhes.php?papel={tick}')
    [ table_section ] = re.findall(re.compile('<table.*</table>', re.DOTALL), html_data.text)
    tables = [
      fragment_fromstring(t + '</table>')
      for t in table_section.split('</table>')
      if t.strip()
    ]

    data = {}

    for table in tables:
        for tr in table.xpath('tr'):
            td = [
              _convert_data(i.xpath('span')[-1].text_content().strip())
              for i in tr.xpath('td')
              if 'label' in i.attrib.get('class') or 'data' in i.attrib.get('class')
            ]

            while td:
                key = td.pop(0)
                value = td.pop(0)
                if key:
                    data[key] = value

    return data


if __name__ == '__main__':
    import pprint
    import sys
    try:
        tick = sys.argv[1]
    except IndexError:
        tick = 'ITSA4'
    pprint.pprint(get_specific_data(tick))
