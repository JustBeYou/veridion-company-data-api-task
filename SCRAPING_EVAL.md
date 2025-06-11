Scraping evaluation
===

## Iteration 1 - MVP (only alive domains)

```
⚡ 49.7s
1076 datapoints from 696 domains

... forgot to copy domain success rate ...

Phone Numbers
57%
Social Media
58%
Addresses
14%
Domains Attempted:
696
Successfully Scraped:
484
With Contact Pages:
315
```

## Iteration 2 - remove empty data points

remove some useless data

```
⚡ 44.0s
806 datapoints from 696 domains

51%
Domain Success
100%
Page Success
Phone Numbers
71%
Social Media
76%
Addresses
17%
Domains Attempted:
696
Successfully Scraped:
356
With Contact Pages:
252
```

## Iteration 3 - scrape all available links with common words, no external, depth 1, fix social media extraction bug

increased datapoints a little

```
June 11, 2025
⚡ 1m 15s
10:04 PM
1026 datapoints from 696 domains

47%
Domain Success
100%
Page Success
Phone Numbers
74%
Social Media
73%
Addresses
19%
Domains Attempted:
696
Successfully Scraped:
326
With Contact Pages:
233
```

## Iteration 4 - keep only social media profiles and improve phone number matching a bit

removed some

```
June 11, 2025
⚡ 1m 16s
10:32 PM
1088 datapoints from 696 domains

49%
Domain Success
100%
Page Success
Phone Numbers
74%
Social Media
71%
Addresses
19%
Domains Attempted:
696
Successfully Scraped:
341
With Contact Pages:
249
```

## Iteration 5 - use address parsing library, increase timeout to 3 seconds

looks good enough for the challenge

```
June 11, 2025
⚡ 2m 41s
11:02 PM
1145 datapoints from 696 domains

55%
Domain Success
100%
Page Success
Phone Numbers
73%
Social Media
70%
Addresses
51%
Domains Attempted:
696
Successfully Scraped:
384
With Contact Pages:
276
```
