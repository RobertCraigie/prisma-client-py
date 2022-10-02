import json
import os

print(json.dumps(dict(os.environ), indent=2))
raise RuntimeError()
