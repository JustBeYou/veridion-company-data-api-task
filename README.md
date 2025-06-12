Company Data API (SW Engineer)
===

# Overview

**Disclaimer**: I did use LLM tools (ChatGPT, Claude, Cursor) for speeding up development as I would do for any day
to day work.

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

Merging the scraped data with the CSV was straightforward. All data is indexed by the domain (one record per unique domain).
I chose to import the data into ElasticSerach, because I am familiar enough with it and it's a widely used software.

1. After every scraper run, the new data is imported into ElasticSerach merged with old entries (no duplicates are kept, old data is still around)
2. The schema for ES chosen is:
   * `text` for `address`, `company names` to allow partial and fuzzy matches
   * `keyword` for phone numbers, social media links to allow perfect matches
3. Only **37.7%** of companies from the sample CSV have datapoints found during scraping.

![Kibana showing statistics about the scraped data.](https://github.com/user-attachments/assets/68164548-ed89-4e02-97b1-baab795c1d6e)

TBD API

## Bonus points
