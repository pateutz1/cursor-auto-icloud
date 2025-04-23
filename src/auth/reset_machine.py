import os
import sys
import json
import uuid
import hashlib
import shutil
from colorama import Fore, Style, init

# Add parent directory to path to import language module
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

try:
    from src.utils.language import getTranslation, _
except ImportError:
    from utils.language import getTranslation, _

# Initialize colorama
init()

# Define emoji and color constants
EMOJI = {
    "FILE": "📄",
    "BACKUP": "💾",
    "SUCCESS": "✅",
    "ERROR": "❌",
    "INFO": "ℹ️",
    "RESET": "🔄",
}


class MachineIDResetter:
    def __init__(self):
        # Determine operating system
        if sys.platform == "win32":  # Windows
            appdata = os.getenv("APPDATA")
            if appdata is None:
                raise EnvironmentError(getTranslation("appdata_not_set"))
            self.db_path = os.path.join(
                appdata, "Cursor", "User", "globalStorage", "storage.json"
            )
        elif sys.platform == "darwin":  # macOS
            self.db_path = os.path.abspath(
                os.path.expanduser(
                    "~/Library/Application Support/Cursor/User/globalStorage/storage.json"
                )
            )
        elif sys.platform == "linux":  # Linux and other Unix-like systems
            self.db_path = os.path.abspath(
                os.path.expanduser("~/.config/Cursor/User/globalStorage/storage.json")
            )
        else:
            raise NotImplementedError(getTranslation("unsupported_os").format(sys.platform))

    def generate_new_ids(self):
        """Generate new machine IDs"""
        # Generate new UUID
        dev_device_id = str(uuid.uuid4())

        # Generate new machineId (64 characters hexadecimal)
        machine_id = hashlib.sha256(os.urandom(32)).hexdigest()

        # Generate new macMachineId (128 characters hexadecimal)
        mac_machine_id = hashlib.sha512(os.urandom(64)).hexdigest()

        # Generate new sqmId
        sqm_id = "{" + str(uuid.uuid4()).upper() + "}"

        return {
            "telemetry.devDeviceId": dev_device_id,
            "telemetry.macMachineId": mac_machine_id,
            "telemetry.machineId": machine_id,
            "telemetry.sqmId": sqm_id,
        }

    def reset_machine_ids(self):
        """Reset machine IDs and backup original file"""
        try:
            print(f"{Fore.CYAN}{EMOJI['INFO']} {getTranslation('checking_config_file')}...{Style.RESET_ALL}")

            # Check if file exists
            if not os.path.exists(self.db_path):
                print(
                    f"{Fore.RED}{EMOJI['ERROR']} {getTranslation('config_file_not_exist')}: {self.db_path}{Style.RESET_ALL}"
                )
                return False

            # Check file permissions
            if not os.access(self.db_path, os.R_OK | os.W_OK):
                print(
                    f"{Fore.RED}{EMOJI['ERROR']} {getTranslation('config_file_no_permission')}{Style.RESET_ALL}"
                )
                print(
                    f"{Fore.RED}{EMOJI['ERROR']} {getTranslation('go_cursor_help_warning')} {self.db_path} {Style.RESET_ALL}"
                )
                return False

            # Read existing configuration
            print(f"{Fore.CYAN}{EMOJI['FILE']} {getTranslation('reading_current_config')}...{Style.RESET_ALL}")
            with open(self.db_path, "r", encoding="utf-8") as f:
                config = json.load(f)

            # Generate new IDs
            print(f"{Fore.CYAN}{EMOJI['RESET']} {getTranslation('generating_new_machine_ids')}...{Style.RESET_ALL}")
            new_ids = self.generate_new_ids()

            # Update configuration
            config.update(new_ids)

            # Save new configuration
            print(f"{Fore.CYAN}{EMOJI['FILE']} {getTranslation('saving_new_config')}...{Style.RESET_ALL}")
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)

            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {getTranslation('machine_id_reset_success')}{Style.RESET_ALL}")
            print(f"\n{Fore.CYAN}{getTranslation('new_machine_ids')}:{Style.RESET_ALL}")
            for key, value in new_ids.items():
                print(f"{EMOJI['INFO']} {key}: {Fore.GREEN}{value}{Style.RESET_ALL}")

            return True

        except PermissionError as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} {getTranslation('permission_error')}: {str(e)}{Style.RESET_ALL}")
            print(
                f"{Fore.YELLOW}{EMOJI['INFO']} {getTranslation('run_as_admin_suggestion')}{Style.RESET_ALL}"
            )
            return False
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} {getTranslation('reset_process_error')}: {str(e)}{Style.RESET_ALL}")

            return False


if __name__ == "__main__":
    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{EMOJI['RESET']} {getTranslation('cursor_machine_id_reset_tool')}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")

    resetter = MachineIDResetter()
    resetter.reset_machine_ids()

    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    input(f"{EMOJI['INFO']} {getTranslation('press_enter_exit')}...")
