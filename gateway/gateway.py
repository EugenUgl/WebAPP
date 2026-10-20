import requests
from flask import Flask, Response, request

app = Flask(__name__)

# Адреса наших внутренних сервисов
AUTH_SERVICE_URL = "http://auth-backend:5000"
FRONTEND_SERVICE_URL = "http://frontend-service:5000"


@app.route("/", defaults={"path": ""}, methods=["GET", "POST", "PUT", "DELETE"])
@app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def proxy(path):
    # --- ЛОГИКА РОУТИНГА ---
    # Если запрос идет на корень сайта ("/"), отправляем его во frontend-service
    if path == "":
        url = f"{FRONTEND_SERVICE_URL}/"
    # Все остальные запросы (login, register, dashboard) отправляем в auth-backend
    else:
        url = f"{AUTH_SERVICE_URL}/{path}"

    headers = {key: value for key, value in request.headers if key.lower() != "host"}

    try:
        response = requests.request(
            method=request.method,
            url=url,
            headers=headers,
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False,
        )

        proxy_response = Response(response.content, response.status_code)
        current_gateway_host = request.host

        for key, value in response.headers.items():
            if key.lower() not in ["content-length", "connection", "transfer-encoding"]:
                if key.lower() == "location":
                    # Универсальная замена адресов бэкенда на адрес шлюза
                    value = value.replace(AUTH_SERVICE_URL, f"http://{current_gateway_host}")
                    value = value.replace(FRONTEND_SERVICE_URL, f"http://{current_gateway_host}")
                proxy_response.headers[key] = value

        return proxy_response

    except requests.exceptions.ConnectionError:
        return "<h1>Error 502: Bad Gateway. Один из внутренних сервисов недоступен.</h1>", 502


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
