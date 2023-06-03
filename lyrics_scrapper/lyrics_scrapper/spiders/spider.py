import re
import json
import scrapy
import datetime

from scrapy.utils.project import get_project_settings

class Lyric(scrapy.Spider):

    name = "Lyric Scrapper"

    base_url = "https://www.lyrics.com"

    genres = {
        "blues" : '/genre/Blues', 
        "brass military" : '/genre/Brass%20__%20Military',
        "classical" : '/genre/Classical', 
        "electronic" : '/genre/Electronic', 
        "folk,world,country" : '/genre/Folk,%20World,%20__%20Country', 
        "soul" : '/genre/Funk%20--%20Soul', 
        "hip hop" : '/genre/Hip%20Hop', 
        "jazz" : '/genre/Jazz', 
        "latin" : '/genre/Latin', 
        "non-music" : '/genre/Non-Music', 
        "pop" : '/genre/Pop', 
        "reggae" :'/genre/Reggae', 
        "rock" : '/genre/Rock',
        "stage screen" : '/genre/Stage%20__%20Screen'
    }

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.76'
    }

    def start_requests(self):

        for genre in self.genres:
            url_to_scrap = self.base_url + self.genres[genre]
            yield scrapy.Request(url_to_scrap, headers=self.headers, meta={'genre':genre, "current_page":1}, callback=self.parse_genre)

    def parse_genre(self, res):
        
        lyric_links = res.css("p.lyric-meta-title a::attr(href)").getall()
        
        max_page = res.css("div.pager a.rc5::text").getall()
        max_page = max([int(x) for x in max_page])

        for link in lyric_links:
            yield scrapy.Request(self.base_url + link, headers=self.headers, meta=res.meta, callback=self.parse_lyric)

        if res.meta.get("current_page") < max_page:
            res.meta['current_page'] += 1
            url_to_follow = self.base_url + self.genres[res.meta.get("genre")] + "/" + str(res.meta.get('current_page'))
            yield scrapy.Request(url_to_follow, headers=self.headers, meta=res.meta, callback=self.parse_genre)
    
    def parse_lyric(self, res):

        style = res.css("div.lyric-infobox a.small::text").getall()
        if len(style)==2:
            style = style[-1]
        else:
            style = None
        
        lyric = res.css("pre.lyric-body").get()

        if(lyric == None):
            return

        clean_html = re.compile('<.*?>')
        lyric = re.sub(clean_html, '', lyric)
        clean_r =  re.compile('\r*?')
        lyric = re.sub(clean_r, '', lyric)

        title = res.css("h1.lyric-title::text").get()
        artist = res.css("h3.lyric-artist a::text").get()

        data = {
            'url' : res.request.url,
            'genre' : res.meta.get("genre"),
            'style' : style,
            'title' : title,
            'artist' : artist,
            'lyric' : lyric
        }

        yield data


#if __name__ == "__main__":
#    from scrapy.crawler import CrawlerProcess
#    process = CrawlerProcess(get_project_settings())
#
#    process.crawl(Lyric)
#    process.start()
        

