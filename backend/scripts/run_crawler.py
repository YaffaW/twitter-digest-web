"""Simple script to run the crawler once or in loop (for dev)."""
from app.core import crawler
import sys


def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'once':
        cfg = crawler.load_config()
        accounts = cfg.get('accounts', [])
        queries = cfg.get('queries', [])
        res = crawler.crawl_once(accounts, queries, max_per=cfg.get('max_per', 20))
        print('Fetched', len(res), 'tweets')
    else:
        cfg = crawler.load_config()
        interval = cfg.get('poll_interval', 60)
        crawler.start_in_thread(interval)
        print('Crawler started in background thread. Press Ctrl+C to exit.')
        try:
            import time
            while True:
                time.sleep(3600)
        except KeyboardInterrupt:
            print('Stopping')


if __name__ == '__main__':
    main()
