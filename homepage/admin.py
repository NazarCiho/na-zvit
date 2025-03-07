from django.contrib import admin

# Register your models here.
import jwt

# Секретний ключ
secret_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InNlY3JldCIsInN1YiI6ImTuiKgyNThkLTZiMmEtNDlmOC04ZmU5LTBlYTQ4NzhlMDQ4MyIsImlhdCI6MTc0MDMxNDc3NSwiZXhwIjoxNzQwMzE4Mzc1fQ.UhJh9EYl-sNPIpvyR56hQP8KUlVW_M-bH3w4Hr7fAa8'

# Нові дані
payload = {
    'username': 'secret',
    'sub': 'd258d-6b2a-49f8-8fe9-0ea4878e0483',
    'iat': 1740314775,
    'exp': 1740318375
}

# Створення нового токену
token = jwt.encode(payload, secret_key, algorithm='HS256')
print(token)
