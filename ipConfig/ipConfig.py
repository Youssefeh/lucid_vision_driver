import subprocess
import re
import sys


def list_cameras():
    """Scans for available cameras and returns their MAC and IP details."""
    try:
        result = subprocess.run(
            ["./IpConfigUtility", "/list"],
            stdout=subprocess.PIPE,
            input="\n",  # Simulate Enter key press
            text=True
        )
        output = result.stdout
        cameras = []
        for line in output.splitlines():
            match = re.match(r"\[(\d+)]\s+([\w:]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+.*", line)
            if match:
                index, mac, ip, subnet, gateway = match.groups()
                cameras.append({
                    "index": index,
                    "mac": mac,
                    "ip": ip,
                    "subnet": subnet,
                    "gateway": gateway
                })
        return cameras
    except Exception as e:
        print(f"Error listing cameras: {e}")
        sys.exit(1)


def apply_camera_ip(mac_address, new_ip, subnet="255.255.0.0", gateway="0.0.0.0"):
    """
    Forces and then persists a new IP address for the camera with the specified MAC address.
    Combines the operations into one final message.
    """
    try:
        # Force IP
        subprocess.run(
            ["./IpConfigUtility", "/force", "-a", new_ip, "-m", mac_address, "-s", subnet, "-g", gateway],
            stdout=subprocess.PIPE,
            input="\n",  # Simulate Enter key press
            text=True
        )

        # Persist IP
        subprocess.run(
            ["./IpConfigUtility", "/persist", "-a", new_ip, "-m", mac_address, "-s", subnet, "-g", gateway],
            stdout=subprocess.PIPE,
            input="\n",  # Simulate Enter key press
            text=True
        )

        print(f"Successfully applied IP {new_ip} to camera with MAC {mac_address}.")
    except Exception as e:
        print(f"Failed to apply IP {new_ip} to camera with MAC {mac_address}: {e}")


def assign_ips_to_cameras():
    """Automatically assigns new IP addresses to all detected cameras."""
    cameras = list_cameras()
    if not cameras:
        print("No cameras found.")
        return

    print("Detected Cameras:")
    for cam in cameras:
        print(f"MAC: {cam['mac']}, Current IP: {cam['ip']}, Subnet: {cam['subnet']}, Gateway: {cam['gateway']}")

    print("\nEnter new IP addresses for the cameras.")
    for cam in cameras:
        while True:
            new_ip = input(f"Enter new IP for camera with MAC {cam['mac']}: ")
            if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", new_ip):
                break
            print("Invalid IP address format. Please try again.")
        
        apply_camera_ip(cam["mac"], new_ip)


if __name__ == "__main__":
    assign_ips_to_cameras()
