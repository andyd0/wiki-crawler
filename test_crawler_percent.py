from wiki_crawler import WikiCrawler


if __name__ == '__main__':
    # Ignore invalids set to False so that dead ends / cycles are included
    # in the counts. Average and percent that lead to Philosophy will be
    # shown when done
    crawler = WikiCrawler(wiki=None, max_crawls=10, ignore_invalids=False)
    crawler.crawl()
