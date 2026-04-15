import os
import sys

os.environ['POSTGRES_URL'] = 'sqlite:///./test.db'
os.environ['REDIS_URL'] = 'redis://localhost:6379/0'

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
