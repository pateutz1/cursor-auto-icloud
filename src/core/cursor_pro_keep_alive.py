import os
import platform
import json
import sys
import csv
import uuid
import secrets
import hashlib
import base64
from pathlib import Path
import dotenv
import requests
from datetime import datetime
from enum import Enum
from typing import Optional, Tuple

from src.core.exit_cursor import ExitCursor
import src.core.go_cursor_help as go_cursor_help
import src.auth.patch_cursor_get_machine_id as patch_cursor_get_machine_id
from src.auth.reset_machine import MachineIDResetter
from src.utils.language import LanguageManager

from src.icloud.generateEmail import generateIcloudEmail
from src.icloud.deleteEmail import deleteIcloudEmail

os.environ["PYTHONVERBOSE"] = "0"
os.environ["PYINSTALLER_VERBOSE"] = "0"

import time
import random
from src.auth.cursor_auth_manager import CursorAuthManager
import os
from src.utils.logger import logging
from src.utils.browser_utils import BrowserManager
from src.utils.get_email_code import EmailVerificationHandler
from src.ui.logo import print_logo
from src.utils.config import Config

# Add parent directory to path to import language module
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

try:
    from src.utils.language import getTranslation, _
except ImportError:
    from utils.language import getTranslation, _

# Define EMOJI dictionary
EMOJI = {"ERROR": "❌", "WARNING": "⚠️", "INFO": "ℹ️"}


class VerificationStatus(Enum):
    """Verification status enumeration"""

    PASSWORD_PAGE = "@name=password"
    CAPTCHA_PAGE = "@data-index=0"
    ACCOUNT_SETTINGS = "Account Settings"


class TurnstileError(Exception):
    """Turnstile verification related exception"""

    pass


def save_screenshot(tab, stage: str, timestamp: bool = True) -> None:
    """
    Save a screenshot of the page

    Args:
        tab: Browser tab object
        stage: Screenshot stage identifier
        timestamp: Whether to add a timestamp
    """
    try:
        # Create screenshots directory
        screenshot_dir = "screenshots"
        if not os.path.exists(screenshot_dir):
            os.makedirs(screenshot_dir)

        # Generate filename
        if timestamp:
            filename = f"turnstile_{stage}_{int(time.time())}.png"
        else:
            filename = f"turnstile_{stage}.png"

        filepath = os.path.join(screenshot_dir, filename)

        # Save screenshot
        tab.get_screenshot(filepath)
        logging.debug(getTranslation("screenshot_saved").format(filepath))
    except Exception as e:
        logging.warning(getTranslation("screenshot_save_failed").format(str(e)))


def check_verification_success(tab) -> Optional[VerificationStatus]:
    """
    Check if verification was successful

    Returns:
        VerificationStatus: Returns corresponding status if successful, None if failed
    """
    for status in VerificationStatus:
        if tab.ele(status.value):
            logging.info(getTranslation("verification_success_page").format(status.name))
            return status
    return None


def handle_turnstile(tab, max_retries: int = 2, retry_interval: tuple = (1, 2)) -> bool:
    """
    Handle Turnstile verification

    Args:
        tab: Browser tab object
        max_retries: Maximum number of retry attempts
        retry_interval: Retry interval time range (min, max)

    Returns:
        bool: Whether verification was successful

    Raises:
        TurnstileError: Exception during verification process
    """
    logging.info(getTranslation("detecting_turnstile"))
    save_screenshot(tab, "start")

    retry_count = 0

    try:
        while retry_count < max_retries:
            retry_count += 1
            logging.debug(getTranslation("verification_attempt").format(retry_count))

            try:
                # Locate verification frame element
                challenge_check = (
                    tab.ele("@id=cf-turnstile", timeout=2)
                    .child()
                    .shadow_root.ele("tag:iframe")
                    .ele("tag:body")
                    .sr("tag:input")
                )

                if challenge_check:
                    logging.info(getTranslation("turnstile_detected"))
                    # Random delay before clicking verification
                    time.sleep(random.uniform(1, 3))
                    challenge_check.click()
                    time.sleep(2)

                    # Save post-verification screenshot
                    save_screenshot(tab, "clicked")

                    # Check verification result
                    if check_verification_success(tab):
                        logging.info(getTranslation("turnstile_passed"))
                        save_screenshot(tab, "success")
                        return True

            except Exception as e:
                logging.debug(getTranslation("attempt_failed").format(str(e)))

            # Check if already verified successfully
            if check_verification_success(tab):
                return True

            # Random delay before next attempt
            time.sleep(random.uniform(*retry_interval))

        # Exceeded maximum retry attempts
        logging.error(getTranslation("verification_max_retries_reached").format(max_retries))
        logging.error(getTranslation("visit_project_for_info"))
        save_screenshot(tab, "failed")
        return False

    except Exception as e:
        error_msg = getTranslation("turnstile_exception").format(str(e))
        logging.error(error_msg)
        save_screenshot(tab, "error")
        raise TurnstileError(error_msg)



def get_cursor_session_token(tab, max_attempts: int = 3, retry_interval: int = 2) -> Optional[Tuple[str, str]]:
    """
    Get Cursor session token
    
    Args:
        tab: Browser tab object
        max_attempts: Maximum number of attempts
        retry_interval: Retry interval in seconds
        
    Returns:
        Tuple[str, str] | None: Returns (userId, accessToken) tuple if successful, None if failed
    """
    logging.info(getTranslation("start_getting_session_token"))
    
    # First try deep login method using UUID
    logging.info(getTranslation("try_deep_login"))
    
    def _generate_pkce_pair():
        """Generate PKCE verification pair"""
        code_verifier = secrets.token_urlsafe(43)
        code_challenge_digest = hashlib.sha256(code_verifier.encode('utf-8')).digest()
        code_challenge = base64.urlsafe_b64encode(code_challenge_digest).decode('utf-8').rstrip('=')    
        return code_verifier, code_challenge
    
    attempts = 0
    while attempts < max_attempts:
        try:
            verifier, challenge = _generate_pkce_pair()
            id = uuid.uuid4()
            client_login_url = f"https://www.cursor.com/cn/loginDeepControl?challenge={challenge}&uuid={id}&mode=login"
            
            logging.info(getTranslation("visiting_deep_login_url").format(client_login_url))
            tab.get(client_login_url)
            save_screenshot(tab, f"deeplogin_attempt_{attempts}")
            
            if tab.ele("xpath=//span[contains(text(), 'Yes, Log In')]", timeout=5):
                logging.info(getTranslation("clicking_confirm_login"))
                tab.ele("xpath=//span[contains(text(), 'Yes, Log In')]").click()
                time.sleep(1.5)
                
                auth_poll_url = f"https://api2.cursor.sh/auth/poll?uuid={id}&verifier={verifier}"
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Cursor/0.48.6 Chrome/132.0.6834.210 Electron/34.3.4 Safari/537.36",
                    "Accept": "*/*"
                }
                
                logging.info(getTranslation("polling_auth_status").format(auth_poll_url))
                response = requests.get(auth_poll_url, headers=headers, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    accessToken = data.get("accessToken", None)
                    authId = data.get("authId", "")
                    
                    if accessToken:
                        userId = ""
                        if len(authId.split("|")) > 1:
                            userId = authId.split("|")[1]
                        
                        logging.info(getTranslation("token_userid_success"))
                        return userId, accessToken
                else:
                    logging.error(getTranslation("api_request_failed").format(response.status_code))
            else:
                logging.warning(getTranslation("login_confirm_button_not_found"))
                
            attempts += 1
            if attempts < max_attempts:
                wait_time = retry_interval * attempts  # Gradually increase wait time
                logging.warning(getTranslation("token_attempt_failed").format(attempts, wait_time))
                save_screenshot(tab, f"token_attempt_{attempts}")
                time.sleep(wait_time)
                
        except Exception as e:
            logging.error(getTranslation("deep_login_token_failed").format(str(e)))
            attempts += 1
            save_screenshot(tab, f"token_error_{attempts}")
            if attempts < max_attempts:
                wait_time = retry_interval * attempts
                logging.warning(getTranslation("retry_in_seconds").format(wait_time))
                time.sleep(wait_time)
    
    # Return None after all attempts fail
    logging.error(getTranslation("max_attempts_reached").format(max_attempts))
    return None


def update_cursor_auth(email=None, access_token=None, refresh_token=None):
    """
    Convenience function to update Cursor authentication information
    """
    auth_manager = CursorAuthManager()
    return auth_manager.update_auth(email, access_token, refresh_token)


def sign_up_account(browser, tab, sign_up_url, settings_url, first_name, last_name, account, password, email_handler):
    """
    Handle the account sign-up process
    
    Args:
        browser: Browser instance
        tab: Browser tab
        sign_up_url: URL for the signup page
        settings_url: URL for the settings page
        first_name: First name for the account 
        last_name: Last name for the account
        account: Email account
        password: Password for the account
        email_handler: Email verification handler
        
    Returns:
        bool: True if signup was successful, False otherwise
    """
    logging.info(getTranslation("start_registration"))
    logging.info(getTranslation("visiting_login_page").format(sign_up_url))
    tab.get(sign_up_url)

    try:
        if tab.ele("@name=first_name"):
            logging.info(getTranslation("filling_personal_info"))
            tab.actions.click("@name=first_name").input(first_name)
            logging.info(getTranslation("input_first_name").format(first_name))
            time.sleep(random.uniform(1, 3))

            tab.actions.click("@name=last_name").input(last_name)
            logging.info(getTranslation("input_last_name").format(last_name))
            time.sleep(random.uniform(1, 3))

            tab.actions.click("@name=email").input(account)
            logging.info(getTranslation("input_email").format(account))
            time.sleep(random.uniform(1, 3))

            logging.info(getTranslation("submit_personal_info"))
            tab.actions.click("@type=submit")

    except Exception as e:
        logging.error(getTranslation("signup_page_access_failed").format(str(e)))
        return False

    handle_turnstile(tab)

    try:
        if tab.ele("@name=password"):
            logging.info(getTranslation("setting_password"))
            tab.ele("@name=password").input(password)
            time.sleep(random.uniform(1, 3))

            logging.info(getTranslation("submit_password"))
            tab.ele("@type=submit").click()
            logging.info(getTranslation("password_setup_complete"))

    except Exception as e:
        logging.error(getTranslation("password_setup_failed").format(str(e)))
        return False

    if tab.ele("This email is not available."):
        logging.error(getTranslation("email_already_used"))
        return False

    handle_turnstile(tab)

    while True:
        try:
            if tab.ele("Account Settings"):
                logging.info(getTranslation("registration_successful"))
                break
            if tab.ele("@data-index=0"):
                logging.info(getTranslation("getting_verification_code"))
                code = email_handler.get_verification_code()
                if not code:
                    logging.error(getTranslation("verification_code_failed"))
                    return False

                logging.info(getTranslation("verification_code_success").format(code))
                logging.info(getTranslation("entering_verification_code"))
                i = 0
                for digit in code:
                    tab.ele(f"@data-index={i}").input(digit)
                    time.sleep(random.uniform(0.1, 0.3))
                    i += 1
                logging.info(getTranslation("verification_code_complete"))
                break
        except Exception as e:
            logging.error(getTranslation("verification_process_error").format(str(e)))

    handle_turnstile(tab)
    wait_time = random.randint(3, 6)
    for i in range(wait_time):
        logging.info(getTranslation("waiting_for_processing").format(wait_time-i))
        time.sleep(1)

    logging.info(getTranslation("getting_account_info"))
    tab.get(settings_url)
    try:
        usage_selector = (
            "css:div.col-span-2 > div > div > div > div > "
            "div:nth-child(1) > div.flex.items-center.justify-between.gap-2 > "
            "span.font-mono.text-sm\\/\\[0\\.875rem\\]"
        )
        usage_ele = tab.ele(usage_selector)
        if usage_ele:
            usage_info = usage_ele.text
            total_usage = usage_info.split("/")[-1].strip()
            logging.info(getTranslation("account_usage_limit").format(total_usage))
            logging.info(getTranslation("visit_project_for_info"))

    except Exception as e:
        logging.error(getTranslation("get_account_limit_failed").format(str(e)))

    logging.info(getTranslation("registration_complete"))
    account_info = getTranslation("cursor_account_info").format(account, password)
    logging.info(account_info)
    time.sleep(5)
    return True


def get_env_directory():
    """
    Get the directory where the .env file is located.
    Returns the directory path if .env exists, otherwise returns the current directory.
    """
    # Check common locations for .env file
    possible_env_paths = [
        ".env",  # Current directory
        os.path.join(os.path.dirname(sys.executable), ".env"),  # Next to executable
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env")  # Project root
    ]
    
    for env_path in possible_env_paths:
        if os.path.exists(env_path):
            return os.path.dirname(os.path.abspath(env_path))
    
    # If .env is not found, return current directory
    return os.path.abspath(".")


class EmailGenerator:
    def __init__(
        self,
        password="".join(
            random.choices(
                "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*",
                k=12,
            )
        ),
        use_icloud=False,
        delete_after_use=False
    ):
        configInstance = Config()
        configInstance.print_config()
        self.names = self.load_names()
        self.default_password = password
        self.default_first_name = self.generate_random_name()
        self.default_last_name = self.generate_random_name()
        self.use_icloud = use_icloud
        self.delete_after_use = delete_after_use
        self.generated_email = None
        self.generateIcloudEmail = None
        self.deleteIcloudEmail = None
        
        # Try to load dotenv config if exists
        try:
            dotenv.load_dotenv()
        except Exception as e:
            logging.warning(getTranslation("env_file_load_failed").format(str(e)))
        
        # Try to import iCloud email generator if use_icloud is True
        if self.use_icloud:
            try:
                # Import the modules from the correct location
                from src.icloud.generateEmail import generateIcloudEmail
                from src.icloud.deleteEmail import deleteIcloudEmail
                self.generateIcloudEmail = generateIcloudEmail
                self.deleteIcloudEmail = deleteIcloudEmail
                logging.info(getTranslation("icloud_feature_enabled"))
            except ImportError:
                try:
                    # Try relative import as fallback
                    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    if current_dir not in sys.path:
                        sys.path.append(current_dir)
                    from icloud.generateEmail import generateIcloudEmail
                    from icloud.deleteEmail import deleteIcloudEmail
                    self.generateIcloudEmail = generateIcloudEmail
                    self.deleteIcloudEmail = deleteIcloudEmail
                    logging.info(getTranslation("icloud_feature_enabled"))
                except ImportError:
                    logging.error(getTranslation("icloud_module_import_failed_local"))
                    self.use_icloud = False

    def load_names(self):
        """Load names from names-dataset.txt file"""
        # Look for the file in the executable directory first, then in the project structure
        possible_paths = [
            "names-dataset.txt",  # In the current/executable directory
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                "data", "names-dataset.txt")  # Project structure path
        ]
        
        for names_file_path in possible_paths:
            try:
                with open(names_file_path, "r") as file:
                    logging.info(getTranslation("names_dataset_loaded").format(names_file_path))
                    return file.read().split()
            except FileNotFoundError:
                continue
                
        logging.error(getTranslation("names_dataset_not_found"))
        # Return a small set of default names as fallback
        return ["John", "Jane", "Michael", "Emma", "Robert", "Olivia"]

    def generate_random_name(self):
        """Generate a random username"""
        return random.choice(self.names)

    def get_emails_file_path(self):
        """Get the path to the emails.txt file, prioritizing accessible locations"""
        # Check if EMAIL_FILE_PATH is defined in .env
        env_path = os.environ.get("EMAIL_FILE_PATH")
        if env_path and os.path.exists(env_path):
            return env_path
        
        # First try to place emails.txt in the same directory as .env
        env_dir = get_env_directory()
        env_dir_path = os.path.join(env_dir, "emails.txt")
        
        # Try common locations
        possible_paths = [
            env_dir_path,  # Same directory as .env
            "data/emails.txt",  # In the current/executable directory
            os.path.join(os.path.dirname(sys.executable), "data", "emails.txt"),  # Next to executable
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                "data", "emails.txt")  # Project structure path
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
                
        # Default to the same location as .env file
        default_path = env_dir_path
        try:
            # Make sure the directory exists
            os.makedirs(os.path.dirname(default_path), exist_ok=True)
        except:
            # If creating directory fails, use data directory as fallback
            default_path = "data/emails.txt"
            os.makedirs(os.path.dirname(default_path), exist_ok=True)
            
        return default_path

    def generate_email(self, length=4):
        """
        Generate a random email address, using iCloud hidden email if iCloud feature is enabled
        """
        # If iCloud is enabled, try to generate an iCloud email
        if self.use_icloud:
            try:
                emails = self.generateIcloudEmail(1, True)
                if emails and len(emails) > 0:
                    self.generated_email = emails[0]
                    return self.generated_email
                else:
                    logging.warning(getTranslation("icloud_email_gen_failed"))
            except Exception as e:
                logging.error(getTranslation("icloud_email_gen_error").format(str(e)))
                logging.warning(getTranslation("using_local_email_list"))
            
        # If iCloud failed or not enabled, use local email list
        emails_file_path = self.get_emails_file_path()
        logging.info(f"Using emails file: {emails_file_path}")
        
        # Ensure the data directory exists
        os.makedirs(os.path.dirname(emails_file_path), exist_ok=True)
        
        # Check if emails.txt exists and has content
        try:
            if not os.path.exists(emails_file_path):
                with open(emails_file_path, "w") as f:
                    pass
                logging.warning(getTranslation("empty_email_file_created").format(emails_file_path))
                
            with open(emails_file_path, "r") as f:
                lines = f.readlines()
                
            if not lines:                    
                logging.warning(getTranslation("email_list_empty"))
                sys.exit(1)
                    
            first_email = lines[0].strip()
            self.generated_email = first_email
            
            # Write remaining emails back to file
            with open(emails_file_path, "w") as f:
                f.writelines(lines[1:])
                
            return self.generated_email
        except Exception as e:
            logging.error(getTranslation("email_file_read_error").format(str(e)))
            logging.warning(getTranslation("email_list_empty"))
            sys.exit(1)

    def delete_generated_email(self):
        """
        Delete the generated iCloud email if delete_after_use is enabled
        
        Returns:
            bool: True if deletion was successful or not needed, False otherwise
        """
        if not self.use_icloud or not self.delete_after_use or not self.generated_email:
            return True
            
        if not self.deleteIcloudEmail:
            logging.warning(getTranslation("delete_email_not_available"))
            return False
            
        try:
            logging.info(getTranslation("deleting_generated_email").format(self.generated_email))
            results = self.deleteIcloudEmail(self.generated_email)
            
            if results and len(results) > 0:
                email, success, message = results[0]
                if success:
                    logging.info(message)
                    return True
                else:
                    logging.error(message)
                    return False
            else:
                logging.error(getTranslation("delete_email_no_result"))
                return False
        except Exception as e:
            logging.error(getTranslation("delete_email_exception").format(str(e)))
            return False
            
    def get_account_info(self):
        """Get complete account information"""
        return {
            "email": self.generate_email(),
            "password": self.default_password,
            "first_name": self.default_first_name,
            "last_name": self.default_last_name,
        }


def get_user_agent():
    """Get user agent"""
    try:
        # Get user agent using JavaScript
        browser_manager = BrowserManager()
        browser = browser_manager.init_browser()
        user_agent = browser.latest_tab.run_js("return navigator.userAgent")
        browser_manager.quit()
        return user_agent
    except Exception as e:
        logging.error(getTranslation("get_user_agent_failed").format(str(e)))
        return None


def check_cursor_version():
    """Check cursor version"""
    pkg_path, main_path = patch_cursor_get_machine_id.get_cursor_paths()
    with open(pkg_path, "r", encoding="utf-8") as f:
        version = json.load(f)["version"]
    return patch_cursor_get_machine_id.version_check(version, min_version="0.45.0")


def reset_machine_id(greater_than_0_45):
    if greater_than_0_45:
        # Prompt to manually execute script https://github.com/Ryan0204/cursor-auto-icloud/blob/main/patch_cursor_get_machine_id.py
        go_cursor_help.go_cursor_help()
    else:
        MachineIDResetter().reset_machine_ids()


def print_end_message():
    logging.info(getTranslation("operation_complete"))


def save_account_to_csv(account_info, csv_path="accounts.csv"):
    """
    Save account information to a CSV file.
    
    Args:
        account_info: Dictionary containing account details
        csv_path: Path to the CSV file
    """
    # Check for CSV_FILE_PATH in environment variables
    env_csv_path = os.environ.get("CSV_FILE_PATH")
    if env_csv_path:
        csv_path = env_csv_path
    else:
        # Try to save accounts.csv in the same directory as .env
        env_dir = get_env_directory()
        csv_path = os.path.join(env_dir, "accounts.csv")
        
    file_path = Path(csv_path)
    logging.info(getTranslation("saving_account_to_csv").format(file_path))
    
    # Check if file exists to determine if we need to write headers
    file_exists = file_path.exists()
    
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(os.path.abspath(csv_path)), exist_ok=True)
        
        with open(file_path, mode='a', newline='') as file:
            fieldnames = ['created_date', 'email', 'password', 'access_token', 'refresh_token', 'first_name', 'last_name']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            
            # Write headers if file doesn't exist
            if not file_exists:
                writer.writeheader()
            
            # Add creation date to account info
            account_info_with_date = account_info.copy()
            account_info_with_date['created_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Write account info
            writer.writerow(account_info_with_date)
            
        logging.info(getTranslation("account_saved_to_csv").format(csv_path))
        return True
    except Exception as e:
        logging.error(getTranslation("save_account_failed").format(str(e)))
        return False


def main():
    """Main function for the Cursor Pro Keep Alive application."""
    greater_than_0_45 = check_cursor_version()
    browser_manager = None
    
    # Initialize the language manager
    lang_manager = LanguageManager()
    
    # Define URLs used in the program
    login_url = "https://authenticator.cursor.sh"
    sign_up_url = "https://authenticator.cursor.sh/sign-up"
    settings_url = "https://www.cursor.com/settings"
    
    try:
        logging.info(getTranslation("program_init"))
        ExitCursor()

        # Main menu loop to handle language switching
        while True:
            # Using the new getTranslation function for more readable code
            print(getTranslation("select_operation_mode"))
            print(getTranslation("reset_machine_code_only"))
            print(getTranslation("complete_registration"))
            print(getTranslation("generate_icloud_email"))
            print(getTranslation("complete_registration_icloud"))
            print(getTranslation("select_language"))

            while True:
                try:
                    # Using the original _ function for comparison
                    choice = int(input(_("enter_option")).strip())
                    if choice in [1, 2, 3, 4, 5]:
                        break
                    else:
                        print(_("invalid_option"))
                except ValueError:
                    print(_("enter_valid_number"))

            if choice == 5:
                # Switch language
                lang_manager.select_language()
                continue  # Return to the main menu with new language
            else:
                break  # Exit the menu loop and proceed with the selected option

        # Set delete_icloud_email_after_use based on user choice if using iCloud
        delete_icloud_email_after_use = False
        if choice == 4:  # If using iCloud email
            # Ask user if they want to delete the email after use
            delete_prompt = input(getTranslation("delete_email_prompt") + " (Y/N) [Y]: ").strip().upper()
            # Default is Yes (empty or Y)
            delete_icloud_email_after_use = delete_prompt != "N"
            if delete_icloud_email_after_use:
                logging.info(getTranslation("delete_after_use_enabled"))
            else:
                logging.info(getTranslation("delete_after_use_disabled"))

        if choice == 1:
            # Only execute machine code reset
            reset_machine_id(greater_than_0_45)
            logging.info(getTranslation("reset_complete"))
            print_end_message()
            sys.exit(0)
            
        elif choice == 3:
            # Generate iCloud hidden email
            try:
                count = int(input(getTranslation("enter_email_count")).strip())
                if count <= 0:
                    logging.error(getTranslation("email_count_gt_zero"))
                    sys.exit(1)
                    
                # Import the iCloud email generator
                try:
                    # Try direct import first
                    from src.icloud.generateEmail import generateIcloudEmail
                    emails = generateIcloudEmail(count)
                except ImportError:
                    try:
                        # Try with modified path as fallback
                        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                        if current_dir not in sys.path:
                            sys.path.append(current_dir)
                        from icloud.generateEmail import generateIcloudEmail
                        emails = generateIcloudEmail(count)
                    except ImportError:
                        logging.error(getTranslation("icloud_module_import_failed"))
                        print(getTranslation("install_dependencies"))
                        print_end_message()
                        sys.exit(1)
                
                if emails:
                    print(getTranslation("generated_emails").format(len(emails)))
                    for email in emails:
                        print(email)
                else:
                    print(getTranslation("no_emails_generated"))
            except ValueError:
                logging.error(getTranslation("invalid_count"))
                sys.exit(1)

        logging.info(getTranslation("initializing_browser"))

        # Get user_agent
        user_agent = get_user_agent()
        if not user_agent:
            logging.error(getTranslation("getting_user_agent_failed"))
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

        # Remove "HeadlessChrome" from user_agent
        user_agent = user_agent.replace("HeadlessChrome", "Chrome")

        browser_manager = BrowserManager()
        browser = browser_manager.init_browser(user_agent)

        # Get and print browser's user-agent
        user_agent = browser.latest_tab.run_js("return navigator.userAgent")

        logging.info(getTranslation("visit_project_for_info"))
        logging.info(getTranslation("config_info"))
        
        logging.info(getTranslation("generating_random_account"))

        # Use iCloud hidden email if choice is 4
        use_icloud = (choice == 4)
        email_generator = EmailGenerator(use_icloud=use_icloud, delete_after_use=delete_icloud_email_after_use)
        first_name = email_generator.default_first_name
        last_name = email_generator.default_last_name
        account = email_generator.generate_email()
        password = email_generator.default_password

        logging.info(getTranslation("generated_email_account").format(account))

        logging.info(getTranslation("initializing_email_verification"))
        email_handler = EmailVerificationHandler(account)

        auto_update_cursor_auth = True

        tab = browser.latest_tab

        tab.run_js("try { turnstile.reset() } catch(e) { }")

        logging.info(getTranslation("start_registration"))
        logging.info(getTranslation("visiting_login_page").format(login_url))
        tab.get(login_url)

        if sign_up_account(browser, tab, sign_up_url, settings_url, first_name, last_name, account, password, email_handler):
            logging.info(getTranslation("getting_session_token"))
            access_token, refresh_token = get_cursor_session_token(tab)
            if access_token and refresh_token:
                account_info = {
                    'email': account,
                    'password': password,
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'first_name': first_name,
                    'last_name': last_name
                }
                save_account_to_csv(account_info)
                logging.info(getTranslation("updating_auth_info"))
                update_cursor_auth(
                    email=account, access_token=access_token, refresh_token=refresh_token
                )
                
                # Delete iCloud email if option is enabled
                if use_icloud and delete_icloud_email_after_use:
                    logging.info(getTranslation("deleting_icloud_email_after_use"))
                    email_generator.delete_generated_email()
                
                logging.info(getTranslation("visit_project_for_info"))
                logging.info(getTranslation("resetting_machine_code"))
                reset_machine_id(greater_than_0_45)
                logging.info(getTranslation("all_operations_complete"))
                print_end_message()
            else:
                logging.error(getTranslation("session_token_failed"))

    except Exception as e:
        logging.error(getTranslation("program_execution_error").format(str(e)))
        import traceback

        logging.error(traceback.format_exc())
    finally:
        if browser_manager:
            browser_manager.quit()
        input(getTranslation("program_complete"))


# If this script is run directly, execute the main function
if __name__ == "__main__":
    main()
