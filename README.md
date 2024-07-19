# Load Tester API

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Clone the Repository](#clone-the-repository)
  - [Install Dependencies](#install-dependencies)
- [Usage](#usage)
  - [Command Line Interface (CLI)](#command-line-interface-cli)
  - [Docker](#docker)
  - [Examples](#examples)
- [Tests](#tests)

## Overview
Load Tester API is a comprehensive HTTP load testing tool designed to simulate various loads on web services and measure their performance. The tool is built using `aiohttp` for asynchronous HTTP requests and provides detailed reports on the performance of the tested endpoints. Semaphores were used to perform concurrent requests. 

The Load Tester tool evaluates server performance by simulating concurrent HTTP requests. It consists of the LoadTester class for managing and executing tests, the TestResult class for collecting and summarizing metrics, and the generate_report function for producing a detailed performance report. The tool runs tests based on user-defined parameters (URL, concurrency, request count, etc.), measures various performance metrics, and provides a comprehensive report of latencies, transfer rates, and error rates. Results are saved in JSON format and printed for easy review.

## Features
- Asynchronous HTTP requests using `aiohttp`
- Configurable concurrency, total requests and qpos
- Supports multiple HTTP methods
- Custom headers and payloads
- Detailed performance metrics including connection times, request rates, and error rates
- Output results in JSON format
- Docker Containerization

## Installation

### Prerequisites
- Python 3.7+
- Docker (optional, for containerized execution)

### Clone the Repository

```bash
git clone https://github.com/your-username/load-tester-api.git

cd load-tester-api 
```

### Install Dependencies

1. Setup virtual environment:

    ```python -m venv venv```
  
    ```venv\scripts\activate.ps1```

2. Install the packages:

    ``` pip install -r requirements.txt ```

## Usage

### Command Line Interface (CLI)
The CLI allows you to run load tests directly from the command line.

```python -m load_tester_api.cli --url http://example.com --concurrency 10 --requests 100 --method GET ```

Arguments:

--url: The target URL to test (required)

--concurrency: Number of concurrent requests (default: 10)

--requests: Total number of requests to perform (default: 100)

--method: HTTP method to use for requests (default: GET)

--headers: Comma-separated list of headers (e.g., 'Key1, Key2')

--payload: Payload to send with the requests (for POST, PUT, etc.)

-- qps: Queries per Second (default: None)

The output is saved to outputs/cli

### Docker

You can run the load tester in a Docker container.

1. Building the Docker Image
2. ``` docker run --rm --url http://example.com --concurrency 10 --requests 100 --method GET ```

### Examples

You can run multiple requests and configurations using the script in the examples directory. This script demonstrates how to use the Load Tester API programmatically.

#### Running Examples
To run the example tests provided in examples/examples.py, execute the following command:

```python -m load_tester_api.examples.examples```

The script will perform various load tests and save the results in the specified output directory (outputs/batch).

Feel free to add more requests in examples.py as per needed.

### Tests

The tests directory contains unit tests for the Load Tester API.

Running Tests
To run the unit tests provided in tests/ut1.py, use the following command:

```python -m unittest load_tester_api.tests.ut1```

