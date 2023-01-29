# URL Shortener Service Documentation

## Overview

The URL Shortener Service is a simple web service that shortens URLs and stores them in a Redis database for retrieval. It provides two methods for accessing the shortened URLs: `app.post("/shorten")` and `app.get("/{short_id}")`. The service also includes json logging and Prometheus metrics for monitoring.

## Methods

### app.post("/shorten")

This method takes a long URL as input and returns a shortened URL as output. The shortened URL and its corresponding long URL are stored in the Redis database.

### app.get("/{short_id}")

This method takes a `short_id` as input and returns the original long URL that was associated with the `short_id`. The `short_id` is used to retrieve the corresponding long URL from the Redis database. If the `short_id` is not found, an error message will be returned.

## Logging

The service uses logging to record important events and errors. Logs are in JSON format and include information such as the time the event occurred, the type of event, and any relevant details.

## Prometheus Metrics

Prometheus metrics are used to track various statistics about the service, such as the number of requests, the response times, and the success rate of the requests. These metrics can be used to monitor the performance and health of the service and to identify any issues that may need to be addressed.
