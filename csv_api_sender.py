#!/usr/bin/env python3
"""
Biometric Data CSV to API Sender
Reads CSV file with biometric data and sends to the api-condutores endpoint.
Supports: fileFace, fileSign, filesFinger1, filesFinger2
"""

import csv
import requests
import json
import argparse
import sys
import base64
import os
from typing import Dict, List, Optional
from collections import defaultdict
import logging
from datetime import datetime

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    COLORS_AVAILABLE = True
except ImportError:
    COLORS_AVAILABLE = False
    # Fallback if colorama not available
    class Fore:
        GREEN = RED = YELLOW = CYAN = RESET = ""
    class Style:
        BRIGHT = RESET_ALL = ""

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BiometricAPIProcessor:
    """Process CSV file with biometric data and send to API endpoint."""

    # Tipo_Biometria code mapping
    BIOMETRIA_TYPE_MAPPING = {
        '1': 'fileFace',
        '2': 'fileSign',
        '3': 'filesFinger1',
        '4': 'filesFinger2'
    }

    # Mapping of possible CSV column names to API field names (legacy support)
    FIELD_MAPPING = {
        'fileFace': ['fileFace', 'face_img', 'face', 'faceImage'],
        'fileSign': ['fileSign', 'signature', 'sign', 'signImage'],
        'filesFinger1': ['filesFinger1', 'fingerprint1', 'finger1', 'fp1'],
        'filesFinger2': ['filesFinger2', 'fingerprint2', 'finger2', 'fp2']
    }

    def __init__(self, api_base_url: str, headers: Dict[str, str] = None):
        """
        Initialize the processor.

        Args:
            api_base_url: The base API URL (e.g., http://127.0.0.1:5000)
            headers: Optional HTTP headers for API requests
        """
        self.api_base_url = api_base_url.rstrip('/')
        self.headers = headers or {'Content-Type': 'application/json'}
        self.files_not_found = []

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

    def file_to_base64(self, file_path: str) -> Optional[str]:
        """
        Read file and convert to base64 string.

        Args:
            file_path: Path to the file

        Returns:
            Base64 encoded string or None if file not found
        """
        try:
            with open(file_path, 'rb') as f:
                return base64.b64encode(f.read()).decode('utf-8')
        except FileNotFoundError:
            self.files_not_found.append(file_path)
            logger.warning(f"File not found: {file_path}")
            return None
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return None

    def group_by_license(self, records: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Group CSV records by Numero_Carta.

        Args:
            records: List of CSV records

        Returns:
            Dictionary mapping license numbers to their records
        """
        grouped = defaultdict(list)

        for record in records:
            numero_carta = record.get('Numero_Carta', '').strip()
            if numero_carta:
                grouped[numero_carta].append(record)

        return dict(grouped)

    def build_payload_from_rows(self, rows: List[Dict]) -> Dict:
        """
        Build API payload from multiple CSV rows for the same driver.
        Supports both formats:
        1. Tipo_Biometria format (ID, Numero_Carta, Caminho_Completo, Tipo_Biometria)
        2. Direct base64 format (numero_carta, fileFace, fileSign, etc.)

        Args:
            rows: List of CSV rows for the same driver

        Returns:
            Dictionary with API field names and base64 values
        """
        payload = {}

        for row in rows:
            # Format 1: Tipo_Biometria with file paths
            if 'Tipo_Biometria' in row and 'Caminho_Completo' in row:
                tipo = str(row.get('Tipo_Biometria', '')).strip()
                file_path = row.get('Caminho_Completo', '').strip()
                is_active = row.get('Is_Active', '1').strip()

                # Skip inactive records
                if is_active != '1':
                    continue

                if tipo in self.BIOMETRIA_TYPE_MAPPING and file_path:
                    api_field = self.BIOMETRIA_TYPE_MAPPING[tipo]

                    # Convert file to base64
                    base64_data = self.file_to_base64(file_path)
                    if base64_data:
                        payload[api_field] = base64_data

            # Format 2: Direct base64 values (legacy support)
            else:
                for api_field, csv_field_options in self.FIELD_MAPPING.items():
                    for csv_field in csv_field_options:
                        if csv_field in row and row[csv_field] and row[csv_field].strip():
                            payload[api_field] = row[csv_field].strip()
                            break

        return payload

    def get_license_number(self, row: Dict) -> Optional[str]:
        """
        Extract license number from CSV row.

        Args:
            row: CSV row as dictionary

        Returns:
            License number or None
        """
        possible_fields = ['Numero_Carta', 'numero_carta', 'license_number', 'license', 'carta', 'id']

        for field in possible_fields:
            if field in row and row[field] and row[field].strip():
                return row[field].strip()

        return None

    def send_to_api(self, numero_carta: str, payload: Dict) -> Dict:
        """
        Send biometric data to API for a specific license number.

        Args:
            numero_carta: Driver's license number
            payload: Dictionary with biometric data (fileFace, fileSign, etc.)

        Returns:
            API response dictionary with status and details
        """
        url = f"{self.api_base_url}/biometric-data/{numero_carta}"

        try:
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=30
            )

            response_data = response.json() if response.text else {}

            if response.status_code == 201:
                # Success - HTTP 201 Created
                return {
                    'status': 'success',
                    'status_code': response.status_code,
                    'response': response_data
                }
            elif response.status_code == 400:
                # Bad Request - No valid data provided
                message = response_data.get('status', {}).get('message',
                          response_data.get('message', 'No new biometric data provided'))
                return {
                    'status': 'skipped',
                    'status_code': response.status_code,
                    'error': message,
                    'response': response_data
                }
            elif response.status_code == 404:
                # Not Found - API endpoint doesn't exist
                return {
                    'status': 'config_error',
                    'status_code': response.status_code,
                    'error': 'API endpoint not found - check API URL configuration',
                    'response': response_data
                }
            elif response.status_code == 500:
                # Internal Server Error
                message = response_data.get('message', 'Server error occurred')
                return {
                    'status': 'server_error',
                    'status_code': response.status_code,
                    'error': f'Server error: {message}',
                    'response': response_data
                }
            else:
                # Other HTTP errors
                return {
                    'status': 'error',
                    'status_code': response.status_code,
                    'error': response_data.get('message', f'HTTP {response.status_code} error'),
                    'response': response_data
                }

        except requests.exceptions.Timeout:
            return {
                'status': 'error',
                'error': 'Request timeout (30s exceeded)'
            }
        except requests.exceptions.ConnectionError:
            return {
                'status': 'error',
                'error': 'Connection error - unable to reach API'
            }
        except requests.exceptions.RequestException as e:
            return {
                'status': 'error',
                'error': str(e)
            }
        except json.JSONDecodeError:
            return {
                'status': 'error',
                'error': 'Invalid JSON response from API'
            }

    def print_status_line(self, row_num: int, total: int, numero_carta: str,
                         status: str, details: str = ""):
        """
        Print formatted status line for console output.

        Args:
            row_num: Current row number
            total: Total number of rows
            numero_carta: License number
            status: 'OK', 'FAILED', 'SKIPPED', etc.
            details: Additional details about the result
        """
        # Color-coded status symbols
        if status == "OK":
            status_symbol = f"{Fore.GREEN}[OK]{Style.RESET_ALL}"
        elif status == "SKIPPED":
            status_symbol = f"{Fore.YELLOW}[SKIPPED]{Style.RESET_ALL}"
        elif status == "CONFIG_ERROR":
            status_symbol = f"{Fore.RED}{Style.BRIGHT}[CONFIG ERROR]{Style.RESET_ALL}"
        elif status == "SERVER_ERROR":
            status_symbol = f"{Fore.RED}[SERVER ERROR]{Style.RESET_ALL}"
        else:  # FAILED
            status_symbol = f"{Fore.RED}[FAILED]{Style.RESET_ALL}"

        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{timestamp} | Row {row_num}/{total} | {numero_carta:15} | {status_symbol:10} | {details}")

    def process_csv(self, csv_file: str) -> Dict:
        """
        Process CSV file and send each record to the API.
        Groups records by Numero_Carta and sends all biometric data for each driver.

        Args:
            csv_file: Path to CSV file

        Returns:
            Processing results summary with detailed report
        """
        records = self.read_csv(csv_file)

        # Group records by license number
        grouped_records = self.group_by_license(records)

        print("\n" + "="*100)
        print(f"Starting processing of {len(records)} CSV rows → {len(grouped_records)} unique drivers")
        print("="*100)
        print(f"{'Time':8} | {'Driver':11} | {'License Number':15} | {'Status':10} | Details")
        print("-"*100)

        results = {
            'total_csv_rows': len(records),
            'total_drivers': len(grouped_records),
            'success': 0,
            'failed': 0,
            'skipped': 0,
            'details': []
        }

        for idx, (numero_carta, rows) in enumerate(grouped_records.items(), 1):
            if not numero_carta:
                self.print_status_line(idx, len(grouped_records), "N/A", "FAILED",
                                     "Missing license number in CSV")
                results['skipped'] += 1
                results['details'].append({
                    'driver': idx,
                    'numero_carta': None,
                    'status': 'skipped',
                    'error': 'Missing license number'
                })
                continue

            # Build payload from all rows for this driver
            payload = self.build_payload_from_rows(rows)

            if not payload:
                self.print_status_line(idx, len(grouped_records), numero_carta, "FAILED",
                                     "No biometric data found or all files missing")
                results['skipped'] += 1
                results['details'].append({
                    'driver': idx,
                    'numero_carta': numero_carta,
                    'status': 'skipped',
                    'error': 'No biometric data available',
                    'csv_rows': len(rows)
                })
                continue

            # Send to API
            result = self.send_to_api(numero_carta, payload)

            if result['status'] == 'success':
                # HTTP 201 - Success
                results['success'] += 1
                api_status = result.get('response', {}).get('status', {})

                files_created = api_status.get('files_created', [])
                files_updated = api_status.get('files_updated', [])
                files_missing = api_status.get('files_missing', [])

                details_parts = []

                if files_created:
                    details_parts.append(f"Created: {', '.join(files_created)}")

                if files_updated:
                    details_parts.append(f"Replaced: {', '.join(files_updated)}")

                if files_missing:
                    details_parts.append(f"{Fore.YELLOW}Warning: Missing {', '.join(files_missing)}{Style.RESET_ALL}")

                details = " | ".join(details_parts) if details_parts else "Data submitted"

                self.print_status_line(idx, len(grouped_records), numero_carta, "OK", details)

                results['details'].append({
                    'driver': idx,
                    'numero_carta': numero_carta,
                    'status': 'success',
                    'files_created': files_created,
                    'files_updated': files_updated,
                    'files_missing': files_missing,
                    'csv_rows': len(rows)
                })

            elif result['status'] == 'skipped':
                # HTTP 400 - Bad Request (no valid data)
                results['skipped'] += 1
                error_msg = result.get('error', 'No new biometric data provided')

                self.print_status_line(idx, len(grouped_records), numero_carta, "SKIPPED",
                                     error_msg)

                results['details'].append({
                    'driver': idx,
                    'numero_carta': numero_carta,
                    'status': 'skipped',
                    'error': error_msg,
                    'csv_rows': len(rows)
                })

            elif result['status'] == 'config_error':
                # HTTP 404 - Not Found (wrong API URL)
                results['failed'] += 1
                error_msg = result.get('error', 'API endpoint not found')

                self.print_status_line(idx, len(grouped_records), numero_carta, "CONFIG_ERROR",
                                     error_msg)

                results['details'].append({
                    'driver': idx,
                    'numero_carta': numero_carta,
                    'status': 'config_error',
                    'error': error_msg,
                    'csv_rows': len(rows)
                })

            elif result['status'] == 'server_error':
                # HTTP 500 - Internal Server Error
                results['failed'] += 1
                error_msg = result.get('error', 'Server error occurred')

                self.print_status_line(idx, len(grouped_records), numero_carta, "SERVER_ERROR",
                                     f"{error_msg}. Contact administrator or retry later.")

                results['details'].append({
                    'driver': idx,
                    'numero_carta': numero_carta,
                    'status': 'server_error',
                    'error': error_msg,
                    'csv_rows': len(rows)
                })

            else:
                # Other errors
                results['failed'] += 1
                error_msg = result.get('error', 'Unknown error')

                self.print_status_line(idx, len(grouped_records), numero_carta, "FAILED",
                                     f"Error: {error_msg}")

                results['details'].append({
                    'driver': idx,
                    'numero_carta': numero_carta,
                    'status': 'failed',
                    'error': error_msg,
                    'response': result.get('response', {}),
                    'csv_rows': len(rows)
                })

        # Print summary
        print("-"*100)
        print(f"\n{'SUMMARY':^100}")
        print("="*100)
        print(f"Total CSV rows:        {results['total_csv_rows']}")
        print(f"Total unique drivers:  {results['total_drivers']}")
        print(f"Successful:            {results['success']}")
        print(f"Failed:                {results['failed']}")
        print(f"Skipped:               {results['skipped']}")
        if self.files_not_found:
            print(f"\n{Fore.YELLOW}Files not found:       {len(self.files_not_found)}{Style.RESET_ALL}")
        print("="*100 + "\n")

        return results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Send biometric data from CSV to api-condutores',
        epilog='''
Example usage:
  %(prog)s data.csv http://127.0.0.1:5000
  %(prog)s data.csv http://127.0.0.1:5000 --output report.json
  %(prog)s data.csv http://127.0.0.1:5000 --header "Authorization: Bearer token123"

CSV Format:
  Required: numero_carta (or license_number, license, carta, id)
  Optional: fileFace, fileSign, filesFinger1, filesFinger2 (base64 encoded images)
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        'csv_file',
        help='Path to CSV file with biometric data'
    )
    parser.add_argument(
        'api_base_url',
        help='API base URL (e.g., http://127.0.0.1:5000)'
    )
    parser.add_argument(
        '--header',
        action='append',
        help='HTTP header in format "Key: Value" (can be used multiple times)'
    )
    parser.add_argument(
        '--output',
        help='Save detailed results to JSON file'
    )

    args = parser.parse_args()

    # Parse custom headers
    headers = {'Content-Type': 'application/json'}
    if args.header:
        for header in args.header:
            if ':' not in header:
                logger.error(f"Invalid header format: {header}. Use 'Key: Value'")
                sys.exit(1)
            key, value = header.split(':', 1)
            headers[key.strip()] = value.strip()

    # Process CSV and send to API
    processor = BiometricAPIProcessor(args.api_base_url, headers)
    results = processor.process_csv(args.csv_file)

    # Save results if requested
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\nDetailed results saved to: {args.output}")

    # Exit with appropriate code
    if results['failed'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()