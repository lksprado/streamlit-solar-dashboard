FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copie apenas os arquivos necessários para instalar as dependências
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copie o código do aplicativo
COPY app/src ./app/src

# Copie o arquivo .env para o diretório de trabalho
COPY .env ./

# Exponha a porta que o Streamlit usará
EXPOSE 8501

# Comando para executar o Streamlit
CMD ["streamlit", "run", "app/src/dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]