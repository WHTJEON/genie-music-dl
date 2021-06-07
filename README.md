<p align="center">
<img width = 300px src="https://user-images.githubusercontent.com/57805304/120742890-d1926100-c532-11eb-8248-9f19e589d10f.png" />
</p>

<!-- <h1 align="center">IINA</h1> -->

<p align="center"><b>The Ultimate Genie Music Downloader</b></p>

---

## Features
* 단일 트랙 다운로드 (Download track)
* 앨범 전체 다운로드 (Download Album)
* 아티스트 전곡 다운로드 (Download Artist)
* 지니 플레이리스트 다운로드 (Download Playlist)
* 실시간 TOP 200 차트 다운로드 (Download Realtime Chart)
* 실시간 TOP 200 차트 보기 (Print Realtime Chart)
* 트랙, 앨범, 아티스트 검색 후 다운로드 (Search and Download)

## Getting Started

### Prerequisites
* Python 3.7 or later
* 지니뮤직 스트리밍 이용권 (종류 상관 X)

### Installation
1. Clone the repo
 ```sh
 $ git clone https://github.com/WHTJEON/genie-music-downloader.git
 $ cd genie-music-downloader
 ```
2. Install Required Packages
 ```sh
 $ pip install -r requirements.txt
 ```

## Instructions
1. Interactive Mode (More Features)
```
$ python3 genie-dl.py
```
<img width="720" alt="스크린샷 2021-06-05 오후 8 59 39" src="https://user-images.githubusercontent.com/57805304/120960806-8cbb3400-c797-11eb-93f4-14a956bb2bd1.png">

2. Argument Mode (-i "Song, Album, Artist, Playlist URL")
```
$ python3 genie-dl.py -i "https://www.genie.co.kr/detail/albumInfo?axnm=82038886"
```
<img width="720" alt="스크린샷 2021-06-05 오후 9 01 39" src="https://user-images.githubusercontent.com/57805304/120960799-8a58da00-c797-11eb-8406-4a0d7ba1b3ec.png">


## To be updated
* FLAC 다운로드 기능
* UI 개선
* Settings 
* Multi-Disc 앨범 다운로드 개선

## Legal Disclaimer
This was made with educational purposes only. Use at your own risk. 
