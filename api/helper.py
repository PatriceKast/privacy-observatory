import json

# Helping functions
def is_json(myjson):
  try:
    json.loads(myjson)
  except ValueError as e:
    return False
  return True