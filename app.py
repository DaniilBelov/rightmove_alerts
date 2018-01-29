from bs4 import BeautifulSoup
import json
from apscheduler.schedulers.blocking import BlockingScheduler
import requests
import os

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

sched = BlockingScheduler()

@sched.scheduled_job('interval', hours=4, id='scanRightmove')
def scanRightmove():
    url = "http://www.rightmove.co.uk/property-to-rent/find.html?locationIdentifier=USERDEFINEDAREA%5E%7B%22id%22%3A4703045%7D&maxPrice=800&savedSearchId=25639538&minBedrooms=2&retirement=false&letFurnishType=furnished"

    page = requests.get(url);
    soup = BeautifulSoup(page.content, 'html.parser')

    data = soup.select('div.l-searchResult.is-list')
    old_links = json.load(open('got.json'))

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
def clearoldLinks()
    with open(os.path.join(__location__, 'got.json'), 'w') as outfile:
        json.dump([], outfile)

sched.start()
