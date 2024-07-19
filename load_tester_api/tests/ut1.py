import unittest
import subprocess
import os
import json


class TestExampleCLI(unittest.TestCase):

    def run_cli(self, args):
        """Helper method to run the CLI and capture the output."""
        process = subprocess.Popen(
            ["python", "-m", "load_tester_api.cli"] + args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = process.communicate()
        return process.returncode, stdout.decode("utf-8"), stderr.decode("utf-8")

    def extract_output_filename(self, stdout):
        """Helper method to extract the output filename from stdout."""
        lines = stdout.split("\n")
        for line in lines:
            if line.startswith("Results saved to") or line.startswith(
                "Error details saved to"
            ):
                return line.split(" to ")[-1].strip()
        return None

    def test_valid_url(self):
        """Test with a valid URL."""
        returncode, stdout, stderr = self.run_cli(
            ["--url", "http://example.com", "--concurrency", "1", "--requests", "10"]
        )
        print("STDOUT:", stdout)  # Debug: Print stdout for examination
        print("STDERR:", stderr)  # Debug: Print stderr for examination
        self.assertEqual(returncode, 0)
        self.assertIn("Results saved to", stdout)

        output_file = self.extract_output_filename(stdout)
        self.assertIsNotNone(output_file, "Output file name not found in stdout.")
        self.assertTrue(
            os.path.exists(output_file), f"Output file {output_file} does not exist."
        )

        with open(output_file, "r") as f:
            data = json.load(f)
            self.assertIn("Server Software", data)
            self.assertIn("Complete requests", data)
            self.assertEqual(data["Complete requests"], 10)


if __name__ == "__main__":
    unittest.main()
