# Restaurant Review - Analytics

### Motivation
There is a vast amount of reviews based on user likes and tastes which needs to be analyzed to recognize user sentiment
and develop language based models for review generation and recommendation

### Objectives

1. Analyze the reviews for restaurants distributions, spatial mapping and statistics
2. Develop a review sentiment analysis model for ordinal regression of rating
3. Develop a review generation model based on Natural Language Generation
4. Develop a recommender system based on the review

### Data

* Restaurant data is acquired on census block groups based on high foot traffic data

* Reviews are scraped from maps and only 80% of reviews are taken where total reviews > 500

* The review scraper was based out of [Gaspa93's repo](https://github.com/gaspa93/googlemaps-scraper)

* Restaurants with 'Hotel' , 'Inn', 'Plaza' or 'Intercontinental' in their name were omitted due to scraping errors