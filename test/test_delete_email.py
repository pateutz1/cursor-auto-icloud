"""
Test script for the iCloud Email Deletion feature.
This script allows you to test deleting a specific iCloud Hide My Email address.
"""

import os
import sys
import asyncio
import argparse
from typing import List, Optional, Union, Tuple

ICLOUD_COOKIES=None
# Add parent directory to path to import required modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


if parent_dir not in sys.path:
    sys.path.append(parent_dir)

try:
    from src.utils.logger import logging
    from src.icloud.deleteEmail import deleteIcloudEmail
    from src.utils.language import getTranslation, _
except ImportError:
    print("Failed to import required modules. Make sure you're running from the project root.")
    sys.exit(1)

def setup_logging():
    """Configure detailed logging for the test script"""
    import logging as std_logging
    std_logging.basicConfig(
        level=std_logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def check_icloud_cookies():
    """Check if iCloud cookies are configured"""
    cookies = ICLOUD_COOKIES;
    if not cookies.strip():
        print("⚠️  " + getTranslation("icloud_cookies_not_configured"))
        return False
    else:
        cookie_length = len(cookies.strip())
        print(f"✅ iCloud cookies found: {cookie_length} characters")
        return True

def main():
    """Main test function"""
    print("\n🧪 iCloud Hide My Email Deletion Test\n")
    
    # Setup logging
    setup_logging()
    
    # Check if cookies are configured
    if not check_icloud_cookies():
        sys.exit(1)
    
    # Get email to delete from command line or user input
    parser = argparse.ArgumentParser(description='Test iCloud Hide My Email deletion.')
    parser.add_argument('email', nargs='?', help='Email address to delete')
    args = parser.parse_args()
    
    email_to_delete = args.email
    
    if not email_to_delete:
        # Get email from user input
        email_to_delete = input("Enter the email address to delete: ").strip()
    
    if not email_to_delete:
        print("No email specified. Exiting.")
        sys.exit(1)
        
    # Confirm before deletion
    print(f"\nYou're about to delete the email: {email_to_delete}")
    confirmation = input("Are you sure you want to proceed? (y/N): ").strip().lower()
    
    if confirmation != 'y':
        print("Operation cancelled by user.")
        sys.exit(0)
    
    print(f"\nDeleting email: {email_to_delete}")
    results = deleteIcloudEmail(email_to_delete)
    
    
    sys.exit(0 if results[0][1] else 1)

if __name__ == "__main__":
    main()
