import os
from enum import Enum
from typing import Dict

class Language(Enum):
    """Language enum for supported languages"""
    ENGLISH = "en"
    CHINESE = "zh"

class LanguageManager:
    """Manages language translations and settings for the application"""
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one instance of LanguageManager exists"""
        if cls._instance is None:
            cls._instance = super(LanguageManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the language manager with translations"""
        if self._initialized:
            return
            
        # Set default language (can be overridden by env var or user selection)
        env_lang = os.environ.get("LANGUAGE", "").lower()
        if env_lang == "en" or env_lang == "english":
            self.current_language = Language.ENGLISH
        elif env_lang == "zh" or env_lang == "chinese":
            self.current_language = Language.CHINESE
        else:
            self.current_language = Language.CHINESE  # Default to Chinese for backward compatibility
        
        self._translations = self._load_translations()
        self._initialized = True
    
    def _load_translations(self) -> Dict[str, Dict[str, str]]:
        """Load all translations for the application"""
        return {
            # Main UI messages
            "program_init": {
                Language.ENGLISH: "\n=== Initializing Program ===",
                Language.CHINESE: "\n=== Initializing Program ==="
            },
            "select_operation_mode": {
                Language.ENGLISH: "\nPlease select operation mode:",
                Language.CHINESE: "\nPlease select operation mode:"
            },
            "reset_machine_code_only": {
                Language.ENGLISH: "1. Reset machine code only",
                Language.CHINESE: "1. Reset machine code only"
            },
            "complete_registration": {
                Language.ENGLISH: "2. Complete registration process",
                Language.CHINESE: "2. Complete registration process"
            },
            "generate_icloud_email": {
                Language.ENGLISH: "3. Generate iCloud hidden email",
                Language.CHINESE: "3. Generate iCloud hidden email"
            },
            "complete_registration_icloud": {
                Language.ENGLISH: "4. Complete registration process (using iCloud hidden email)",
                Language.CHINESE: "4. Complete registration process (using iCloud hidden email)"
            },
            "select_language": {
                Language.ENGLISH: "5. Switch language (Current language: English)",
                Language.CHINESE: "5. Switch language (Current language: Chinese)"
            },
            "enter_option": {
                Language.ENGLISH: "Please enter option (1-5): ",
                Language.CHINESE: "Please enter option (1-5): "
            },
            "invalid_option": {
                Language.ENGLISH: "Invalid option, please try again",
                Language.CHINESE: "Invalid option, please try again"
            },
            "enter_valid_number": {
                Language.ENGLISH: "Please enter a valid number",
                Language.CHINESE: "Please enter a valid number"
            },
            
            # Machine code reset
            "reset_complete": {
                Language.ENGLISH: "Machine code reset complete",
                Language.CHINESE: "Machine code reset complete"
            },
            
            # iCloud email generation
            "enter_email_count": {
                Language.ENGLISH: "Please enter the number of emails to generate: ",
                Language.CHINESE: "Please enter the number of emails to generate: "
            },
            "email_count_gt_zero": {
                Language.ENGLISH: "Email count must be greater than 0",
                Language.CHINESE: "Email count must be greater than 0"
            },
            "icloud_module_import_failed": {
                Language.ENGLISH: "Failed to import iCloud email generation module",
                Language.CHINESE: "Failed to import iCloud email generation module"
            },
            "install_dependencies": {
                Language.ENGLISH: "Cannot import iCloud email generation module, please make sure all dependencies are installed",
                Language.CHINESE: "Cannot import iCloud email generation module, please make sure all dependencies are installed"
            },
            "generated_emails": {
                Language.ENGLISH: "Successfully generated {0} email addresses:",
                Language.CHINESE: "Successfully generated {0} email addresses:"
            },
            "no_emails_generated": {
                Language.ENGLISH: "No email addresses were generated",
                Language.CHINESE: "No email addresses were generated"
            },
            "invalid_count": {
                Language.ENGLISH: "Invalid count",
                Language.CHINESE: "Invalid count"
            },

            # Browser initialization
            "initializing_browser": {
                Language.ENGLISH: "Initializing browser...",
                Language.CHINESE: "Initializing browser..."
            },
            "getting_user_agent_failed": {
                Language.ENGLISH: "Failed to get user agent, using default",
                Language.CHINESE: "Failed to get user agent, using default"
            },
            
            # Configuration info
            "config_info": {
                Language.ENGLISH: "\n=== Configuration Info ===",
                Language.CHINESE: "\n=== Configuration Info ==="
            },
            "generating_random_account": {
                Language.ENGLISH: "Generating random account information...",
                Language.CHINESE: "Generating random account information..."
            },
            "generated_email_account": {
                Language.ENGLISH: "Generated email account: {0}",
                Language.CHINESE: "Generated email account: {0}"
            },
            "initializing_email_verification": {
                Language.ENGLISH: "Initializing email verification module...",
                Language.CHINESE: "Initializing email verification module..."
            },
            
            # Registration process
            "start_registration": {
                Language.ENGLISH: "\n=== Starting Registration Process ===",
                Language.CHINESE: "\n=== Starting Registration Process ==="
            },
            "visiting_login_page": {
                Language.ENGLISH: "Visiting login page: {0}",
                Language.CHINESE: "Visiting login page: {0}"
            },
            "getting_session_token": {
                Language.ENGLISH: "Getting session token...",
                Language.CHINESE: "Getting session token..."
            },
            "updating_auth_info": {
                Language.ENGLISH: "Updating authentication information...",
                Language.CHINESE: "Updating authentication information..."
            },
            "resetting_machine_code": {
                Language.ENGLISH: "Resetting machine code...",
                Language.CHINESE: "Resetting machine code..."
            },
            "all_operations_complete": {
                Language.ENGLISH: "All operations complete",
                Language.CHINESE: "All operations complete"
            },
            "session_token_failed": {
                Language.ENGLISH: "Failed to get session token, registration process incomplete",
                Language.CHINESE: "Failed to get session token, registration process incomplete"
            },
            
            # Spam folder related translations
            "checking_spam_folders": {
                Language.ENGLISH: "Verification code not found in inbox, checking spam/junk folders...",
                Language.CHINESE: "Verification code not found in inbox, checking spam/junk folders..."
            },
            "icloud_folder_list_failed": {
                Language.ENGLISH: "Failed to retrieve folder list from iCloud",
                Language.CHINESE: "Failed to retrieve folder list from iCloud"
            },
            "checking_folder": {
                Language.ENGLISH: "Checking folder: {0}",
                Language.CHINESE: "Checking folder: {0}"
            },
            "verification_code_found_in_spam": {
                Language.ENGLISH: "Verification code found in spam: {0} (folder: {1})",
                Language.CHINESE: "Verification code found in spam: {0} (folder: {1})"
            },
            "error_checking_folder": {
                Language.ENGLISH: "Error checking folder {0}: {1}",
                Language.CHINESE: "Error checking folder {0}: {1}"
            },
            "no_verification_code_in_spam": {
                Language.ENGLISH: "No verification code found in spam folders",
                Language.CHINESE: "No verification code found in spam folders"
            },
            "spam_folder_check_failed": {
                Language.ENGLISH: "Spam folder check failed: {0}",
                Language.CHINESE: "Spam folder check failed: {0}"
            },
            
            # Sign-up process specific
            "filling_personal_info": {
                Language.ENGLISH: "Filling personal information...",
                Language.CHINESE: "Filling personal information..."
            },
            "input_first_name": {
                Language.ENGLISH: "Entered first name: {0}",
                Language.CHINESE: "Entered first name: {0}"
            },
            "input_last_name": {
                Language.ENGLISH: "Entered last name: {0}",
                Language.CHINESE: "Entered last name: {0}"
            },
            "input_email": {
                Language.ENGLISH: "Entered email: {0}",
                Language.CHINESE: "Entered email: {0}"
            },
            "submit_personal_info": {
                Language.ENGLISH: "Submitting personal information...",
                Language.CHINESE: "Submitting personal information..."
            },
            "signup_page_access_failed": {
                Language.ENGLISH: "Failed to access signup page: {0}",
                Language.CHINESE: "Failed to access signup page: {0}"
            },
            "setting_password": {
                Language.ENGLISH: "Setting password...",
                Language.CHINESE: "Setting password..."
            },
            "submit_password": {
                Language.ENGLISH: "Submitting password...",
                Language.CHINESE: "Submitting password..."
            },
            "password_setup_complete": {
                Language.ENGLISH: "Password setup complete, waiting for system response...",
                Language.CHINESE: "Password setup complete, waiting for system response..."
            },
            "password_setup_failed": {
                Language.ENGLISH: "Password setup failed: {0}",
                Language.CHINESE: "Password setup failed: {0}"
            },
            "email_already_used": {
                Language.ENGLISH: "Registration failed: Email already in use",
                Language.CHINESE: "Registration failed: Email already in use"
            },
            "registration_successful": {
                Language.ENGLISH: "Registration successful - entered account settings page",
                Language.CHINESE: "Registration successful - entered account settings page"
            },
            "getting_verification_code": {
                Language.ENGLISH: "Getting email verification code...",
                Language.CHINESE: "Getting email verification code..."
            },
            "verification_code_failed": {
                Language.ENGLISH: "Failed to get verification code",
                Language.CHINESE: "Failed to get verification code"
            },
            "verification_code_success": {
                Language.ENGLISH: "Successfully got verification code: {0}",
                Language.CHINESE: "Successfully got verification code: {0}"
            },
            "entering_verification_code": {
                Language.ENGLISH: "Entering verification code...",
                Language.CHINESE: "Entering verification code..."
            },
            "verification_code_complete": {
                Language.ENGLISH: "Verification code input complete",
                Language.CHINESE: "Verification code input complete"
            },
            "verification_process_error": {
                Language.ENGLISH: "Verification process error: {0}",
                Language.CHINESE: "Verification process error: {0}"
            },
            "waiting_for_processing": {
                Language.ENGLISH: "Waiting for system processing... {0} seconds remaining",
                Language.CHINESE: "Waiting for system processing... {0} seconds remaining"
            },
            "getting_account_info": {
                Language.ENGLISH: "Getting account information...",
                Language.CHINESE: "Getting account information..."
            },
            "account_usage_limit": {
                Language.ENGLISH: "Account usage limit: {0}",
                Language.CHINESE: "Account usage limit: {0}"
            },
            "get_account_limit_failed": {
                Language.ENGLISH: "Failed to get account limit information: {0}",
                Language.CHINESE: "Failed to get account limit information: {0}"
            },
            "registration_complete": {
                Language.ENGLISH: "\n=== Registration Complete ===",
                Language.CHINESE: "\n=== Registration Complete ==="
            },
            "cursor_account_info": {
                Language.ENGLISH: "Cursor Account Information:\nEmail: {0}\nPassword: {1}",
                Language.CHINESE: "Cursor Account Information:\nEmail: {0}\nPassword: {1}"
            },
            
            # End messages
            "program_execution_error": {
                Language.ENGLISH: "Error during program execution: {0}",
                Language.CHINESE: "Error during program execution: {0}"
            },
            "program_complete": {
                Language.ENGLISH: "Press Enter to exit...",
                Language.CHINESE: "Press Enter to exit..."
            },
            "operation_complete": {
                Language.ENGLISH: "\n\n\n\n\n\n============================\nAll operations complete\n\n=== Get More Information ===\nPlease visit the open source project for more information: https://github.com/Ryan0204/cursor-auto-icloud",
                Language.CHINESE: "\n\n\n\n\n\n============================\nAll operations complete\n\n=== Get More Information ===\nPlease visit the open source project for more information: https://github.com/Ryan0204/cursor-auto-icloud"
            },
            
            # Language selection
            "select_new_language": {
                Language.ENGLISH: "\nSelect language / 选择语言:\n1. English\n2. 中文\nPlease enter option (1-2): ",
                Language.CHINESE: "\nSelect language / 选择语言:\n1. English\n2. 中文\nPlease enter option (1-2): "
            },
            "language_switched": {
                Language.ENGLISH: "Language switched to English",
                Language.CHINESE: "Language switched to Chinese"
            },
            
            # Application main
            "application_starting": {
                Language.ENGLISH: "Starting Cursor Pro Keep Alive application...",
                Language.CHINESE: "Starting Cursor Pro Keep Alive application..."
            },
            "application_error": {
                Language.ENGLISH: "An error occurred: {0}",
                Language.CHINESE: "An error occurred: {0}"
            },
            
            # Reset Machine
            "appdata_not_set": {
                Language.ENGLISH: "APPDATA environment variable is not set",
                Language.CHINESE: "APPDATA environment variable is not set"
            },
            "unsupported_os": {
                Language.ENGLISH: "Unsupported operating system: {0}",
                Language.CHINESE: "Unsupported operating system: {0}"
            },
            "checking_config_file": {
                Language.ENGLISH: "Checking configuration file",
                Language.CHINESE: "Checking configuration file"
            },
            "config_file_not_exist": {
                Language.ENGLISH: "Configuration file does not exist",
                Language.CHINESE: "Configuration file does not exist"
            },
            "config_file_no_permission": {
                Language.ENGLISH: "Cannot read/write configuration file, please check file permissions!",
                Language.CHINESE: "Cannot read/write configuration file, please check file permissions!"
            },
            "go_cursor_help_warning": {
                Language.ENGLISH: "If you have used go-cursor-help to modify the ID; please modify the read-only permission of the file",
                Language.CHINESE: "If you have used go-cursor-help to modify the ID; please modify the read-only permission of the file"
            },
            "reading_current_config": {
                Language.ENGLISH: "Reading current configuration",
                Language.CHINESE: "Reading current configuration"
            },
            "generating_new_machine_ids": {
                Language.ENGLISH: "Generating new machine identifiers",
                Language.CHINESE: "Generating new machine identifiers"
            },
            "saving_new_config": {
                Language.ENGLISH: "Saving new configuration",
                Language.CHINESE: "Saving new configuration"
            },
            "machine_id_reset_success": {
                Language.ENGLISH: "Machine identifier reset successful!",
                Language.CHINESE: "Machine identifier reset successful!"
            },
            "new_machine_ids": {
                Language.ENGLISH: "New machine identifiers",
                Language.CHINESE: "New machine identifiers"
            },
            "permission_error": {
                Language.ENGLISH: "Permission error",
                Language.CHINESE: "Permission error"
            },
            "run_as_admin_suggestion": {
                Language.ENGLISH: "Please try running this program as administrator",
                Language.CHINESE: "Please try running this program as administrator"
            },
            "reset_process_error": {
                Language.ENGLISH: "Reset process error",
                Language.CHINESE: "Reset process error"
            },
            "cursor_machine_id_reset_tool": {
                Language.ENGLISH: "Cursor Machine ID Reset Tool",
                Language.CHINESE: "Cursor Machine ID Reset Tool"
            },
            "press_enter_exit": {
                Language.ENGLISH: "Press Enter to exit",
                Language.CHINESE: "Press Enter to exit"
            },
            
            # Auth Manager
            "no_values_to_update": {
                Language.ENGLISH: "No values provided for update",
                Language.CHINESE: "No values provided for update"
            },
            "value_updated_success": {
                Language.ENGLISH: "Successfully updated {0}",
                Language.CHINESE: "Successfully updated {0}"
            },
            "value_not_found_or_unchanged": {
                Language.ENGLISH: "{0} not found or value unchanged",
                Language.CHINESE: "{0} not found or value unchanged"
            },
            "database_error": {
                Language.ENGLISH: "Database error: {0}",
                Language.CHINESE: "Database error: {0}"
            },
            "general_error": {
                Language.ENGLISH: "An error occurred: {0}",
                Language.CHINESE: "An error occurred: {0}"
            },
            
            # iCloud Email Generator
            "generate_email_failed": {
                Language.ENGLISH: "Failed to generate email: {0}",
                Language.CHINESE: "Failed to generate email: {0}"
            },
            "unknown_error": {
                Language.ENGLISH: "Unknown error",
                Language.CHINESE: "Unknown error"
            },
            "generate_email_failed_no_address": {
                Language.ENGLISH: "Failed to generate email: Unable to get email address",
                Language.CHINESE: "Failed to generate email: Unable to get email address"
            },
            "reserve_email_failed": {
                Language.ENGLISH: "Failed to reserve email: {0}",
                Language.CHINESE: "Failed to reserve email: {0}"
            },
            "email_generated_success": {
                Language.ENGLISH: "Email {0} generated successfully",
                Language.CHINESE: "Email {0} generated successfully"
            },
            "generate_email_error": {
                Language.ENGLISH: "Error occurred during email generation: {0}",
                Language.CHINESE: "Error occurred during email generation: {0}"
            },
            "icloud_cookies_not_configured": {
                Language.ENGLISH: "iCloud Cookies not configured, please set ICLOUD_COOKIES in the .env file",
                Language.CHINESE: "iCloud Cookies not configured, please set ICLOUD_COOKIES in the .env file"
            },
            "start_generating_emails": {
                Language.ENGLISH: "Starting to generate {0} iCloud hidden emails...",
                Language.CHINESE: "Starting to generate {0} iCloud hidden emails..."
            },
            "emails_generated_success": {
                Language.ENGLISH: "Successfully generated {0} email addresses",
                Language.CHINESE: "Successfully generated {0} email addresses"
            },
            "emails_saved_to_file": {
                Language.ENGLISH: "Email addresses have been saved to {0}",
                Language.CHINESE: "Email addresses have been saved to {0}"
            },
            "invalid_count_parameter": {
                Language.ENGLISH: "Invalid count parameter: {0}",
                Language.CHINESE: "Invalid count parameter: {0}"
            },
            
            # iCloud Hide My Email
            "generating_icloud_hidden_email": {
                Language.ENGLISH: "Generating iCloud hidden email...",
                Language.CHINESE: "Generating iCloud hidden email..."
            },
            "generate_email_timeout": {
                Language.ENGLISH: "Email generation timed out",
                Language.CHINESE: "Email generation timed out"
            },
            "request_timeout": {
                Language.ENGLISH: "Request timed out",
                Language.CHINESE: "Request timed out"
            },
            "reserving_email": {
                Language.ENGLISH: "Reserving email {0}...",
                Language.CHINESE: "Reserving email {0}..."
            },
            "reserve_email_timeout": {
                Language.ENGLISH: "Email reservation timed out",
                Language.CHINESE: "Email reservation timed out"
            },
            "getting_email_list": {
                Language.ENGLISH: "Getting email list...",
                Language.CHINESE: "Getting email list..."
            },
            "list_email_timeout": {
                Language.ENGLISH: "Getting email list timed out",
                Language.CHINESE: "Getting email list timed out"
            },
            "list_email_failed": {
                Language.ENGLISH: "Failed to get email list: {0}",
                Language.CHINESE: "Failed to get email list: {0}"
            },
            "deleting_email": {
                Language.ENGLISH: "Deleting email {0}...",
                Language.CHINESE: "Deleting email {0}..."
            },
            "delete_email_timeout": {
                Language.ENGLISH: "Deleting email timed out",
                Language.CHINESE: "Deleting email timed out"
            },
            "delete_email_failed": {
                Language.ENGLISH: "Failed to delete email: {0}",
                Language.CHINESE: "Failed to delete email: {0}"
            },
            
            # go_cursor_help.py
            "current_operating_system": {
                Language.ENGLISH: "Current operating system: {0}",
                Language.CHINESE: "Current operating system: {0}"
            },
            "executing_macos_command": {
                Language.ENGLISH: "Executing macOS command",
                Language.CHINESE: "Executing macOS command"
            },
            "executing_linux_command": {
                Language.ENGLISH: "Executing Linux command",
                Language.CHINESE: "Executing Linux command"
            },
            "executing_windows_command": {
                Language.ENGLISH: "Executing Windows command",
                Language.CHINESE: "Executing Windows command"
            },
            
            # exit_cursor.py
            "starting_cursor_exit": {
                Language.ENGLISH: "Starting to exit Cursor...",
                Language.CHINESE: "Starting to exit Cursor..."
            },
            "no_cursor_processes_found": {
                Language.ENGLISH: "No running Cursor processes found",
                Language.CHINESE: "No running Cursor processes found"
            },
            "all_cursor_processes_closed": {
                Language.ENGLISH: "All Cursor processes have been closed normally",
                Language.CHINESE: "All Cursor processes have been closed normally"
            },
            "processes_not_closed_in_time": {
                Language.ENGLISH: "The following processes did not close within the time limit: {0}",
                Language.CHINESE: "The following processes did not close within the time limit: {0}"
            },
            "error_closing_cursor": {
                Language.ENGLISH: "Error occurred while closing Cursor processes: {0}",
                Language.CHINESE: "Error occurred while closing Cursor processes: {0}"
            },
            
            # patch_cursor_get_machine_id.py
            "cursor_path_not_found_linux": {
                Language.ENGLISH: "Cursor installation path not found on Linux system",
                Language.CHINESE: "Cursor installation path not found on Linux system"
            },
            "cursor_path_not_default": {
                Language.ENGLISH: "Your Cursor installation is not in the default path, please create a symbolic link with the following command:",
                Language.CHINESE: "Your Cursor installation is not in the default path, please create a symbolic link with the following command:"
            },
            "create_symlink_command": {
                Language.ENGLISH: 'cmd /c mklink /d "C:\\Users\\<username>\\AppData\\Local\\Programs\\Cursor" "default installation path"',
                Language.CHINESE: 'cmd /c mklink /d "C:\\Users\\<username>\\AppData\\Local\\Programs\\Cursor" "default installation path"'
            },
            "example_command": {
                Language.ENGLISH: "For example:",
                Language.CHINESE: "For example:"
            },
            "example_command_path": {
                Language.ENGLISH: 'cmd /c mklink /d "C:\\Users\\<username>\\AppData\\Local\\Programs\\Cursor" "D:\\SoftWare\\cursor"',
                Language.CHINESE: 'cmd /c mklink /d "C:\\Users\\<username>\\AppData\\Local\\Programs\\Cursor" "D:\\SoftWare\\cursor"'
            },
            "file_not_exist": {
                Language.ENGLISH: "File does not exist: {0}",
                Language.CHINESE: "File does not exist: {0}"
            },
            "file_no_write_permission": {
                Language.ENGLISH: "No write permission for file: {0}",
                Language.CHINESE: "No write permission for file: {0}"
            },
            "invalid_version_format": {
                Language.ENGLISH: "Invalid version format: {0}",
                Language.CHINESE: "Invalid version format: {0}"
            },
            "version_below_minimum": {
                Language.ENGLISH: "Version {0} is below the minimum requirement {1}",
                Language.CHINESE: "Version {0} is below the minimum requirement {1}"
            },
            "version_above_maximum": {
                Language.ENGLISH: "Version {0} is above the maximum requirement {1}",
                Language.CHINESE: "Version {0} is above the maximum requirement {1}"
            },
            "version_check_failed": {
                Language.ENGLISH: "Version check failed: {0}",
                Language.CHINESE: "Version check failed: {0}"
            },
            "file_modified_success": {
                Language.ENGLISH: "File modified successfully",
                Language.CHINESE: "File modified successfully"
            },
            "file_modification_error": {
                Language.ENGLISH: "Error while modifying file: {0}",
                Language.CHINESE: "Error while modifying file: {0}"
            },
            "mainjs_backup_created": {
                Language.ENGLISH: "main.js backed up: {0}",
                Language.CHINESE: "main.js backed up: {0}"
            },
            "backup_failed": {
                Language.ENGLISH: "File backup failed: {0}",
                Language.CHINESE: "File backup failed: {0}"
            },
            "mainjs_restored": {
                Language.ENGLISH: "main.js has been restored",
                Language.CHINESE: "main.js has been restored"
            },
            "backup_not_found": {
                Language.ENGLISH: "Backup file not found",
                Language.CHINESE: "Backup file not found"
            },
            "restore_backup_failed": {
                Language.ENGLISH: "Failed to restore backup: {0}",
                Language.CHINESE: "Failed to restore backup: {0}"
            },
            "script_execution_started": {
                Language.ENGLISH: "Script execution started...",
                Language.CHINESE: "Script execution started..."
            },
            "backup_restore_complete": {
                Language.ENGLISH: "Backup restoration complete",
                Language.CHINESE: "Backup restoration complete"
            },
            "backup_restore_failed": {
                Language.ENGLISH: "Backup restoration failed",
                Language.CHINESE: "Backup restoration failed"
            },
            "current_cursor_version": {
                Language.ENGLISH: "Current Cursor version: {0}",
                Language.CHINESE: "Current Cursor version: {0}"
            },
            "reading_version_failed": {
                Language.ENGLISH: "Failed to read version: {0}",
                Language.CHINESE: "Failed to read version: {0}"
            },
            "version_not_supported": {
                Language.ENGLISH: "Version not supported (requires >= 0.45.x)",
                Language.CHINESE: "Version not supported (requires >= 0.45.x)"
            },
            "version_check_passed": {
                Language.ENGLISH: "Version check passed, preparing to modify files",
                Language.CHINESE: "Version check passed, preparing to modify files"
            },
            "backup_failed_abort": {
                Language.ENGLISH: "File backup failed, aborting operation",
                Language.CHINESE: "File backup failed, aborting operation"
            },
            "script_execution_complete": {
                Language.ENGLISH: "Script execution complete",
                Language.CHINESE: "Script execution complete"
            },
            "execution_error": {
                Language.ENGLISH: "Error during execution: {0}",
                Language.CHINESE: "Error during execution: {0}"
            },
            "press_enter_exit": {
                Language.ENGLISH: "\nExecution complete, press Enter to exit...",
                Language.CHINESE: "\nExecution complete, press Enter to exit..."
            },
            
            # New translation keys for config.py
            "env_file_not_exist": {
                Language.ENGLISH: "File {0} does not exist",
                Language.CHINESE: "File {0} does not exist"
            },
            "icloud_email": {
                Language.ENGLISH: "iCloud Email",
                Language.CHINESE: "iCloud Email"
            },
            "icloud_app_password": {
                Language.ENGLISH: "iCloud App Password",
                Language.CHINESE: "iCloud App Password"
            },
            "config_not_set": {
                Language.ENGLISH: "{name} not configured, please set {key} in the .env file",
                Language.CHINESE: "{name} not configured, please set {key} in the .env file"
            },
            "icloud_email_info": {
                Language.ENGLISH: "iCloud Email: {0}@icloud.com",
                Language.CHINESE: "iCloud Email: {0}@icloud.com"
            },
            "icloud_password_info": {
                Language.ENGLISH: "iCloud App Password: {0}",
                Language.CHINESE: "iCloud App Password: {0}"
            },
            "env_loaded_success": {
                Language.ENGLISH: "Environment variables loaded successfully!",
                Language.CHINESE: "Environment variables loaded successfully!"
            },
            "error_message": {
                Language.ENGLISH: "Error: {0}",
                Language.CHINESE: "Error: {0}"
            },
            "reading_version_failed": {
                Language.ENGLISH: "Failed to read version: {0}",
                Language.CHINESE: "Failed to read version: {0}"
            },
            # New translation keys for cursor_pro_keep_alive.py
            "screenshot_saved": {
                Language.ENGLISH: "Screenshot saved: {0}",
                Language.CHINESE: "Screenshot saved: {0}"
            },
            "screenshot_save_failed": {
                Language.ENGLISH: "Failed to save screenshot: {0}",
                Language.CHINESE: "Failed to save screenshot: {0}"
            },
            "verification_success_page": {
                Language.ENGLISH: "Verification success - Reached {0} page",
                Language.CHINESE: "Verification success - Reached {0} page"
            },
            "detecting_turnstile": {
                Language.ENGLISH: "Detecting Turnstile verification...",
                Language.CHINESE: "Detecting Turnstile verification..."
            },
            "verification_attempt": {
                Language.ENGLISH: "Verification attempt {0}",
                Language.CHINESE: "Verification attempt {0}"
            },
            "turnstile_detected": {
                Language.ENGLISH: "Turnstile verification detected, processing...",
                Language.CHINESE: "Turnstile verification detected, processing..."
            },
            "turnstile_passed": {
                Language.ENGLISH: "Turnstile verification passed",
                Language.CHINESE: "Turnstile verification passed"
            },
            "attempt_failed": {
                Language.ENGLISH: "Current attempt failed: {0}",
                Language.CHINESE: "Current attempt failed: {0}"
            },
            "verification_max_retries_reached": {
                Language.ENGLISH: "Verification failed - Maximum retries reached: {0}",
                Language.CHINESE: "Verification failed - Maximum retries reached: {0}"
            },
            "visit_project_for_info": {
                Language.ENGLISH: "Please visit the open source project for more information: https://github.com/Ryan0204/cursor-auto-icloud",
                Language.CHINESE: "Please visit the open source project for more information: https://github.com/Ryan0204/cursor-auto-icloud"
            },
            "turnstile_exception": {
                Language.ENGLISH: "Turnstile verification process exception: {0}",
                Language.CHINESE: "Turnstile verification process exception: {0}"
            },
            "getting_cookies": {
                Language.ENGLISH: "Getting cookies",
                Language.CHINESE: "Getting cookies"
            },
            "token_attempt_failed": {
                Language.ENGLISH: "Attempt {0} failed to get CursorSessionToken, retrying in {1} seconds...",
                Language.CHINESE: "Attempt {0} failed to get CursorSessionToken, retrying in {1} seconds..."
            },
            "token_max_attempts": {
                Language.ENGLISH: "Maximum attempts reached ({0}), failed to get CursorSessionToken",
                Language.CHINESE: "Maximum attempts reached ({0}), failed to get CursorSessionToken"
            },
            "get_cookie_failed": {
                Language.ENGLISH: "Failed to get cookie: {0}",
                Language.CHINESE: "Failed to get cookie: {0}"
            },
            "retry_in_seconds": {
                Language.ENGLISH: "Will retry in {0} seconds...",
                Language.CHINESE: "Will retry in {0} seconds..."
            },
            "env_file_load_failed": {
                Language.ENGLISH: "Failed to load .env file: {0}",
                Language.CHINESE: "Failed to load .env file: {0}"
            },
            "icloud_feature_enabled": {
                Language.ENGLISH: "iCloud hidden email feature enabled",
                Language.CHINESE: "iCloud hidden email feature enabled"
            },
            "icloud_module_import_failed_local": {
                Language.ENGLISH: "Failed to import iCloud email module, will use local email list",
                Language.CHINESE: "Failed to import iCloud email module, will use local email list"
            },
            "names_dataset_loaded": {
                Language.ENGLISH: "Names dataset loaded from {0}",
                Language.CHINESE: "Names dataset loaded from {0}"
            },
            "names_dataset_not_found": {
                Language.ENGLISH: "Names dataset file not found in any known location",
                Language.CHINESE: "Names dataset file not found in any known location"
            },
            "icloud_email_gen_failed": {
                Language.ENGLISH: "iCloud email generation failed, will use local email list",
                Language.CHINESE: "iCloud email generation failed, will use local email list"
            },
            "icloud_email_gen_error": {
                Language.ENGLISH: "iCloud email generation error: {0}",
                Language.CHINESE: "iCloud email generation error: {0}"
            },
            "using_local_email_list": {
                Language.ENGLISH: "Using local email list",
                Language.CHINESE: "Using local email list"
            },
            "empty_email_file_created": {
                Language.ENGLISH: "Created empty email list file at {0}",
                Language.CHINESE: "Created empty email list file at {0}"
            },
            "email_list_empty": {
                Language.ENGLISH: "Email list is empty, program execution completed",
                Language.CHINESE: "Email list is empty, program execution completed"
            },
            "email_file_read_error": {
                Language.ENGLISH: "Error reading email file: {0}",
                Language.CHINESE: "Error reading email file: {0}"
            },
            "get_user_agent_failed": {
                Language.ENGLISH: "Failed to get user agent: {0}",
                Language.CHINESE: "Failed to get user agent: {0}"
            },
            "saving_account_to_csv": {
                Language.ENGLISH: "Saving account information to CSV file: {0}",
                Language.CHINESE: "Saving account information to CSV file: {0}"
            },
            "account_saved_to_csv": {
                Language.ENGLISH: "Account information saved to {0}",
                Language.CHINESE: "Account information saved to {0}"
            },
            "save_account_failed": {
                Language.ENGLISH: "Failed to save account information: {0}",
                Language.CHINESE: "Failed to save account information: {0}"
            },
            # New translation keys for get_email_code.py
            "verification_code_attempt": {
                Language.ENGLISH: "Attempting to get verification code (attempt {0}/{1})...",
                Language.CHINESE: "Attempting to get verification code (attempt {0}/{1})..."
            },
            "verification_code_not_found_retry": {
                Language.ENGLISH: "Verification code not found, retrying in {0} seconds...",
                Language.CHINESE: "Verification code not found, retrying in {0} seconds..."
            },
            "verification_code_fetch_failed": {
                Language.ENGLISH: "Failed to get verification code: {0}",
                Language.CHINESE: "Failed to get verification code: {0}"
            },
            "error_will_retry": {
                Language.ENGLISH: "An error occurred, will retry in {0} seconds...",
                Language.CHINESE: "An error occurred, will retry in {0} seconds..."
            },
            "max_retries_reached_with_error": {
                Language.ENGLISH: "Failed to get verification code and reached maximum retries: {0}",
                Language.CHINESE: "Failed to get verification code and reached maximum retries: {0}"
            },
            "verification_code_not_found_after_attempts": {
                Language.ENGLISH: "Verification code not found after {0} attempts.",
                Language.CHINESE: "Verification code not found after {0} attempts."
            },
            "using_icloud_imap": {
                Language.ENGLISH: "Using iCloud IMAP to get email...",
                Language.CHINESE: "Using iCloud IMAP to get email..."
            },
            "verification_code_timeout": {
                Language.ENGLISH: "Verification code retrieval timed out",
                Language.CHINESE: "Verification code retrieval timed out"
            },
            "icloud_email_list_failed": {
                Language.ENGLISH: "Failed to get iCloud email list: {0}",
                Language.CHINESE: "Failed to get iCloud email list: {0}"
            },
            "no_emails_in_icloud": {
                Language.ENGLISH: "No emails found in iCloud folder: {0}",
                Language.CHINESE: "No emails found in iCloud folder: {0}"
            },
            "icloud_imap_fetch_failed": {
                Language.ENGLISH: "iCloud IMAP fetch failed: {0}",
                Language.CHINESE: "iCloud IMAP fetch failed: {0}"
            },
            "icloud_imap_fetch_status_failed": {
                Language.ENGLISH: "iCloud IMAP fetch failed with status: {0}",
                Language.CHINESE: "iCloud IMAP fetch failed with status: {0}"
            },
            "verification_code_found_in_email": {
                Language.ENGLISH: "Verification code found in iCloud email: {0}",
                Language.CHINESE: "Verification code found in iCloud email: {0}"
            },
            "no_verification_code_in_email": {
                Language.ENGLISH: "No verification code found in iCloud emails",
                Language.CHINESE: "No verification code found in iCloud emails"
            },
            "icloud_imap_operation_failed": {
                Language.ENGLISH: "iCloud IMAP operation failed: {0}",
                Language.CHINESE: "iCloud IMAP operation failed: {0}"
            },
            "email_body_decode_failed": {
                Language.ENGLISH: "Failed to decode email body: {0}",
                Language.CHINESE: "Failed to decode email body: {0}"
            },
            "none_type_attribute_error": {
                Language.ENGLISH: "INBOX is empty, checking other folders",
                Language.CHINESE: "INBOX is empty, checking other folders"
            },
            # New IMAP error handling translations
            "checking_imap_folder": {
                Language.ENGLISH: "Checking IMAP folder: {0}",
                Language.CHINESE: "Checking IMAP folder: {0}"
            },
            "empty_messages_response": {
                Language.ENGLISH: "IMAP server returned empty messages response",
                Language.CHINESE: "IMAP server returned empty messages response"
            },
            "empty_first_message_item": {
                Language.ENGLISH: "IMAP server returned empty first message item",
                Language.CHINESE: "IMAP server returned empty first message item"
            },
            "unexpected_message_type": {
                Language.ENGLISH: "Unexpected message type from IMAP server: {0}",
                Language.CHINESE: "Unexpected message type from IMAP server: {0}"
            },
            "inbox_empty_error": {
                Language.ENGLISH: "Inbox is empty - no emails in folder: {0}",
                Language.CHINESE: "Inbox is empty - no emails in folder: {0}"
            },
            # Token refresh translations
            "token_refresh_success": {
                Language.ENGLISH: "Successfully refreshed token",
                Language.CHINESE: "Successfully refreshed token"
            },
            "token_refresh_failed": {
                Language.ENGLISH: "Failed to refresh token: {0}",
                Language.CHINESE: "Failed to refresh token: {0}"
            },
            "token_refresh_exception": {
                Language.ENGLISH: "Exception during token refresh: {0}",
                Language.CHINESE: "Exception during token refresh: {0}"
            },
            # New translations for get_cursor_session_token function
            "start_getting_session_token": {
                Language.ENGLISH: "Starting to get session token",
                Language.CHINESE: "Starting to get session token"
            },
            "try_deep_login": {
                Language.ENGLISH: "Trying to get token using deep login method",
                Language.CHINESE: "Trying to get token using deep login method"
            },
            "visiting_deep_login_url": {
                Language.ENGLISH: "Visiting deep login URL: {0}",
                Language.CHINESE: "Visiting deep login URL: {0}"
            },
            "clicking_confirm_login": {
                Language.ENGLISH: "Clicking login confirmation button",
                Language.CHINESE: "Clicking login confirmation button"
            },
            "polling_auth_status": {
                Language.ENGLISH: "Polling authentication status: {0}",
                Language.CHINESE: "Polling authentication status: {0}"
            },
            "token_userid_success": {
                Language.ENGLISH: "Successfully obtained account token and userId",
                Language.CHINESE: "Successfully obtained account token and userId"
            },
            "api_request_failed": {
                Language.ENGLISH: "API request failed with status code: {0}",
                Language.CHINESE: "API request failed with status code: {0}"
            },
            "login_confirm_button_not_found": {
                Language.ENGLISH: "Login confirmation button not found",
                Language.CHINESE: "Login confirmation button not found"
            },
            "deep_login_token_failed": {
                Language.ENGLISH: "Deep login token acquisition failed: {0}",
                Language.CHINESE: "Deep login token acquisition failed: {0}"
            },
            "max_attempts_reached": {
                Language.ENGLISH: "Maximum attempts reached ({0}), failed to get session token",
                Language.CHINESE: "Maximum attempts reached ({0}), failed to get session token"
            },
            # Email deletion translations
            "no_emails_found": {
                Language.ENGLISH: "No emails found in iCloud account",
                Language.CHINESE: "No emails found in iCloud account"
            },
            "email_not_found": {
                Language.ENGLISH: "Email not found: {0}",
                Language.CHINESE: "Email not found: {0}"
            },
            "email_deleted_success": {
                Language.ENGLISH: "Email deleted successfully: {0}",
                Language.CHINESE: "Email deleted successfully: {0}"
            },
            "email_deletion_failed": {
                Language.ENGLISH: "Email deletion failed: {0}",
                Language.CHINESE: "Email deletion failed: {0}"
            },
            "no_emails_to_delete": {
                Language.ENGLISH: "No emails specified for deletion",
                Language.CHINESE: "No emails specified for deletion"
            },
            "email_deletion_error": {
                Language.ENGLISH: "Error during email deletion: {0}",
                Language.CHINESE: "Error during email deletion: {0}"
            },
            "deleting_emails": {
                Language.ENGLISH: "Deleting {0} email(s)...",
                Language.CHINESE: "Deleting {0} email(s)..."
            },
            "success": {
                Language.ENGLISH: "Success",
                Language.CHINESE: "Success"
            },
            "failed": {
                Language.ENGLISH: "Failed",
                Language.CHINESE: "Failed"
            },
            "no_emails_specified": {
                Language.ENGLISH: "No emails specified. Usage: deleteEmail.py email1@example.com [email2@example.com ...]",
                Language.CHINESE: "No emails specified. Usage: deleteEmail.py email1@example.com [email2@example.com ...]"
            },
            "delete_email_not_available": {
                Language.ENGLISH: "Email deletion function not available",
                Language.CHINESE: "Email deletion function not available"
            },
            "deleting_generated_email": {
                Language.ENGLISH: "Deleting generated email: {0}",
                Language.CHINESE: "Deleting generated email: {0}"
            },
            "delete_email_no_result": {
                Language.ENGLISH: "No result received from email deletion",
                Language.CHINESE: "No result received from email deletion"
            },
            "delete_email_exception": {
                Language.ENGLISH: "Error occurred while deleting email: {0}",
                Language.CHINESE: "Error occurred while deleting email: {0}"
            },
            "delete_after_use_enabled": {
                Language.ENGLISH: "Delete email after use option enabled",
                Language.CHINESE: "Delete email after use option enabled"
            },
            "deleting_icloud_email_after_use": {
                Language.ENGLISH: "Deleting iCloud email after successful registration",
                Language.CHINESE: "Deleting iCloud email after successful registration"
            },
            "delete_email_prompt": {
                Language.ENGLISH: "Delete iCloud email after successful registration?",
                Language.CHINESE: "Delete iCloud email after successful registration?"
            },
            "delete_after_use_disabled": {
                Language.ENGLISH: "Keep email after use option selected",
                Language.CHINESE: "Keep email after use option selected"
            },
            "deactivating_email": {
                Language.ENGLISH: "Deactivating email with ID: {0}",
                Language.CHINESE: "Deactivating email with ID: {0}"
            },
            "deactivate_email_timeout": {
                Language.ENGLISH: "Timeout while trying to deactivate email",
                Language.CHINESE: "Timeout while trying to deactivate email"
            },
            "deactivate_email_failed": {
                Language.ENGLISH: "Failed to deactivate email: {0}",
                Language.CHINESE: "Failed to deactivate email: {0}"
            },
            "email_deactivation_failed": {
                Language.ENGLISH: "Email deactivation failed: {0}",
                Language.CHINESE: "Email deactivation failed: {0}"
            },
            "email_missing_id": {
                Language.ENGLISH: "Email is missing anonymousId: {0}",
                Language.CHINESE: "Email is missing anonymousId: {0}"
            },
        }
    
    def get_text(self, key: str, *args) -> str:
        """
        Get translated text for the current language
        
        Args:
            key: The translation key
            *args: Optional format arguments
            
        Returns:
            str: The translated text
        """
        if key not in self._translations:
            # Fallback to key if translation not found
            return key
            
        translation = self._translations[key].get(self.current_language, key)
        
        # Apply formatting if args are provided
        if args:
            try:
                return translation.format(*args)
            except:
                return translation
                
        return translation
    
    def switch_language(self, language: Language) -> None:
        """
        Switch the current language
        
        Args:
            language: The language to switch to
        """
        self.current_language = language
        
    def toggle_language(self) -> Language:
        """
        Toggle between available languages
        
        Returns:
            Language: The new language
        """
        if self.current_language == Language.ENGLISH:
            self.current_language = Language.CHINESE
        else:
            self.current_language = Language.ENGLISH
            
        return self.current_language
        
    def select_language(self) -> Language:
        """
        Prompt user to select a language
        
        Returns:
            Language: The selected language
        """
        while True:
            try:
                choice = input(self.get_text("select_new_language")).strip()
                if choice == "1":
                    self.current_language = Language.ENGLISH
                    print(self.get_text("language_switched"))
                    break
                elif choice == "2":
                    self.current_language = Language.CHINESE
                    print(self.get_text("language_switched"))
                    break
                else:
                    print(self.get_text("invalid_option"))
            except ValueError:
                print(self.get_text("enter_valid_number"))
                
        return self.current_language


# Helper function for easier access to translations
def _(key: str, *args) -> str:
    """
    Shorthand function to get translated text
    
    Args:
        key: The translation key
        *args: Optional format arguments
        
    Returns:
        str: The translated text
    """
    return LanguageManager().get_text(key, *args)

# More descriptive alternative to _()
def getTranslation(key: str, *args) -> str:
    """
    Get translated text for the current language setting
    
    This is a more descriptive alternative to the shorthand _() function
    
    Args:
        key: The translation key
        *args: Optional format arguments
        
    Returns:
        str: The translated text
    """
    return LanguageManager().get_text(key, *args) 