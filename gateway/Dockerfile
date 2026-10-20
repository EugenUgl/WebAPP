FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host pypi.pythonhosted.org --trusted-host files.pythonhosted.org flask requests
COPY gateway.py .
EXPOSE 80
CMD ["python", "gateway.py"]
