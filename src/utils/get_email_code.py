from datetime import datetime
import logging
import time
import re
from config import Config
import requests
import email
import imaplib
import poplib
from email.parser import Parser
import json
import socket

# Import translation functions
from src.utils.language import getTranslation, _


class EmailVerificationHandler:
    def __init__(self,account):
        self.session = requests.Session()
        self.account = account

    def get_verification_code(self, max_retries=5, retry_interval=60):
        """
        Get verification code with retry mechanism.

        Args:
            max_retries: Maximum number of retry attempts.
            retry_interval: Time interval between retries (seconds).

        Returns:
            str or None: Verification code if found, None otherwise.
        """

        for attempt in range(max_retries):
            try:
                logging.info(getTranslation("verification_code_attempt").format(attempt + 1, max_retries))

                verify_code = self._get_latest_mail_code()
                if attempt < max_retries - 1 and not verify_code:  # Wait for all attempts except the last one
                    logging.warning(getTranslation("verification_code_not_found_retry").format(retry_interval))
                    time.sleep(retry_interval)
                else: 
                    return verify_code

            except Exception as e:
                logging.error(getTranslation("verification_code_fetch_failed").format(e))  # Log general exceptions
                if attempt < max_retries - 1:
                    logging.error(getTranslation("error_will_retry").format(retry_interval))
                    time.sleep(retry_interval)
                else:
                    raise Exception(getTranslation("max_retries_reached_with_error").format(e)) from e

        raise Exception(getTranslation("verification_code_not_found_after_attempts").format(max_retries))

    def _get_latest_mail_code(self):
        """
        Get verification code from latest email:
        1. iCloud IMAP
        
        Returns:
            str or tuple: Verification code or (code, email_id) tuple
        """
        # First try iCloud IMAP
        icloud_imap = Config().get_icloud_imap()
        if icloud_imap:
            logging.info(getTranslation("using_icloud_imap"))
            # First check inbox
            verify_code = self._get_mail_code_by_icloud_imap(icloud_imap)
            if verify_code:
                return verify_code
            
            # If no code found in inbox, check spam/junk folders
            logging.info(getTranslation("checking_spam_folders"))
            verify_code = self._check_spam_folders(icloud_imap)
            if verify_code:
                return verify_code
        
        return None

    def _check_spam_folders(self, icloud_config):
        """Check spam and junk folders for verification code
        
        Args:
            icloud_config: iCloud IMAP configuration
            
        Returns:
            str or None: verification code if found
        """
        # Common spam/junk folder names in email services
        spam_folders = ['Junk', 'Spam', 'Bulk Mail', 'Junk E-mail']
        
        # Get list of available folders first
        try:
            mail = imaplib.IMAP4_SSL(icloud_config['imap_server'], icloud_config['imap_port'])
            mail.login(icloud_config['imap_user'], icloud_config['imap_pass'])
            
            status, folder_list = mail.list()
            mail.logout()
            
            if status != 'OK':
                logging.error(getTranslation("icloud_folder_list_failed"))
                return None
                
            # Parse folder names from the response
            available_folders = []
            for folder_info in folder_list:
                if isinstance(folder_info, bytes):
                    parts = folder_info.decode('utf-8', errors='ignore').split('"')
                    if len(parts) > 1:
                        folder_name = parts[-2]
                        available_folders.append(folder_name)
            
            # Filter spam folders that actually exist
            valid_spam_folders = [folder for folder in spam_folders if folder in available_folders]
            
            # If no valid spam folders found, try the default list
            if not valid_spam_folders:
                valid_spam_folders = spam_folders
                
            logging.info(f"Available spam folders: {valid_spam_folders}")
            
        except Exception as e:
            logging.error(getTranslation("icloud_folder_list_failed") + f": {str(e)}")
            # Continue with the default list if we can't get available folders
            valid_spam_folders = spam_folders
        
        # Check each potential spam folder
        for folder in valid_spam_folders:
            try:
                # Create a new connection for each folder to avoid state issues
                mail = None
                try:
                    mail = imaplib.IMAP4_SSL(icloud_config['imap_server'], icloud_config['imap_port'])
                    mail.login(icloud_config['imap_user'], icloud_config['imap_pass'])
                    mail.select(folder)
                except Exception as e:
                    logging.error(getTranslation("error_checking_folder").format(folder, f"Failed to select folder: {e}"))
                    if mail:
                        try:
                            mail.logout()
                        except:
                            pass
                    continue  # Try next folder
                
                logging.info(getTranslation("checking_folder").format(folder))
                
                try:
                    status, messages = mail.search(None, 'ALL')
                    if status != 'OK':
                        logging.error(f"Search failed in folder {folder}: {status}")
                        mail.logout()
                        continue  # Try next folder
                    
                    # Handle different message types (bytes or string)
                    if isinstance(messages[0], bytes):
                        mail_ids = messages[0].split()
                    elif isinstance(messages[0], str):
                        mail_ids = messages[0].encode('utf-8').split()
                    else:
                        mail_ids = []
                        
                    if not mail_ids:
                        logging.info(f"No emails in folder {folder}")
                        mail.logout()
                        continue  # No emails in this folder
                    
                    # Check the latest 10 emails in this folder
                    for i in range(min(10, len(mail_ids))):
                        mail_id = mail_ids[len(mail_ids) - 1 - i]
                        try:
                            status, msg_data = mail.fetch(mail_id, '(BODY[])')
                        except (EOFError, ConnectionError, socket.error) as e:
                            logging.error(getTranslation("icloud_imap_fetch_failed").format(e))
                            break  # Connection issue, try next folder
                            
                        if status != 'OK' or not msg_data or not msg_data[0]:
                            logging.error(getTranslation("icloud_imap_fetch_status_failed").format(status))
                            continue
                        
                        # Safety check for data structure
                        if not isinstance(msg_data[0], tuple) or len(msg_data[0]) < 2:
                            logging.error(f"Unexpected message data structure: {msg_data}")
                            continue
                            
                        raw_email = msg_data[0][1]
                        if not raw_email:
                            continue
                            
                        email_message = email.message_from_bytes(raw_email)
                        sender = email_message.get('from', '')
                        recipient = email_message.get('to', '')
                        
                        if self.account not in recipient:
                            continue
                        if 'no-reply_at_cursor_sh' not in sender:
                            continue
                        
                        body = self._extract_imap_body(email_message)
                        if body:
                            # Look for 6-digit verification code
                            code_match = re.search(r"(?<![a-zA-Z@.])\b\d{6}\b", body)
                            if code_match:
                                code = code_match.group()
                                logging.info(getTranslation("verification_code_found_in_spam").format(code, folder))
                                
                                try:
                                    mail.store(mail_id, '+FLAGS', '\\Deleted')
                                    mail.expunge()
                                except Exception as e:
                                    logging.error(f"Failed to delete message: {e}")
                                
                                mail.logout()
                                return code
                except Exception as e:
                    logging.error(getTranslation("error_checking_folder").format(folder, e))
                
                # Close the connection for this folder
                try:
                    mail.logout()
                except:
                    pass
                    
            except Exception as e:
                logging.error(getTranslation("error_checking_folder").format(folder, e))
                continue  # Try next folder
        
        logging.info(getTranslation("no_verification_code_in_spam"))
        return None

    def _get_mail_code_by_icloud_imap(self, icloud_config, retry=0):
        """
        Get email verification code using iCloud IMAP
        
        Args:
            icloud_config: iCloud IMAP configuration information
            retry: Number of retry attempts
            
        Returns:
            str or None: Verification code if found, None otherwise
        """
        if retry > 0:
            time.sleep(3)
        if retry >= 20:
            raise Exception(getTranslation("verification_code_timeout"))
        
        try:
            # Connect to iCloud IMAP server
            mail = imaplib.IMAP4_SSL(icloud_config['imap_server'], icloud_config['imap_port'])
            
            mail.login(icloud_config['imap_user'], icloud_config['imap_pass'])
            mail.select(icloud_config['imap_dir'] or 'INBOX')
            
            # Get recent emails
            status, messages = mail.search(None, 'ALL')
            if status != 'OK':
                logging.error(getTranslation("icloud_email_list_failed").format(status))
                return None
            
            mail_ids = messages[0].split()
            print(mail_ids)
            if not mail_ids:
                # No emails found
                logging.info(getTranslation("no_emails_in_icloud"))
                return self._get_mail_code_by_icloud_imap(icloud_config, retry=retry + 1)
            
            # Check the latest 10 emails
            for i in range(min(10, len(mail_ids))):
                mail_id = mail_ids[len(mail_ids) - 1 - i]  
                try:
                    status, msg_data = mail.fetch(mail_id, '(BODY[])')
                except (EOFError, ConnectionError, socket.error) as e:
                    logging.error(getTranslation("icloud_imap_fetch_failed").format(e))
                    mail.logout()
                    return None
                if status != 'OK':
                    logging.error(getTranslation("icloud_imap_fetch_status_failed").format(status))
                    continue
                raw_email = msg_data[0][1]

                email_message = email.message_from_bytes(raw_email)
                sender = email_message.get('from', '')
                recipient = email_message.get('to', '')

                if self.account not in recipient:
                    continue
                if 'no-reply_at_cursor_sh' not in sender:
                    continue

                body = self._extract_imap_body(email_message)
                if body:
                    # Look for 6-digit verification code
                    code_match = re.search(r"(?<![a-zA-Z@.])\b\d{6}\b", body)
                    if code_match:
                        code = code_match.group()
                        logging.info(getTranslation("verification_code_found_in_email").format(code))
                        
                        mail.store(mail_id, '+FLAGS', '\\Deleted')
                        mail.expunge()
                        
                        mail.logout()
                        return code
            
            logging.info(getTranslation("no_verification_code_in_email"))
            mail.logout()
            return None
            
        except Exception as e:
            if isinstance(e, AttributeError) and "'NoneType' object has no attribute 'split'" in str(e):
                logging.error(getTranslation("none_type_attribute_error"))
                return None
            logging.error(getTranslation("icloud_imap_operation_failed").format(e))
            return None

    def _extract_imap_body(self, email_message):
        """
        Extract email body content
        
        Args:
            email_message: Email message object
            
        Returns:
            str: Email body content
        """
        # Extract email body
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    try:
                        charset = part.get_content_charset() or 'utf-8'
                        payload = part.get_payload(decode=True)
                        
                        # Handle potential int type payload (error from logs)
                        if isinstance(payload, int):
                            logging.error(f"Unexpected payload type (int): {payload}")
                            continue
                            
                        if payload:
                            body = payload.decode(charset, errors='ignore')
                            return body
                    except Exception as e:
                        logging.error(getTranslation("email_body_decode_failed").format(e))
        else:
            content_type = email_message.get_content_type()
            if content_type == "text/plain":
                try:
                    charset = email_message.get_content_charset() or 'utf-8'
                    payload = email_message.get_payload(decode=True)
                    
                    # Handle potential int type payload (error from logs)
                    if isinstance(payload, int):
                        logging.error(f"Unexpected payload type (int): {payload}")
                        return ""
                        
                    if payload:
                        body = payload.decode(charset, errors='ignore')
                        return body
                except Exception as e:
                    logging.error(getTranslation("email_body_decode_failed").format(e))
        return ""

if __name__ == "__main__":
    email_handler = EmailVerificationHandler()
    code = email_handler.get_verification_code()
    print(code)
