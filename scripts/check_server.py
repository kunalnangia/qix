import socket
import requests
import time
from datetime import datetime

def check_port(host='localhost', port=8001, timeout=5):
    """Check if a port is open on the specified host"""
    try:
        socket.setdefaulttimeout(timeout)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception as e:
        print(f"Error checking port: {e}")
        return False

def check_http_endpoint(url, timeout=5):
    """Check if an HTTP endpoint is responding"""
    try:
        response = requests.get(url, timeout=timeout)
        return {
            'status': 'up',
            'status_code': response.status_code,
            'response_time': response.elapsed.total_seconds(),
            'timestamp': datetime.now().isoformat()
        }
    except requests.exceptions.RequestException as e:
        return {
            'status': 'down',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

def main():
    print("Checking server status...")
    
    # Check if port 8001 is open
    port_open = check_port()
    print(f"Port 8001 is {'open' if port_open else 'closed'}")
    
    if not port_open:
        print("Server is not running on port 8001. Please start the server first.")
        return
    
    # Check health endpoint
    print("\nTesting health endpoint...")
    health_url = "http://localhost:8001/health"
    health_status = check_http_endpoint(health_url)
    
    if health_status['status'] == 'up':
        print(f"✅ Health endpoint is UP (Status: {health_status['status_code']}, Response Time: {health_status['response_time']:.3f}s)")
    else:
        print(f"❌ Health endpoint is DOWN: {health_status['error']}")
    
    # Check API version endpoint
    print("\nTesting API version endpoint...")
    api_version_url = "http://localhost:8001/api/version"
    api_status = check_http_endpoint(api_version_url)
    
    if api_status['status'] == 'up':
        print(f"✅ API version endpoint is UP (Status: {api_status['status_code']}, Response Time: {api_status['response_time']:.3f}s)")
    else:
        print(f"❌ API version endpoint is DOWN: {api_status['error']}")
    
    # Check root endpoint
    print("\nTesting root endpoint...")
    root_url = "http://localhost:8001/"
    root_status = check_http_endpoint(root_url)
    
    if root_status['status'] == 'up':
        print(f"✅ Root endpoint is UP (Status: {root_status['status_code']}, Response Time: {root_status['response_time']:.3f}s)")
    else:
        print(f"❌ Root endpoint is DOWN: {root_status['error']}")

if __name__ == "__main__":
    main()
