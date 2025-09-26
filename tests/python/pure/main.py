import platform
import subprocess

def ping_host_subprocess(host):
    """
    Pings a host using the system's ping command and returns True if successful, False otherwise.
    """
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', host]  # Ping once

    try:
        # Use subprocess.run for more control and capturing output
        result = subprocess.run(command, capture_output=True, text=True, timeout=5)
        # Check for success based on return code or output content
        if result.returncode == 0:
            print(f"Ping to {host} successful.")
            return True
        else:
            print(f"Ping to {host} failed. Output:\n{result.stdout}{result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"Ping to {host} timed out.")
        return False
    except FileNotFoundError:
        print("Ping command not found. Ensure it's in your system's PATH.")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

# Example usage
target_host = "www.google.com"
if ping_host_subprocess(target_host):
    print(f"{target_host} is reachable.")
else:
    print(f"{target_host} is not reachable.")