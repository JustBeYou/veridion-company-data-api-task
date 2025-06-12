Company Data API (SW Engineer)
===

# Overview

**Disclaimer**: I did use LLM tools (ChatGPT, Claude, Cursor) for speeding up development as I would do for any day
to day work. I spent around 16 hours on the solution, ~ 2 work days.

**Note**: Please see the **in scope** and **out of scope** sections below to get a better understanding of what is included in the solution.

I build a fast (**3 minutes runtime**, single-threaded, async) web **crawler** using **Python Scrapy** with decent fill rates
(**~70%** for phone and social media links, **~50%** for addresses). The scraper outputs statistics which can be visualized
in the **dashboard** built with **Flask**, you can see historical runs. The historical runs were used to experiment with
better scraping strategies. The scraped data is joined and imported into **ElasticSearch** and exposed by a **Flask** API.

You can run the project yourself by using the following command:

```
docker compose up # The scraper will start automatically, you should be able to see data in the dashboard after ~3 minutes
```

* **Scraper dashboard** - http://localhost:5000
* **Kibana** - http://localhost:5601
* **API** - http://localhost:5000/api/search

Example API call:
```bash
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "name": ["Acme Corporation", "Acme Corp"],
    "phone": ["555-123-4567", "+1-555-123-4567"],
    "urls": ["https://www.acme.com", "acme.com"],
    "address": ["123 Main St, Anytown USA", "123 Main Street"]
  }'
```

Example response:
```json
{
  "company": {
    "company_names": [
      "1st American Mortgage Corporation"
    ],
    "domain": "1stamc.com"
  },
  "found": true,
  "score": 29.686008,
  "search_criteria": {
    "addresses": [
      "123 Main St, Anytown USA",
      "123 Main Street"
    ],
    "cleaned_urls": [
      "acme.com",
      "acme.com"
    ],
    "names": [
      "Acme Corporation",
      "Acme Corp"
    ],
    "normalized_phones": [
      "5551234567",
      "15551234567"
    ]
  }
}
```

## In Scope

* Software: Fast scraper, dashboard for visualizing results, ElasticSearch & Kibana, API for serving results
* Report: analysis of scraper evaluation, analysis of API performance
* Practices: Acceptance Test Driven Development (ATDD), automated quality checks
  for each commit (linting, type-checking, formatting), automation for common tasks via Makefiles,
  development and "production-like" environment for running the application via Docker and Compose

## Out of Scope

* Authentication, secrets and other security configs
* CI & CD pipelines on Github Actions to test and deploy the app on each push
* k8s or Nomand instead of docker-compose (not really ment for production workloads)
* Runtime monitoring (atm, we have only post-factum statistics and some dirty logging)
* Support for multi-process (horizontal scaling) for scraping and ingesting data
* Proper ogranization of the project, split into multiple services (everything is bundled into a single Python package)

# Solution

## Data extraction

I appraoched data extraction in an "evaluation-driven" way, meaing I've built a dumb PoC scrapper, a statistics collector and
a dashboard to visualize it for the first milestone. Afterwards, I ran multiple experiments to identify which data extraction
rules better suit our usecase. Some raw notes about the experiments can be found in [SCRAPING_EVAL.md](./SCRAPING_EVAL.md).

1. One of the first thing to notice was that a lot of domains were no longer alive, only **55% domains** produced datapoints in the end
2. The best identified strategies for scraping speed and accuracy were:
  * scrape only pages that have a high chance of being static, the ones having words like `contact`, `about` etc. in their URLs
  * scrape only at depth 1 (to avoid spending too much time on useless pages)
  * do NOT scrape external links
  * extract social media links using a large list of known networks (generated with ChatGPT, contains both long and short domain names like `fb.com`)
  * extract only the social media links that look like pages/profiles/channels using RegEx (reduces noise a lot)
  * use comprehensive RegExes for phone numbers for multiple formats and separators (spaces, dashses etc)
  * extract addreses from html elements having a proper label
  * use `pyap` for matching addresses (it has a huge list of RegExes for many formats)
3. Results using the best scraping strategy:
  * **Datapoints: 1242**
  * **Alive domains: 696**
  * **Domain scrape rate (only alive): 54% (377/696)**
  * **Phone numbers fill rate: 73%**
  * **Social media fill rate: 70%**
  * **Address fill rate: 52%**
4. The process ran in **3m 28s** in single-threaded mode with 32 concurrent requests.

![Results from the best scraper run.](https://github.com/user-attachments/assets/6b7758bb-749c-4e04-933e-688f198ef30c)

## Data retrieval

### Importing data into ES

Merging the scraped data with the CSV was straightforward. All data is indexed by the domain (one record per unique domain).
I chose to import the data into ElasticSerach, because I am familiar enough with it and it's a widely used software.

1. After every scraper run, the new data is imported into ElasticSerach merged with old entries (no duplicates are kept, old data is still around)
2. The schema for ES chosen is:
   * `text` for `address`, `company names` to allow partial and fuzzy matches
   * `keyword` for phone numbers, social media links to allow perfect matches
3. Only **37.7%** of companies from the sample CSV have datapoints found during scraping.

![Kibana showing statistics about the scraped data.](https://github.com/user-attachments/assets/68164548-ed89-4e02-97b1-baab795c1d6e)

### Exposing the API

The API is a simple Flask POST route that takes as input a list of values for each field type we seen until now (names, phone numbers, urls, addresses) and performs
the following operations:

1. Input data is normalized - phone numbers are kept as numbers only, protocol and `www` subdomain is removed from urls
2. We perform a ElasticSearch query with multiple clauses:
  * fuzzy match for provided names against the stored names (BOOST: names have higher boost values)
  * term match for exact names
  * fuzzy match for provided names after processing: split names by capital letters and abbreviations
  * term match for phone numbers (BOOST: medium values for phones and links as there may be collisions)
  * term match for all links
  * fuzzy match for addresses (BOOST: addresses have lower values as there is a lot of noise)
3. We return the entry with the highest score (if any).

![Showcase of a few responses from the CSV.](https://github.com/user-attachments/assets/7106a0f2-5429-45ce-9824-3227a1fcce15)

## Bonus points

Some ideas about how one could evaluate the quality of the macthes:
* use the ElasticSearch score as a guide (but it is influenced by boost values)
* create a human-crafted dataset with perfect matches, compare similarity to perfect matches
* semantic scoring comparing the input entry with the result using LLMs or other ML-based technique (should be explored how such an evaluation model may be trained)
