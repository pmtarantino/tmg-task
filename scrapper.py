import os
import re
import argparse
import concurrent.futures
from bs4 import BeautifulSoup
from tqdm import tqdm
from retry_requests import retry

class Scrapper:

    SAVE_DIR = "contents"
    PARALLEL_CONNECTIONS = 10
    HEADERS = { 'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36"}
    TIMEOUT = 10

    def __init__(self, file):
        self.file = file
        self.websites = []

    def _slugify(self, text):
        return re.sub("https?://","",text)

    def _save_file(self, filename, contents):
        # Clean a bit the content
        filename = self._slugify(filename)
        file_lines = list(
            filter(None, map(str.strip, contents.split(sep="\n"))))
        with open(Scrapper.SAVE_DIR + "/" + filename, 'a', encoding='utf8') as f:
            f.write("\n".join(file_lines))

    def _filter_links(self, links, website):
        links = [link for link in [x.get('href') for x in links] if link]
        clean_links = []
        for link in links:
            link = link.lower()
            # https://bugs.python.org/issue32958
            if len(link) > 64 \
                    or link.startswith(("..", "/..", "javascript", "mailto")) \
                    or link.endswith((".pdf", ".jpg", ".png", ".gif")):
                continue
            if link.startswith("http"):
                if link.startswith(website):
                    clean_links.append(link)
            else:
                link = "/" + link if not link.startswith("/") else link
                clean_links.append(website + link)
        return list(set(clean_links))[0:20]

    def _request_website(self, url):
        try:
            req_session = retry()
            page = req_session.get(url, headers=Scrapper.HEADERS, timeout=Scrapper.TIMEOUT)
            content_type = page.headers.get('content-type')
            if page.status_code != 200 or not content_type.strip().startswith("text/html"):
                return False

            return BeautifulSoup(page.content, 'html.parser')
        except Exception as e:
            return False

    def _get_multiple_content(self, links):
        with concurrent.futures.ThreadPoolExecutor(max_workers=Scrapper.PARALLEL_CONNECTIONS) as ex:
            future_contents = (ex.submit(self._request_website, link)
                               for link in links)
            all_contents = []
            for future in concurrent.futures.as_completed(future_contents):
                result = future.result()
                if result is not False:
                    all_contents.append(result.get_text())
            return "\n".join(all_contents)

    def _get_content(self, website):
        structure = self._request_website(website)
        if structure:
            content_text = structure.get_text()
            self._save_file(website, content_text)
            
            links = self._filter_links(structure.find_all('a'), website)
            deep_content = self._get_multiple_content(links)
            self._save_file(website, deep_content)


    def read_file(self):
        try:
            file_object = open(self.file, "r")
            for line in file_object:
                self.websites.append(line.strip())
            file_object.close()

        except Exception as e:
            raise Exception("File does not exist")

    def get_websites_content(self):
        if not os.path.exists(Scrapper.SAVE_DIR):
            os.mkdir(Scrapper.SAVE_DIR)

        for website in tqdm(self.websites):
            try:
                self._get_content(website)
            except Exception as e:
                continue

    def quick_check(self):
        # Do a quick check to see if every website has its own file after scrapping.
        websites = len(self.websites)
        files = len([name for name in os.listdir(Scrapper.SAVE_DIR) if os.path.isfile(Scrapper.SAVE_DIR + "/" + name)])
        return (websites == files, (websites, files))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Parse websites and clustering them based on their topics.')
    parser.add_argument('--file', required=True, help='File that contains \
        the list of websites. Must be one website per line.')

    args = parser.parse_args()
    scrapper = Scrapper(args.file)
    scrapper.read_file()
    scrapper.get_websites_content()
    quick_check = scrapper.quick_check()
    assert quick_check[0], quick_check[1]