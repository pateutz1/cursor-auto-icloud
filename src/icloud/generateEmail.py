#!/usr/bin/env python3
"""
iCloud Email Generator
This module generates Hide My Email addresses for iCloud accounts.
"""

import os
import sys
import asyncio
from typing import List, Optional

# Add parent directory to path to import language module
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

try:
    from src.utils.logger import logging
    from src.utils.config import Config
    from src.icloud.hidemyemail import HideMyEmail
    from src.utils.language import getTranslation, _
except ImportError:
    from utils.logger import logging
    from utils.config import Config
    from icloud.hidemyemail import HideMyEmail
    from utils.language import getTranslation, _

async def _generate_single_email(cookies: str, label: str = "Cursor-Auto-iCloud") -> Optional[str]:
    """
    Generate a single iCloud Hide My Email address
    
    Args:
        cookies: iCloud cookies for authentication
        label: Label for the email
        
    Returns:
        str: The generated email address or None if failed
    """
    try:
        async with HideMyEmail(label, cookies) as hme:
            # Generate email
            gen_result = await hme.generate_email()
            
            # Debug print the result
            logging.debug(f"API Response: {gen_result}")
            
            if not gen_result.get("success", False):
                logging.error(getTranslation("generate_email_failed").format(gen_result.get('reason', getTranslation("unknown_error"))))
                return None
                
            # Correctly access the email address from the nested structure
            email = gen_result.get("result", {}).get("hme")
            if not email:
                logging.error(getTranslation("generate_email_failed_no_address"))
                return None
                
            # Reserve email
            reserve_result = await hme.reserve_email(email)
            if not reserve_result.get("success", False):
                logging.error(getTranslation("reserve_email_failed").format(reserve_result.get('reason', getTranslation("unknown_error"))))
                return None
                
            logging.info(getTranslation("email_generated_success").format(email))
            return email
    except Exception as e:
        logging.error(getTranslation("generate_email_error").format(str(e)))
        return None

async def _generate_multiple_emails(count: int, cookies: str, label: str = "Cursor-Auto-iCloud") -> List[str]:
    """
    Generate multiple iCloud Hide My Email addresses
    
    Args:
        count: Number of emails to generate
        cookies: iCloud cookies for authentication
        label: Label for the emails
        
    Returns:
        List[str]: List of generated email addresses
    """
    tasks = []
    for _ in range(count):
        tasks.append(_generate_single_email(cookies, label))
    
    results = await asyncio.gather(*tasks)
    # Filter out None values
    return [email for email in results if email]

def generateIcloudEmail(count: int = 1, save_to_file: bool = True) -> List[str]:
    """
    Generate a specified number of iCloud Hide My Email addresses
    
    Args:
        count: Number of emails to generate
        save_to_file: Whether to save emails to data/emails.txt
        
    Returns:
        List[str]: List of generated email addresses
    """
    # Get iCloud cookies from config
    try:
        # Get cookies from .env file
        cookies = os.getenv('ICLOUD_COOKIES', '').strip()
        if not cookies:
            logging.error(getTranslation("icloud_cookies_not_configured"))
            return []
            
        # Generate emails
        logging.info(getTranslation("start_generating_emails").format(count))
        emails = asyncio.run(_generate_multiple_emails(count, cookies))
        
        if not emails:
            logging.error(getTranslation("no_emails_generated"))
            return []
            
        logging.info(getTranslation("emails_generated_success").format(len(emails)))
        
        # Save to file if requested
        if save_to_file:
            data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
                
            emails_file = os.path.join(data_dir, "emails.txt")
            
            # If file exists, read existing emails
            existing_emails = []
            if os.path.exists(emails_file):
                with open(emails_file, "r") as f:
                    existing_emails = [line.strip() for line in f.readlines() if line.strip()]
            
            # Add new emails
            all_emails = existing_emails + emails
            
            # Write back to file
            with open(emails_file, "w") as f:
                f.write("\n".join(all_emails))
                
            logging.info(getTranslation("emails_saved_to_file").format(emails_file))
                
        return emails
        
    except Exception as e:
        logging.error(getTranslation("generate_email_error").format(str(e)))
        import traceback
        logging.error(traceback.format_exc())
        return []

if __name__ == "__main__":
    # If run directly, generate 5 emails
    count = 5
    if len(sys.argv) > 1:
        try:
            count = int(sys.argv[1])
        except ValueError:
            logging.error(getTranslation("invalid_count_parameter").format(sys.argv[1]))
            sys.exit(1)
    
    emails = generateIcloudEmail(count)
    if emails:
        print(getTranslation("emails_generated_success").format(len(emails)))
        for email in emails:
            print(email)
    else:
        print(getTranslation("no_emails_generated"))
