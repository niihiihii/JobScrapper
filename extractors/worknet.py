from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

def get_worknet_page_count(keyword):
  options = Options()
  options.add_argument("--no-sandbox")
  options.add_argument("--disable-dev-shm-usage")
  
  browser = webdriver.Chrome(options=options)
  
  base_url = "https://www.work.go.kr/wnSearch/unifSrch.do?regDateStdt=&regDateEndt=&colName=tb_workinfo&dtlSearch=&query="
  browser.get(f"{base_url}{keyword}")

  soup = BeautifulSoup(browser.page_source, "html.parser")
  pagination = soup.find('nav', class_="pagination")
  pages = pagination.find_all('a', recursive = False)
  count = len(pages)
  if count <= 8:
    return count+1
  else:
    return 10

def extract_worknet_jobs(keyword):
  options = Options()
  options.add_argument("--no-sandbox")
  options.add_argument("--disable-dev-shm-usage")
  
  browser = webdriver.Chrome(options=options)
  
  results = []
  
  pages = get_worknet_page_count(keyword)
  print(f"Found {pages} pages")
  for page in range(pages):
    base_url = "https://www.work.go.kr/wnSearch/unifSrch.do?regDateStdt=&regDateEndt=&colName=tb_workinfo"
    final_url = f"{base_url}&pageIndex={page+1}&dtlSearch=&query={keyword}"
    print("Requesting", final_url)
    browser.get(final_url)
    
    soup = BeautifulSoup(browser.page_source, "html.parser")
    job_list = soup.find('div', class_="result-recruit-list")
    jobs = job_list.find_all('li')
    
    for job in jobs:
      
      anchor = job.select_one('div a')
      link = anchor['href']
      company = job.select_one('div span')
      location_div = job.find('div', class_="cp-info")
      location_p = location_div.find_all('p')
      location_span = location_p[1].find_all('span')
      location = location_span[0]
      position = anchor.get_text()
      job_data = {
            'link': f"https://www.work.go.kr{link}",
            'company': company.string.replace(",", " "),
            'location': location.get_text().replace("근무지", "").strip().replace(",", " "),
            'position': position.strip().replace(",", " ")
      }
      
      # 평소에는 location_span == [근무지, 정보제공처]의 구조로 되어있으나
      # 근무지 미기재시 location_span == [정보제공처]가 돼서 정보제공처를 긁어오는 오류 발생
      # if 제어문 추가로 해결
      
      if len(location_span) == 1:
        job_data['location'] = "비공개"
      results.append(job_data)
  return results