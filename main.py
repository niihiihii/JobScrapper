from extractors.indeed import extract_indeed_jobs
from extractors.wwr import extract_wwr_jobs
from extractors.worknet import extract_worknet_jobs

keyword = input("What do you want to search for?")

indeed = extract_indeed_jobs(keyword)
wwr = extract_wwr_jobs(keyword)
worknet = extract_worknet_jobs(keyword)

jobs = indeed + wwr + worknet

file = open(f"{keyword}.csv", "w", encoding="utf-8-sig")
file.write("Position,Company,Location,URL\n")

for job in jobs:
  file.write(f"{job['position']},{job['company']},{job['location']},{job['link']}\n")
  
file.close()

#indeed 1페이지 테스트 시 keyword = nest
#indeed 2페이지 테스트 시 keyword = golang+python
#indeed 3페이지 테스트 시 keyword = golang
#indeed 10페이지 이상 테스트 시 keyword = python