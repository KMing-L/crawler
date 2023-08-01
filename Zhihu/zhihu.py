import requests
from bs4 import BeautifulSoup as BS
import json
from typing import List, Dict
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
import selenium
import re


def get_zhihu_hot_urls() -> List[str]:
    """
    Get the hot urls list of zhihu

    Returns:
        The hot urls list of zhihu
    """
    url = "https://www.zhihu.com/hot"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15",
    }
    with open("Zhihu/config.json", "r") as f:
        config = json.load(f)
    headers["cookie"] = config["cookie"]
    resp = requests.get(url=url, headers=headers)
    soup = BS(resp.text, "lxml")
    hot_list = []
    for item in soup.find_all("div", class_="HotItem-content"):
        hot_list.append(item.find("a")["href"])
    return hot_list


def get_all_answers(qid: str) -> List[Dict]:
    """
    Get all answers of a question

    Args:
        qid: The id of the question

    Returns:
        The list of all answers
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15",
    }
    with open("Zhihu/config.json", "r") as f:
        config = json.load(f)
    headers["cookie"] = config["cookie"]

    url = f"https://www.zhihu.com/question/{qid}"
    resp = requests.get(url=url, headers=headers)
    soup = BS(resp.text, "lxml")
    sessionId = soup.find("script", id="js-initialData").text
    sessionId = re.findall(r'"sessionId":"(.*?)"', sessionId)[0]
    url = f"https://www.zhihu.com/api/v4/questions/{qid}/feeds?include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cattachment%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Cis_labeled%2Cpaid_info%2Cpaid_info_content%2Creaction_instruction%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cvip_info%2Cbadge%5B%2A%5D.topics%3Bdata%5B%2A%5D.settings.table_of_content.enabled&limit=5&offset=0&order=default&platform=desktop&session_id={sessionId}"
    answers = []
    while True:
        resp = requests.get(url=url, headers=headers)
        data = resp.json()["data"]
        answers.extend(data)
        if resp.json()["paging"]["is_end"]:
            break
        url = resp.json()["paging"]["next"]
    return answers


def get_all_answers_author(qid: str) -> List[str]:
    """"""
    chrome_opetions = ChromeOptions()
    chrome_opetions.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    driver = selenium.webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_opetions)
    driver.get(f"https://www.zhihu.com/question/{qid}")

    button_quit = driver.find_element(By.XPATH, '/html/body/div[5]/div/div/div/div[2]/button')
    button_quit.click()

    while True:
        driver.execute_script("window.scrollBy(0, -10);")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        if driver.find_elements(By.XPATH, '//*[@id="root"]/div/main/div/div/div[3]/div[1]/div/div[2]/a/button'):
            break
    
    authors = [item.text for item in driver.find_elements(By.CLASS_NAME, 'UserLink-link')]
    authors = [item for item in authors if item != '']
    return authors


if __name__ == "__main__":
    # hot_urls = get_zhihu_hot_urls()
    data = get_all_answers("613681273")
    authors = [
        d["target"]["author"]["name"] for d in data if d["target"]["type"] == "answer"
    ]
    print(authors)
    # print(get_all_answers_author("49176890"))
