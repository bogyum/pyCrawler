# pyCrawler
Arirang news crawler using python
------------------------------------

## Version 0.1.0

URL: http://www.arirang.com/News/News_List.asp?sys_lang=Eng&category=?

1. 실행 방법
  '>' $ProjectHome/script/crawling.sh [개발서버환경] [크롤링뉴스작성날짜] [로그파일명]
  
  - 개발서버환경: LOCAL | DEV | TEST  :: $ProjectHome/src/config/config.json 파일에 설정되어 있는 개발환경 구분
  - 크롤링뉴스작성날짜: 크롤링할 뉴스의 작성 날짜 - yyyy-MM-DD 형식. 예> 2020-04-05
  - 로그파일명: crawling.sh 에 포함되어 있으므로, 생략
     
2. 제약
  - 크롤링 대상 뉴스를 찾을 때, 위 URL 에 노출되는 리스트의 첫번째 페이지에 있는 정보만을 가지고 대상 날짜를 비교하여 가져온다. 이 부분은 페이지 순회를 하면서, 원하는 날짜의 뉴스를 가져올 수 있도록 향후 수정되어야 한다.
  - 개발서버환경 구성은 LOCAL 의 경우는 각자의 개발 PC(Laptop) 환경으로 구성하여야 하며, DEV 혹은 TEST 는 나중에 사용할 서버에 셋팅을 해야 한다. DEV 의 경우는 테스트 환경으로 팀원들이 모두 접근이 가능한 서버가 되어야 할 것이고, TEST 의 경우는 현재 사용할 수 있는 자원이 많이 없으므로 REAL 과 동일하게 취급하여 나중에 서비스가 실제로 이루어질 서버로 구성한다.
  - 개발 환경은 anaconda 를 이용하여 셋팅하는 것을 권장한다. 샘플 anaconda image 는 다음 미팅때 배포하여 공유
