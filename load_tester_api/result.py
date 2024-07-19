from statistics import mean, stdev
from urllib.parse import urlparse


class TestResult:
    def __init__(self, total_requests):
        self.total_requests = total_requests
        self.completed_requests = 0
        self.failed_requests = 0
        self.latencies = []
        self.connect_times = []
        self.wait_times = []
        self.processing_times = []
        self.total_transferred = 0
        self.html_transferred = 0
        self.server_software = None
        self.document_length = 0
        self.total_body_sent = 0
        self.errors = []
        self.total_test_time = 0
        self.server_hostname = None
        self.server_port = None
        self.document_path = None
        self.payload = None
        self.concurrency = None
        self.non_2xx_responses = 0
        self.write_errors = 0
        self.connection_errors = 0
        self.read_errors = 0
        self.status_code_errors = 0
        self.invalid_url_errors = 0
        self.timeout_errors = 0
        self.keep_alive_requests = 0
        self.qps = None

    def add_times(self, connect_time, wait_time, processing_time, total_time):
        self.connect_times.append(connect_time)
        self.wait_times.append(wait_time)
        self.processing_times.append(processing_time)
        self.latencies.append(total_time)
        self.completed_requests += 1

    def add_transfer(self, content_length, headers):
        headers_length = sum(
            len(k) + len(v) + 4 for k, v in headers.items()
        )  # 4 for ': ' and '\r\n'
        self.total_transferred += content_length + headers_length
        self.html_transferred += content_length

    def add_error(self, error):
        self.errors.append(error)
        self.failed_requests += 1

    def summary(self):
        total_time = self.total_test_time
        average_latency = mean(self.latencies) if self.latencies else 0
        requests_per_second = self.completed_requests / total_time if total_time else 0
        transfer_rate_received = (
            self.total_transferred / total_time / 1024 if total_time else 0
        )
        transfer_rate_sent = (
            self.total_body_sent / total_time / 1024 if total_time else 0
        )
        transfer_rate_total = (
            (self.total_transferred + self.total_body_sent) / total_time / 1024
            if total_time
            else 0
        )
        error_rate = (
            self.failed_requests / self.total_requests if self.total_requests else 0
        )

        summary = {
            "server_software": self.server_software,
            "server_hostname": self.server_hostname,
            "server_port": self.server_port,
            "document_path": self.document_path,
            "document_length": self.document_length,
            "concurrency_level": self.concurrency,
            "qps": self.qps,
            "total_requests": self.total_requests,
            "completed_requests": self.completed_requests,
            "failed_requests": self.failed_requests,
            "error_rate": f"{error_rate:.2%}",
            "write_errors": self.write_errors,
            "connection_errors": self.connection_errors,
            "read_errors": self.read_errors,
            "status_code_errors": self.status_code_errors,
            "invalid_url_errors": self.invalid_url_errors,
            "timeout_errors": self.timeout_errors,
            "keep_alive_requests": self.keep_alive_requests,
            "total_transferred": self.total_transferred,
            "html_transferred": self.html_transferred,
            "requests_per_second": requests_per_second,
            "time_per_request": average_latency * 1000,
            "transfer_rate_received": transfer_rate_received,
            "transfer_rate_sent": transfer_rate_sent,
            "transfer_rate_total": transfer_rate_total,
            "total_test_time": total_time,
        }
        if self.latencies and self.connect_times:
            latencies_sorted = sorted(self.latencies)
            connect_times_sorted = sorted(self.connect_times)
            wait_times_sorted = sorted(self.wait_times)
            processing_times_sorted = sorted(self.processing_times)

            summary["connection_times"] = {
                "min": min(self.connect_times) * 1000,
                "mean": mean(self.connect_times) * 1000,
                "median": connect_times_sorted[len(connect_times_sorted) // 2] * 1000,
                "max": max(self.connect_times) * 1000,
            }
            summary["processing_times"] = {
                "min": min(self.processing_times) * 1000,
                "mean": mean(self.processing_times) * 1000,
                "median": processing_times_sorted[len(processing_times_sorted) // 2]
                * 1000,
                "max": max(self.processing_times) * 1000,
            }
            summary["waiting_times"] = {
                "min": min(self.wait_times) * 1000,
                "mean": mean(self.wait_times) * 1000,
                "median": wait_times_sorted[len(wait_times_sorted) // 2] * 1000,
                "max": max(self.wait_times) * 1000,
            }
            summary["total_times"] = {
                "min": min(self.latencies) * 1000,
                "mean": mean(self.latencies) * 1000,
                "median": latencies_sorted[len(latencies_sorted) // 2] * 1000,
                "max": max(self.latencies) * 1000,
            }

            percentiles = [50, 66, 75, 80, 90, 95, 98, 99, 100]
            summary["percentiles"] = {
                str(percentile): latencies_sorted[
                    int(len(latencies_sorted) * percentile / 100)
                ]
                * 1000
                for percentile in percentiles
                if int(len(latencies_sorted) * percentile / 100) < len(latencies_sorted)
            }
        else:
            summary["connection_times"] = {}
            summary["processing_times"] = {}
            summary["waiting_times"] = {}
            summary["total_times"] = {}
            summary["percentiles"] = "N/A"
        return summary
