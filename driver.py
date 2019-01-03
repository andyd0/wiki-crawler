from wiki_crawler import WikiCrawler


if __name__ == '__main__':
    crawler = WikiCrawler(wiki=None, max_crawls=1, ignore_invalids=True)
    crawler.crawl()
    crawler.plot_distribution()
