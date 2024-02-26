from bs4 import BeautifulSoup
import pandas as pd
from lxml import html
import os
import time
from login import login,create_driver


driver = create_driver()

driver.maximize_window()



BASE_URL="https://socialblade.com/youtube/top/country/" 
def get_soup(url):
    """return soup object of any url"""
    driver.get(url)
    time.sleep(5)  
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    return soup
        
    
def map_country(soup):
    """return a dictionary mapping each country with their code. Not needed in case for other site except youtube"""
    country_mapping = {}
    country_element = soup.find('select', id='CountrySelectorSidebar')
    country_list = country_element.find_all('option')
    start_parsing = False
    for country in country_list:
        if country.text.strip() == '-----ALPHABETICAL LIST-----':
            start_parsing = True
            continue
        if start_parsing:
            try:
                country_code = country['value']
                country_name = country.text
                country_mapping[country_name] = country_code
            except:
                continue
    return country_mapping
    
def get_mostsubs(soup):
    """return top5000 most subscribed youtube channel from each country"""
    channel_sub_map = []
    root = html.fromstring(str(soup))
    channel_name = root.xpath("//div[contains(@style, 'float: left; width: 350px; line-height: 25px;')]/a")
    subscriber_count = root.xpath("//div[@style='float: left; width: 150px;']")
    channel_list = [channel.text for channel in channel_name]
    subscriber_list = [subscriber.text_content().strip() for subscriber in subscriber_count]
    subscriber_list = subscriber_list[2::2]
    for channel, subcriber in zip(channel_list, subscriber_list):
        channel_sub_map.append({channel: subcriber})
    
    return channel_sub_map

def save_to_csv(country_name, channel_sub_map):
    """save each country name as separate csv file with their most subscribed 50 yt channel and their sub count"""
    folder = "./youtube"
    os.makedirs(folder, exist_ok=True)
    data = [{"Channel": list(channel_sub.keys())[0], "Subs": list(channel_sub.values())[0]} for channel_sub in channel_sub_map]
    df = pd.DataFrame(data)
    file_path = os.path.join(folder, f'{country_name}.csv')
    df.to_csv(file_path, index=False, encoding="utf-8")
    

if __name__ == "__main__":
    session_cookies = login(driver,"your email address","your email address")    
    soup = get_soup(BASE_URL)
    country_mapping = map_country(soup)
   
    for country_name, country_code in country_mapping.items():
    

        country_url = f"{BASE_URL}{country_code}/mostsubscribed"
        country_soup = get_soup(country_url)
        channel_sub_map = get_mostsubs(country_soup)
        save_to_csv(country_name, channel_sub_map)
