from bs4 import BeautifulSoup
import pandas as pd
from lxml import html
import os
import time
from login import login,create_driver
from youtube import get_mostsubs
import re


driver = create_driver()

driver.maximize_window()
                                     
URLS=["https://socialblade.com/instagram/top/5000/followers","https://socialblade.com/facebook/top/5000/likes","https://socialblade.com/twitter/top/5000/most-followers","https://socialblade.com/dlive/top/5000/most-followers","https://socialblade.com/tiktok/top/5000/most-followers","https://socialblade.com/tiktok/top/5000/most-likes","https://socialblade.com/dailymotion/top/5000/mostfollowers","https://socialblade.com/twitch/top/5000/most-followers"]

def extract_site_and_metric(url):
    site_name = url.split("//")[1].split("/")[1]
    metric_match = re.search(r'/top/5000/([a-zA-Z\-_]+)$', url)
    if metric_match:
        metric = metric_match.group(1)
    else:
        metric = None
    return site_name, metric


def get_soup(url):
    """return soup object of any url"""
    driver.get(url)
    time.sleep(5)  
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    return soup



def get_data(url):
    channel_sub_map = []
    
    soup = get_soup(url)
    root = html.fromstring(str(soup))
    site,metrics=extract_site_and_metric(url)
    if site=="twitter"  or site=="twitch" :
        channel_name=root.xpath("//div[contains(@style, 'float: left; width: 200px; line-height: 25px;')]/a")
        subscriber_count = root.xpath("//div[@style='float: left; width: 100px;']")
        channel_list = [channel.text for channel in channel_name]
        subscriber_list = [subscriber.text_content().strip() for subscriber in subscriber_count]
        subscriber_list = subscriber_list[4::4]
        for channel, subcriber in zip(channel_list, subscriber_list):
            channel_sub_map.append({channel: subcriber})
    elif site=="tiktok" and metrics=="most-followers":
        channel_name=root.xpath("//div[contains(@style, 'float: left; width: 200px; line-height: 25px;')]/a")
        subscriber_count = root.xpath("//div[@style='float: left; width: 100px;']")
        channel_list = [channel.text for channel in channel_name]
        subscriber_list = [subscriber.text_content().strip() for subscriber in subscriber_count]
        subscriber_list = subscriber_list[4::4]
        for channel, subcriber in zip(channel_list, subscriber_list):
            channel_sub_map.append({channel: subcriber})
    elif site=="tiktok" and metrics=="most-likes":
        channel_name=root.xpath("//div[contains(@style, 'float: left; width: 200px; line-height: 25px;')]/a")
        subscriber_count = root.xpath("//div[@style='float: left; width: 100px;']")
        channel_list = [channel.text for channel in channel_name]
        subscriber_list = [subscriber.text_content().strip() for subscriber in subscriber_count]
        subscriber_list = subscriber_list[6::4]
        # print(subscriber_list[0:200])

        
        for channel, subcriber in zip(channel_list, subscriber_list):
            channel_sub_map.append({channel: subcriber})
    elif site=="dlive" :
        channel_name=root.xpath("//div[contains(@style, 'float: left; width: 270px; line-height: 25px;')]/a")
        subscriber_count = root.xpath("//div[@style='float: left; width: 120px;']")
        channel_list = [channel.text for channel in channel_name]
        subscriber_list = [subscriber.text_content().strip() for subscriber in subscriber_count]
        subscriber_list = subscriber_list[2::2]
        for channel, subcriber in zip(channel_list, subscriber_list):
            channel_sub_map.append({channel: subcriber})
        
    else:
        channel_sub_map=get_mostsubs(soup)
    
    
    return channel_sub_map
        
    
def saveFile(site_name,url,by=None):
    folder=f"./{site_name}"
    os.makedirs(folder, exist_ok=True)
    data=get_data(url)
    data = [{"Name": list(channel_sub.keys())[0], "Followers": list(channel_sub.values())[0]} for channel_sub in data]
    df=pd.DataFrame(data)
    file_path=os.path.join(folder,f'{site_name}_{by}.csv')
    df.to_csv(file_path,index=False,encoding="utf-8")
    
if __name__ == "__main__":
    session_cookies = login(driver,"","")    
    for link in URLS:
        site,metrics=extract_site_and_metric(link)
        saveFile(f"{site}",link,f"{metrics}")
    

    
    

    
    
    


