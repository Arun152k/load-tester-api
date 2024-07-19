import aiohttp
import asyncio
import time
import logging
from .result import TestResult  # Importing TestResult for recording test results
from .errors import URLCheckError  # Importing custom error for URL check failures
from .utils import validate_url  # Importing URL validation utility
from urllib.parse import urlparse  # For parsing the URL


class LoadTester:
    def __init__(
        self,
        url,
        concurrency=10,
        total_requests=100,
        method="GET",
        headers=None,
        payload=None,
        qps=None,
    ):
        # Initialize the LoadTester with the provided parameters
        self.url = url
        self.concurrency = concurrency
        self.total_requests = total_requests
        self.method = method
        self.headers = headers if headers else {}
        self.payload = payload
        self.qps = qps
        self.logger = logging.getLogger("LoadTester")
        self.logger.setLevel(logging.INFO)
        self.results = TestResult(total_requests)

        # Parse URL components for result recording
        parsed_url = urlparse(url)
        self.results.server_hostname = parsed_url.hostname
        self.results.server_port = parsed_url.port or (
            80 if parsed_url.scheme == "http" else 443
        )
        self.results.document_path = parsed_url.path
        self.results.payload = payload
        self.results.concurrency = concurrency
        self.results.qps = qps

    async def check_url(self):
        # Check if the URL is reachable
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.url) as response:
                    if response.status >= 400:
                        self.logger.error(
                            f"URL check failed with status: {response.status}"
                        )
                        raise URLCheckError(
                            f"URL check failed with status: {response.status}"
                        )
            return True
        except Exception as e:
            self.logger.error(f"URL check failed: {e}")
            raise URLCheckError(f"URL check failed: {e}")

    async def fetch(self, session, sem):
        # Perform a single request and record timing and other metrics
        async with sem:
            try:
                start_time = (
                    time.perf_counter()
                )  # Start time for total request duration
                async with session.request(
                    self.method, self.url, headers=self.headers, data=self.payload
                ) as response:
                    connect_time = (
                        time.perf_counter() - start_time
                    )  # Time to establish the connection

                    end_write_time = time.perf_counter()  # Time after request is sent
                    content = await response.read()  # Read response content
                    begin_read_time = (
                        time.perf_counter()
                    )  # Time after reading response starts

                    done_time = time.perf_counter()  # Time when request is completed

                    # Calculate timing metrics
                    wait_time = begin_read_time - end_write_time
                    processing_time = done_time - begin_read_time
                    total_time = done_time - start_time

                    # Record timing and transfer metrics
                    self.results.add_times(
                        connect_time, wait_time, processing_time, total_time
                    )
                    self.results.add_transfer(len(content), response.headers)

                    # Log and record errors if request failed
                    if response.status != 200:
                        self.results.add_error(
                            f"Request failed with status: {response.status}"
                        )
                        self.logger.warning(
                            f"Request failed with status: {response.status}"
                        )

                    # Record server software and document length
                    if self.results.server_software is None:
                        self.results.server_software = response.headers.get(
                            "Server", "Unknown"
                        ).split(" ")[0]

                    if self.results.document_length == 0 and response.status == 200:
                        self.results.document_length = len(content)

                    if self.payload:
                        self.results.total_body_sent += len(self.payload)

            except aiohttp.ClientConnectorError as e:
                self.results.failed_requests += 1
                self.results.connection_errors += 1
                self.logger.error(f"Connection error: {e}")

            except aiohttp.ClientOSError as e:
                self.results.failed_requests += 1
                self.results.read_errors += 1
                self.logger.error(f"OS error: {e}")

            except aiohttp.ClientPayloadError as e:
                self.results.failed_requests += 1
                self.results.read_errors += 1
                self.logger.error(f"Payload error: {e}")

            except aiohttp.InvalidURL as e:
                self.results.failed_requests += 1
                self.results.invalid_url_errors += 1
                self.logger.error(f"Invalid URL: {e}")

            except asyncio.TimeoutError as e:
                self.results.failed_requests += 1
                self.results.timeout_errors += 1
                self.logger.error(f"Timeout error: {e}")

            except Exception as e:
                self.results.failed_requests += 1
                self.logger.error(f"Request failed: {e}")

    async def run_test(self):
        # Run the load test with the specified parameters
        try:
            validate_url(self.url)  # Validate the URL
            await self.check_url()  # Check if the URL is reachable
            sem = asyncio.Semaphore(self.concurrency)  # Semaphore to limit concurrency
            async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(limit_per_host=self.concurrency)
            ) as session:
                tasks = []
                start_time = time.perf_counter()  # Start time for the entire test
                for _ in range(self.total_requests):
                    if self.qps:
                        await asyncio.sleep(1 / self.qps)  # Control request rate
                    tasks.append(self.fetch(session, sem))  # Create fetch tasks
                await asyncio.gather(*tasks)  # Run all tasks concurrently
                end_time = time.perf_counter()  # End time for the entire test
                self.results.total_test_time = end_time - start_time
        except URLCheckError:
            # Handle URL check failure
            self.results.failed_requests = self.total_requests
            self.results.invalid_url_errors = self.total_requests
            self.results.total_test_time = 0
            self.logger.error("Invalid or unresponsive URL. Exiting...")
            return

    def get_results(self):
        # Return the collected test results
        return self.results
