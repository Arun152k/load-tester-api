def format_results(results):
    def get_times(times):
        return {
            "min": times.get("min", "N/A"),
            "mean": times.get("mean", "N/A"),
            "median": times.get("median", "N/A"),
            "max": times.get("max", "N/A"),
        }

    return {
        "Server Software": results["server_software"],
        "Server Hostname": results["server_hostname"],
        "Server Port": results["server_port"],
        "Document Path": results["document_path"],
        "Document Length": f"{results['document_length']} bytes",
        "Concurrency Level": results["concurrency_level"],
        "qps": results["qps"],
        "Time taken for tests": f"{results['total_test_time']:.3f} seconds",
        "Complete requests": results["completed_requests"],
        "Failed requests": results["failed_requests"],
        "Error rate": f"{results['error_rate']}",
        "Write errors": results["write_errors"],
        "Connection errors": results["connection_errors"],
        "Read errors": results["read_errors"],
        "Status code errors": results["status_code_errors"],
        "Invalid URL errors": results["invalid_url_errors"],
        "Timeout errors": results["timeout_errors"],
        "Keep-Alive requests": results["keep_alive_requests"],
        "Total transferred": f"{results['total_transferred']} bytes",
        "HTML transferred": f"{results['html_transferred']} bytes",
        "Requests per second": f"{results['requests_per_second']:.2f} [#/sec] (mean)",
        "Time per request": f"{results['time_per_request']:.3f} [ms] (mean)",
        "Transfer rate received": f"{results['transfer_rate_received']:.2f} [Kbytes/sec] received",
        "Transfer rate sent": f"{results['transfer_rate_sent']:.2f} [Kbytes/sec] sent",
        "Transfer rate total": f"{results['transfer_rate_total']:.2f} [Kbytes/sec] total",
        "Connection Times (ms)": {
            "Connect": get_times(results.get("connection_times", {})),
            "Processing": get_times(results.get("processing_times", {})),
            "Waiting": get_times(results.get("waiting_times", {})),
            "Total": get_times(results.get("total_times", {})),
        },
        "Percentage of the requests served within a certain time (ms)": results[
            "percentiles"
        ],
    }
