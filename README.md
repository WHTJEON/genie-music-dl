<p align="center">
<img width = 300px src="https://user-images.githubusercontent.com/57805304/120742890-d1926100-c532-11eb-8248-9f19e589d10f.png" />
</p>

<!-- <h1 align="center">IINA</h1> -->

<p align="center"><b>The Ultimate Genie Music Downloader</b></p>

---

## Features (지원기능) 
* 단일 트랙 다운로드 (Download track)
* 앨범 전체 다운로드 (Download Album)
* 아티스트 전곡 다운로드 (Download Artist)
* 지니 플레이리스트 다운로드 (Download Playlist)
* 실시간 TOP 200 차트 다운로드 (Download Realtime Chart)
* 실시간 TOP 200 차트 보기 (Print Realtime Chart)
* 트랙, 앨범, 아티스트 검색 후 다운로드 (Search and Download)

## Requirements (요구사항)
* 지니뮤직 스트리밍 이용권이 결제되어있는 계정 (종류 상관 X)
* Python Packages (eda3, pyfiglet, pick)
```
$ pip install -r requirements.txt
```

## Instructions (사용방법)
1. 반응형 실행 후 옵션 선택
```
$ python3 genie-dl.py
```
<img width="720" alt="스크린샷 2021-06-05 오후 8 59 39" src="https://user-images.githubusercontent.com/57805304/120890975-0096f880-c641-11eb-857a-9a541b4a5fbb.png">

2. 인자 실행 (-i "Song, Album, Artist, Playlist URL")
```
$ python3 genie-dl.py -i "https://www.genie.co.kr/detail/albumInfo?axnm=82038886"
```
<img width="818" alt="스크린샷 2021-06-05 오후 9 01 39" src="https://user-images.githubusercontent.com/57805304/120891013-3f2cb300-c641-11eb-8fab-b14341925bd2.png">


## To be updated (업데이트 예정)
* FLAC 다운로드 기능
* UI 개선
* Settings 
* Multi-Disc 앨범 다운로드 개선

## Legal Disclaimer
This was made with educational purposes only. Use at your own risk. 
