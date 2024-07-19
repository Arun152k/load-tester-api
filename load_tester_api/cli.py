import argparse
import asyncio
import json
import os
from urllib.parse import urlparse
from load_tester_api import LoadTester, LoadTesterError
from load_tester_api import formatter, utils


async def run_test(
    url, concurrency, requests, method, headers=None, payload=None, qps=None
):
    tester = LoadTester(
        url=url,
        concurrency=concurrency,
        total_requests=requests,
        method=method,
        headers=headers,
        payload=payload,
        qps=qps,
    )

    try:
        await tester.run_test()
        results = tester.get_results()
        formatted_results = formatter.format_results(results.summary())

        # Ensure the output directory exists
        os.makedirs(utils.cli_output_folder(), exist_ok=True)
        # Save JSON output to a file
        output_filename = f"{utils.cli_output_folder()}/{urlparse(url).hostname}_{method}_{concurrency}concurrency_{requests}requests.json"
        with open(output_filename, "w") as f:
            json.dump(formatted_results, f, indent=4)

        # Pretty print the formatted results
        print(json.dumps(formatted_results, indent=4))
        print(f"Results saved to {output_filename}")
    except LoadTesterError as e:
        print(json.dumps({"error": str(e)}, indent=4))


async def main():
    parser = argparse.ArgumentParser(description="HTTP Load Testing Tool")
    parser.add_argument("--url", required=True, help="The target URL to test")
    parser.add_argument(
        "--concurrency", type=int, default=10, help="Number of concurrent requests"
    )
    parser.add_argument(
        "--requests", type=int, default=100, help="Total number of requests to perform"
    )
    parser.add_argument(
        "--method", type=str, default="GET", help="HTTP method to use for requests"
    )
    parser.add_argument(
        "--headers",
        type=str,
        help="Comma-separated list of headers (e.g., 'Key1:Value1,Key2:Value2')",
    )
    parser.add_argument(
        "--payload",
        type=str,
        help="Payload to send with the requests (for POST, PUT, etc.)",
    )
    parser.add_argument(
        "--qps", type=float, default=None, help="Queries per second rate to maintain"
    )

    args = parser.parse_args()

    headers = {}
    if args.headers:
        headers_list = args.headers.split(",")
        for header in headers_list:
            key, value = header.split(":")
            headers[key.strip()] = value.strip()

    await run_test(
        args.url,
        args.concurrency,
        args.requests,
        args.method,
        headers,
        args.payload,
        args.qps,
    )


if __name__ == "__main__":
    asyncio.run(main())
