import scrapy
from scrapy_splash import SplashRequest


class MdSpider(scrapy.Spider):
    name = 'md'
    allowed_domains = ['towardsdatascience.com']
    # start_urls = ['http://towardsdatascience.com/archive/2020/01/01/']

    # fuction to generater page links
    def link_generator():
        print('INSIDE LINK GENERATOR')
        url = 'http://towardsdatascience.com'
        year = '2020'
        links = []
        # format month and day
        for month in range(1, 2):
            if month in [1, 3, 5, 7, 8, 10, 12]:
                n_days = 31
            elif month in [4, 6, 9, 11]:
                n_days = 30
            else:
                n_days = 28
            for day in range(1, n_days + 1):

                month, day = str(month), str(day)

                if len(month) == 1:
                    month = f'0{month}'
                if len(day) == 1:
                    day = f'0{day}'

                page = f'{url}/archive/{year}/{month}/{day}'  
                links.append(page)
        return links     

    # calling the link generator function to store all the main page links in a list
    main_links = link_generator()

    script3 = '''
        function main(splash, args)
            local ok, result = splash:with_timeout(function()
            --enabling the return of splash response
            splash.request_body_enabled = true
            --set your user agent
            splash:set_user_agent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36')
            splash.private_mode_enabled = false
            
            --visit the given url
            local url = args.url
            local ok, reason = splash:go(url)
            if ok then
                --if no error found, wait for 1 second for the page to render
                splash:wait(1)
                --store the html content in a variable
                local content = assert(splash:html())
                --return the content
                return content
            end
        end,3600)
        
        return result
        
        end
    '''

# This is the first function scrapy will check
    def start_requests(self):
        # iterating through all the links generated
        for link in self.main_links:
            # send request to each page and return the html content to the parse function
            yield scrapy.Request(url=link,callback=self.parse,
            headers={
                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })

    # This function receives the response as html content
    def parse(self, response):
        
        page_links = response.xpath(".//div[@class='postArticle-readMore']/a/@href").getall()
        page_links = [link.split('?')[0] for link in page_links]

        for link in page_links:
            yield SplashRequest(url=link,callback=self.get_content,
            endpoint='execute',args={'lua_source':self.script3,'timeout':3600})

    def get_content(self,response):

        header = response.xpath("//div[contains(@class,'n p')]/div/div/h1/text()").get()
        sub_header = response.xpath("(//div[contains(@class,'n p')]/div/div/h2)[1]/text()").get()
        article = ' '.join(response.xpath("//div[@class='s']/article/div/section/div/div//text()").extract()).strip()
        claps = response.xpath("//div[contains(@class,'n')]/div/div[1]/span[1]/div/div[2]/div/p/button/text()").get()
        tags = response.xpath("//ul/li/a/text()").getall()

        yield {
            'header':header,
            'sub_header':sub_header,
            'article':article,
            'tag':tags,
            'clap':claps
        }
