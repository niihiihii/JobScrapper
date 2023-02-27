from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

def get_indeed_page_count(keyword):
  options = Options()
  options.add_argument("--no-sandbox")
  options.add_argument("--disable-dev-shm-usage")
  
  browser = webdriver.Chrome(options=options)

  base_url = "https://kr.indeed.com/jobs?q="
  browser.get(f"{base_url}{keyword}")

  soup = BeautifulSoup(browser.page_source, "html.parser")
  pagination = soup.find("nav", attrs={"aria-label":"pagination"})
  pages = pagination.find_all("div", recursive = False)
  count = len(pages)

  #페이지가 1개일 경우 count == 0
  if count == 0:
    print("indeed에서 1페이지를 발견했습니다.")
    return 1

  #페이지가 2개일 경우 count == 3
  elif count == 3:
    print("indeed에서 2페이지를 발견했습니다.")
    return 2
    
  #start값에 큰 값을 부여할 경우 다음 페이지 버튼이 없어서 맨 끝 페이지로 이동한 것처럼 보이지만, 그 다음 페이지가 존재함
  #선택된 페이지(맨 끝 페이지)의 div a에서는 aria-label이 "pagination-page-current"로 표기됨
  #그러나 바로 앞 페이지의 div a의 경우, aria-label에 페이지 번호가 표시됨
  else:
    browser.get(f"{base_url}{keyword}&start=100000")

    soup = BeautifulSoup(browser.page_source, "html.parser")
    pagination = soup.find("nav", attrs={"aria-label":"pagination"})
    pages = pagination.find_all("div", recursive = False)
    page_anchor = pages[-2].find('a')
    count = int(page_anchor['aria-label']) + 2
  
    if count <= 10:
      print(f"indeed에서 {count}페이지를 발견했습니다.")
      return count
      
    else:
      print(f"indeed에서 {count}페이지를 발견했습니다. 10페이지만 스크래핑을 진행합니다")
      return 10

def extract_indeed_jobs(keyword):
  options = Options()
  options.add_argument("--no-sandbox")
  options.add_argument("--disable-dev-shm-usage")
  
  browser = webdriver.Chrome(options=options)
  
  results = []
  
  pages = get_indeed_page_count(keyword)
  for page in range(pages):
    base_url = "https://kr.indeed.com/jobs"
    final_url = f"{base_url}?q={keyword}&start={page*10}"
    print("Requesting", final_url)
    browser.get(final_url)
    
    soup = BeautifulSoup(browser.page_source, "html.parser")
    job_list = soup.find('ul', class_="jobsearch-ResultsList")
    jobs = job_list.find_all('li', recursive = False)
    for job in jobs:
      zone = job.find('div', class_="mosaic-zone")
      if zone == None:
        anchor = job.select_one('h2 a')
        title = anchor['aria-label']
        link = anchor['href']
        company = job.find('span', class_="companyName")
        location = job.find('div', class_="companyLocation")
        
        #location.string이 아니라 location.get_text()를 쓴 이유:
        #location이 대전 +1지역 같은 형식으로 표시된 경우가 있는데 +1지역이 버튼으로 되어있어 
        #div태그 안에 또 다른 자식 태그가 발생해서 .string을 쓸 경우 None을 출력함
        
        job_data = {
              'link': f"https://kr.indeed.com{link}",
              'company': company.string.replace(",", " "),
              'location': location.get_text().replace(",", " "),
              'position': title.replace(",", " ")
        }
        results.append(job_data)
  return results