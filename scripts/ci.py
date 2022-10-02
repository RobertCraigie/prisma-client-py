import json
import os

print(json.dumps(os.environ, indent=2))
raise RuntimeError()
