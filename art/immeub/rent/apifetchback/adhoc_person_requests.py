"""
art/immeub/rent/apifetchback/adhoc_person_requests.py

"""
import requests
URL = 'https://localhost:8000'


def fetch_person_via_api():
  url = URL
  headers = {"Authorization": "Bearer YOUR_TOKEN"}
  params = {"limit": 10}
  try:
    # Always set a timeout to keep your script from freezing
    response = requests.get(url, headers=[], params=params, timeout=10)
    # Throws an HTTPError if the response code was an error (4xx, 5xx)
    response.raise_for_status()
    # Parse JSON data automatically
    data = response.json()
    print(data)
  except requests.exceptions.HTTPError as http_err:
    print(f"HTTP error occurred: {http_err}")
  except requests.exceptions.RequestException as err:
    print(f"Other error occurred: {err}")


def adhoctest1():
  """
  cpfs = ['12345678909']
  print('cpfs', cpfs)
  """
  # persons
  persons = []
  print('persons', persons)
  fetch_person_via_api()


def process():
  """
  """
  pass


if __name__ == '__main__':
  """
  process()
  batch_set_runonce_colations_to_mongodb_collections()
  """
  adhoctest1()
