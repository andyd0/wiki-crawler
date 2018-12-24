from bs4 import BeautifulSoup
import requests
import time

#%%
domain = "https://en.wikipedia.org"
sub_domain = "/wiki/Art"
random_sub = "/wiki/Special:Random"
# page = requests.get(domain + sub_domain)
# soup = BeautifulSoup(page.content, 'html.parser')

# test = soup.find_all('p', recursive="False")

# for element in test:
#     a_tags = element.find_all('a', recursive="False")
#     if 'href' in element and 'wiki' in element['href']:
#         print(element['href'])

# #%%
# for element in test:
#     a_tags = element.find('a', recursive="False")
#     try:
#         next_tag = a_tags['href']
#         break
#     except:
#         pass

#%%
import time
def traverse(link):
    page = requests.get(link)
    soup = BeautifulSoup(page.content, 'html.parser')
    ps = soup.find_all('p', recursive="False")
    next_link = ""
    for element in ps:
        a_tags = element.find('a', recursive="False")
        try:
            next_link = a_tags['href']
            break
        except:
            pass
    return next_link
#%%
target = "/wiki/Philosphy"
count = 0
while sub_domain != target:
    count += 1
    sub_domain = traverse(domain + sub_domain)
    time.sleep(2)
    if count > 10:
        break