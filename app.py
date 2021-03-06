from bs4 import BeautifulSoup
import json
from apscheduler.schedulers.blocking import BlockingScheduler
import requests
import os
from reppy.robots import Robots
from db import DB

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

sched = BlockingScheduler()

@sched.scheduled_job('cron', minute=50, id='scanRightmove')
def scanRightmove():
    db = DB()
    headers = {'User-Agent': 'Dan070Bot(daniilbelov98@yandex.ru)'}
    url = "http://www.rightmove.co.uk/property-to-rent/find.html?locationIdentifier=USERDEFINEDAREA%5E%7B%22id%22%3A4703045%7D&maxBedrooms=3&minBedrooms=2&maxPrice=1200&dontShow=retirement&furnishTypes=furnished"

    robots = Robots.fetch('http://www.rightmove.co.uk/robots.txt', headers=headers)
    allowed = robots.allowed('http://www.rightmove.co.uk/property-to-rent/find.html?*', 'Dan070Bot(daniilbelov98@yandex.ru)')

    if not allowed:
        return

    page = requests.get(url, headers=headers);
    soup = BeautifulSoup(page.content, 'html.parser')

    data = soup.select('div.l-searchResult.is-list')

    t_url = 'https://api.telegram.org/bot538125304:AAEodL7ns7iuTbbpRPgpLteOs-o4UAunV6k/sendMessage'
    headers = {'Content-Type': 'application/json'}

    for property in soup.select('div.l-searchResult.is-list'):
        added = property.select('span.propertyCard-branchSummary-addedOrReduced')[0].get_text()
        payload = {'chat_id': '@rightmove_alerts'}

        if added == 'Added today' or added == 'Reduced today':
            link = property.select('a.propertyCard-link')[0].get('href')
            full_link = 'http://www.rightmove.co.uk' + link

            if db.checkURL(full_link) == 0:
                db.addURL(full_link)
                payload['text'] = full_link
                requests.post(t_url, data=json.dumps(payload), headers=headers);

    db.close()
    print('Cycle')


@sched.scheduled_job('cron', hour=0, minute=30, id='clearLinks')
def clearLinks():
    db = DB()
    db.clear()
    db.close()

sched.start()
