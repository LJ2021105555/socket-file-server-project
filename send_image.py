import requests

def send_image():
    url = "http://127.0.0.1:8000"
    files = {'image': open('test.jpg', 'rb')}
    try:
        response = requests.post(url, files=files)
        print(f"Response from server: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    send_image()
