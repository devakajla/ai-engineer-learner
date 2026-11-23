import pytest
from fastapi.testclient import TestClient

from app_under_test import NoteRepo, app, get_repo
