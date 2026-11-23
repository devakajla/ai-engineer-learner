import pytest
from fastapi.testclient import TestClient

from app_under_test import app, get_weather_client
