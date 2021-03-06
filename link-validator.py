#!/usr/bin/env python3
#
# link-validator.py
# Brandon Amos <http://bamos.io>

import argparse
import re
from urllib.request import urlopen
from urllib.parse import urljoin,urldefrag
from bs4 import BeautifulSoup, SoupStrainer

baseUrl = None
invalidWikiPages = []
visitedUrls = []

def validate(url):
  if url in visitedUrls: return

  visitedUrls.append(url)
  try:
    content = urlopen(url).read().decode("utf8")
  except:
    # Assume the content is binary.
    return

  wikiUrls = []
  invalidUrls = []
  # This may see redundant, but without the `.find_all('a')`, soup will also
  # contain the `DocType` element which does not have an `href` attribute.
  # See <http://stackoverflow.com/questions/17943992/beautifulsoup-and-soupstrainer-for-getting-links-dont-work-with-hasattr-returni>.
  soup = BeautifulSoup(content, parse_only=SoupStrainer('a', href=True)).find_all('a')
  for externalUrl in soup:
    fullExternalUrl = urljoin(url, urldefrag(externalUrl['href']).url)
    if baseUrl in fullExternalUrl and \
        not fullExternalUrl.endswith('/_history'):
      if externalUrl.has_attr('class') and 'absent' in externalUrl['class']:
        invalidUrls.append(fullExternalUrl)
      else:
        wikiUrls.append(fullExternalUrl)

  if len(invalidUrls) > 0:
    invalidWikiPages.append((url, invalidUrls))

  for wikiUrl in wikiUrls:
    if wikiUrl not in visitedUrls:
      validate(wikiUrl)

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('url', type=str,
      help='The base link to the GitHub Wiki to scrape. ' +
      'Example: http://github.com/bamos/github-wiki-link-validator/wiki')
  args = parser.parse_args()

  baseUrl = args.url
  validate(args.url)

  if len(invalidWikiPages) == 0:
    print("No invalid links found.")
  else:
    for url, invalidUrls in invalidWikiPages:
      print("+ " + url)
      for invalidUrl in invalidUrls:
        print("  + " + invalidUrl)
