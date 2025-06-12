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
