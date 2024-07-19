import asyncio
import os
import json
from load_tester_api import LoadTester, LoadTesterError
from load_tester_api import formatter, utils


async def run_test(url, concurrency, requests, method, headers=None, payload=None):
    tester = LoadTester(
        url=url,
        concurrency=concurrency,
        total_requests=requests,
        method=method,
        headers=headers,
        payload=payload,
    )

    try:
        await tester.run_test()
        results = tester.get_results()
        formatted_results = formatter.format_results(results.summary())

        # Save JSON output to a file
        output_filename = f"{utils.batch_output_folder()}/{utils.urlparse(url).hostname}_{method}_{concurrency}concurrency_{requests}requests.json"
        with open(output_filename, "w") as f:
            json.dump(formatted_results, f, indent=4)

        print(f"Results saved to {output_filename}")

    except LoadTesterError as e:
        print(f"Error: {e}")


async def main():
    headers = {"Content-Type": "application/json"}
    payload = '{"key": "value"}'

    # Ensure the output directory exists
    os.makedirs(utils.batch_output_folder(), exist_ok=True)

    # Example tests
    await run_test("http://example.com", 10, 10, "GET")
    await run_test("http://example.com", 50, 5, "POST", headers, payload)
    # await run_test("http://example.com", 10, 10, "PUT", headers, payload)
    # await run_test("http://example.com", 10, 10, "DELETE")


if __name__ == "__main__":
    asyncio.run(main())
