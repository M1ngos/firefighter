#!/usr/bin/env python3
"""
CSV to API Sender
Reads CSV file with identifier fields and sends data to an API endpoint.
"""

import csv
import requests
import json
import argparse
import sys
from typing import Dict, List
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CSVAPIProcessor:
    """Process CSV file and send data to API endpoint."""

    def __init__(self, api_url: str, headers: Dict[str, str] = None):
        """
        Initialize the processor.

        Args:
            api_url: The API endpoint URL
            headers: Optional HTTP headers for API requests
        """
        self.api_url = api_url
        self.headers = headers or {'Content-Type': 'application/json'}

    def read_csv(self, csv_file: str) -> List[Dict]:
        """
        Read CSV file and return list of dictionaries.

        Args:
            csv_file: Path to CSV file

        Returns:
            List of dictionaries containing row data
        """
        data = []
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    data.append(row)
            logger.info(f"Successfully read {len(data)} rows from {csv_file}")
            return data
        except FileNotFoundError:
            logger.error(f"File not found: {csv_file}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Error reading CSV file: {e}")
            sys.exit(1)

    def send_to_api(self, data: Dict) -> Dict:
        """
        Send single record to API.

        Args:
            data: Dictionary containing record data

        Returns:
            API response as dictionary
        """
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            return {
                'status': 'success',
                'status_code': response.status_code,
                'response': response.json() if response.text else {}
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }

    def process_batch(self, csv_file: str, batch_mode: bool = False) -> Dict:
        """
        Process CSV file and send to API.

        Args:
            csv_file: Path to CSV file
            batch_mode: If True, send all records in one request; if False, send individually

        Returns:
            Processing results summary
        """
        records = self.read_csv(csv_file)

        if batch_mode:
            logger.info(f"Sending {len(records)} records in batch mode")
            result = self.send_to_api({'records': records})
            return {
                'total': len(records),
                'batch_result': result
            }
        else:
            logger.info(f"Sending {len(records)} records individually")
            results = {
                'total': len(records),
                'success': 0,
                'failed': 0,
                'details': []
            }

            for idx, record in enumerate(records, 1):
                logger.info(f"Processing record {idx}/{len(records)}")
                result = self.send_to_api(record)

                if result['status'] == 'success':
                    results['success'] += 1
                else:
                    results['failed'] += 1

                results['details'].append({
                    'record_id': record.get('appointment_id', f'record_{idx}'),
                    'result': result
                })

            return results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Process CSV file and send data to API endpoint'
    )
    parser.add_argument(
        'csv_file',
        help='Path to CSV file'
    )
    parser.add_argument(
        'api_url',
        help='API endpoint URL'
    )
    parser.add_argument(
        '--batch',
        action='store_true',
        help='Send all records in a single batch request'
    )
    parser.add_argument(
        '--header',
        action='append',
        help='HTTP header in format "Key: Value" (can be used multiple times)'
    )
    parser.add_argument(
        '--output',
        help='Save results to JSON file'
    )

    args = parser.parse_args()

    # Parse custom headers
    headers = {'Content-Type': 'application/json'}
    if args.header:
        for header in args.header:
            key, value = header.split(':', 1)
            headers[key.strip()] = value.strip()

    # Process CSV and send to API
    processor = CSVAPIProcessor(args.api_url, headers)
    results = processor.process_batch(args.csv_file, args.batch)

    # Display results
    logger.info("Processing complete!")
    logger.info(f"Results: {json.dumps(results, indent=2)}")

    # Save results if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"Results saved to {args.output}")


if __name__ == '__main__':
    main()