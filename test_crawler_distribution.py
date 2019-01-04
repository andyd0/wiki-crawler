from wiki_crawler import WikiCrawler


if __name__ == '__main__':
    # Ignore invalids set to True so that dead ends / cycles are excluded
    # in the counts. Average and the plot of the distribution of path lengths
    # to Philosophy will be shown when done
    crawler = WikiCrawler(wiki=None, max_crawls=2, ignore_invalids=True)
    crawler.crawl()
    crawler.plot_distribution()
