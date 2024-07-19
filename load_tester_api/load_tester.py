import aiohttp
import asyncio
import time
import logging
from .result import TestResult  # Assuming you have these modules
from .errors import URLCheckError
from .utils import validate_url
from urllib.parse import urlparse


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
        self.results.server_hostname = urlparse(url).hostname
        self.results.server_port = urlparse(url).port or (
            80 if urlparse(url).scheme == "http" else 443
        )
        self.results.document_path = urlparse(url).path
        self.results.payload = payload
        self.results.concurrency = concurrency
        self.results.qps = qps

    async def check_url(self):
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
        async with sem:
            try:
                start_time = time.perf_counter()  # Start time for total
                tcp_start_time = time.perf_counter()
                async with session.request(
                    self.method, self.url, headers=self.headers, data=self.payload
                ) as response:
                    connect_time = (
                        time.perf_counter() - tcp_start_time
                    )  # Time to establish the connection

                    end_write_time = (
                        time.perf_counter()
                    )  # Time right after connection is established and request is sent
                    content = await response.read()
                    begin_read_time = (
                        time.perf_counter()
                    )  # Time after reading the response

                    done_time = time.perf_counter()

                    wait_time = (
                        begin_read_time - end_write_time
                    )  # Time spent waiting to read response
                    processing_time = (
                        done_time - begin_read_time
                    )  # Time to process the response
                    total_time = done_time - start_time  # Total time for the request

                    self.results.add_times(
                        connect_time, wait_time, processing_time, total_time
                    )
                    self.results.add_transfer(len(content), response.headers)

                    if response.status != 200:
                        self.results.add_error(
                            f"Request failed with status: {response.status}"
                        )
                        self.logger.warning(
                            f"Request failed with status: {response.status}"
                        )

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
        try:
            validate_url(self.url)
            await self.check_url()
            sem = asyncio.Semaphore(self.concurrency)
            async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(limit_per_host=self.concurrency)
            ) as session:
                tasks = []
                start_time = time.perf_counter()
                for _ in range(self.total_requests):
                    if self.qps:
                        await asyncio.sleep(1 / self.qps)
                    tasks.append(self.fetch(session, sem))
                await asyncio.gather(*tasks)
                end_time = time.perf_counter()
                self.results.total_test_time = end_time - start_time
        except URLCheckError:
            self.results.failed_requests = self.total_requests
            self.results.invalid_url_errors = self.total_requests
            self.results.total_test_time = 0
            self.logger.error("Invalid or unresponsive URL. Exiting...")
            return

    def get_results(self):
        return self.results
