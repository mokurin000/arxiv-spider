from os import makedirs, path
from urllib.error import ContentTooShortError, HTTPError
from http.client import RemoteDisconnected

from arxiv import Client, Search, SortCriterion
from loguru import logger

OUTPUT_DIR = "./downloads"


def main():
    # search for 1000 papers related to traffic, relanvance first
    search = Search(query="traffic", max_results=1000, sort_by=SortCriterion.Relevance)
    page_size = 100

    api_client = Client(page_size=page_size)

    makedirs(OUTPUT_DIR, exist_ok=True)
    for page in range(10):
        for paper in api_client.results(search, offset=page * page_size):
            filename = paper._get_default_filename()
            filepath = path.join(OUTPUT_DIR, filename)
            if path.exists(filepath):
                continue

            try:
                logger.info(f"started: {filename}")
                new_file = paper.download_pdf(dirpath=OUTPUT_DIR)
                logger.info(f"saved: {new_file}")
            # withdraw case: not found
            except HTTPError:
                logger.error(f"withdraw: {filename}")
            # arxiv bug or network issue
            except ContentTooShortError:
                """
                Content-Length is the file size in bytes from host server, in the HTTP protocol.
                This case, arxiv gives us bigger content-length than real data it sent.
                Might be network issue or server-side bug of arxiv.org.
                """
                logger.error(f"content-length error: {filename}")
            # network issue, unexpected connection close.
            except RemoteDisconnected:
                logger.error(f"connection closed: {filename}")


if __name__ == "__main__":
    main()
