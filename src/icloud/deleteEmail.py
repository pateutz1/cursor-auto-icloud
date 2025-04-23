#!/usr/bin/env python3
"""
iCloud Email Deletion Utility
This module deletes Hide My Email addresses from iCloud accounts.
"""

import os
import sys
import asyncio
from typing import List, Optional, Union, Tuple

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

async def _delete_email(cookies: str, email: str) -> Tuple[bool, str]:
    """
    Delete a single Hide My Email address from iCloud
    
    Args:
        cookies: iCloud cookies for authentication
        email: Email address to delete
        
    Returns:
        Tuple[bool, str]: (Success status, Message)
    """
    try:
        logging.info(getTranslation("deleting_email").format(email))
        
        # Use with statement for proper resource management since the class requires it
        async with HideMyEmail(label="Cursor-Auto-iCloud", cookies=cookies) as hide_my_email:
            # Get the list of existing emails
            email_list_response = await hide_my_email.list_email()
            if not email_list_response or not email_list_response.get("success", False):
                return False, getTranslation("no_emails_found")
            
            # Extract emails from the response - emails are in result.hmeEmails
            email_list = email_list_response.get("result", {}).get("hmeEmails", [])
            
            # Find the email in the list
            found_email = None
            for e in email_list:
                if e.get('hme') == email:
                    found_email = e
                    break
            
            if not found_email:
                return False, getTranslation("email_not_found").format(email)
            
            # First deactivate the email using the anonymousId
            anonymous_id = found_email.get('anonymousId')
            if not anonymous_id:
                return False, getTranslation("email_missing_id").format(email)
            
            deactivate_result = await hide_my_email.deactivate_email(anonymous_id)
            if not deactivate_result or not deactivate_result.get("success", False):
                reason = deactivate_result.get("reason", getTranslation("unknown_error")) if deactivate_result else getTranslation("unknown_error")
                return False, getTranslation("email_deactivation_failed").format(reason)
            
            # Then delete the email using the anonymousId
            delete_result = await hide_my_email.delete_email(anonymous_id, email)
            
            if delete_result and delete_result.get("success", False):
                return True, getTranslation("email_deleted_success").format(email)
            else:
                reason = delete_result.get("reason", getTranslation("unknown_error")) if delete_result else getTranslation("unknown_error")
                return False, getTranslation("email_deletion_failed").format(reason)
    
    except asyncio.TimeoutError:
        return False, getTranslation("delete_email_timeout")
    except Exception as e:
        logging.error(f"Exception details: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())
        return False, getTranslation("delete_email_failed").format(str(e))
    
def deleteIcloudEmail(email: Union[str, List[str]]) -> List[Tuple[str, bool, str]]:
    """
    Delete iCloud Hide My Email address(es)
    
    Args:
        email: Single email address or list of email addresses to delete
        
    Returns:
        List[Tuple[str, bool, str]]: List of (email, success, message) tuples
    """
    # Ensure email is a list
    emails = [email] if isinstance(email, str) else email
    
    if not emails:
        logging.error(getTranslation("no_emails_to_delete"))
        return []
    
    # Get iCloud cookies from config
    try:
        # Get cookies from .env file
        cookies = os.getenv('ICLOUD_COOKIES', '').strip()
        if not cookies:
            logging.error(getTranslation("icloud_cookies_not_configured"))
            return [(e, False, getTranslation("icloud_cookies_not_configured")) for e in emails]
            
        # Process each email
        results = []
        for e in emails:
            success, message = asyncio.run(_delete_email(cookies, e))
            results.append((e, success, message))
            if success:
                logging.info(message)
            else:
                logging.error(message)
                
        return results
        
    except Exception as e:
        logging.error(getTranslation("email_deletion_error").format(str(e)))
        import traceback
        logging.error(traceback.format_exc())
        return [(e, False, str(e)) for e in emails]

if __name__ == "__main__":
    # If run directly, delete specified emails
    if len(sys.argv) > 1:
        emails_to_delete = sys.argv[1:]
        print(getTranslation("deleting_emails").format(len(emails_to_delete)))
        results = deleteIcloudEmail(emails_to_delete)
        
        for email, success, message in results:
            status = getTranslation("success") if success else getTranslation("failed")
            print(f"{email}: {status} - {message}")
    else:
        print(getTranslation("no_emails_specified")) 