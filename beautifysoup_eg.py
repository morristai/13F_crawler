content = '''
<div class="value">
    <p class="name">Michael Jordan</p>
</div>

<div class="value">
    <p class="team">Real Madrid</p>
</div>

<div class="value">
    <p class="Sport">Ping Pong</p>
</div>
'''

from bs4 import BeautifulSoup

soup = BeautifulSoup(content)

person = {}

for div in soup.findAll('div', {'class': 'value'}):
    person[div.find('p').attrs['class'][0]] = div.text.strip()

print(person)

# {'Sport': u'Ping Pong', 'name': u'Michael Jordan', 'team': u'Real Madrid'}