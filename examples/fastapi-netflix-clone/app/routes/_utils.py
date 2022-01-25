from pathlib import Path
from fastapi.templating import Jinja2Templates


templates = Jinja2Templates(Path(__file__).parent.parent.parent / 'templates')
