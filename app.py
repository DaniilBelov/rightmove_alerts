from bs4 import BeautifulSoup
import json
from apscheduler.schedulers.blocking import BlockingScheduler
import requests
import os
from reppy.robots import Robots

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

sched = BlockingScheduler()

@sched.scheduled_job('interval', seconds=30, id='scanRightmove')
def scanRightmove():
    headers = {'User-Agent': 'Dan070Bot(daniilbelov98@yandex.ru)'}
    url = "http://www.rightmove.co.uk/property-to-rent/find.html?locationIdentifier=USERDEFINEDAREA%5E%7B%22id%22%3A4703045%7D&maxPrice=800&savedSearchId=25639538&minBedrooms=2&retirement=false&letFurnishType=furnished"

    robots = Robots.fetch('http://www.rightmove.co.uk/robots.txt', headers=headers)
    allowed = robots.allowed('http://www.rightmove.co.uk/property-to-rent/find.html?*', 'Dan070Bot(daniilbelov98@yandex.ru)')

    if not allowed:
        return

    page = requests.get(url, headers=headers);
    soup = BeautifulSoup(page.content, 'html.parser')

    data = soup.select('div.l-searchResult.is-list')

    with open(os.path.join(__location__, 'got.json')) as data_file:
        old_links = json.load(data_file)

    links_today = []
    t_url = 'https://api.telegram.org/bot538125304:AAEodL7ns7iuTbbpRPgpLteOs-o4UAunV6k/sendMessage'
    headers = {'Content-Type': 'application/json'}

    for property in soup.select('div.l-searchResult.is-list'):
        added = property.select('span.propertyCard-branchSummary-addedOrReduced')[0].get_text()
        payload = {'chat_id': '@rightmove_alerts'}

        if added == 'Added today' or added == 'Reduced today':
            link = property.select('a.propertyCard-link')[0].get('href')
            full_link = 'http://www.rightmove.co.uk' + link

            if full_link not in old_links:
                links_today.append(full_link)
                payload['text'] = full_link
                requests.post(t_url, data=json.dumps(payload), headers=headers);

    old_links = old_links + links_today

    with open(os.path.join(__location__, 'got.json'), 'w') as outfile:
        json.dump(old_links, outfile)

    print('Cycle')


@sched.scheduled_job('cron', minute=0, hour=0, id='clearOldLinks')
def clearoldLinks():
    with open(os.path.join(__location__, 'got.json'), 'w') as outfile:
        json.dump([], outfile)

sched.start()