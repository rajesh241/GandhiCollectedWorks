import json

def is_json(json_data):
  try:
    real_json=json.loads(json_data)
    valid_json = True
  except ValueError:
    valid_json=False
  return valid_json