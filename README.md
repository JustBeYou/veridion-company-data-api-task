Company Data API (SW Engineer)
===

# Overview

**Disclaimer**: I did use LLM tools (ChatGPT, Claude, Cursor) for speeding up development as I would do for any day
to day work.

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
