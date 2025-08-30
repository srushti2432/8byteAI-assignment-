# 8Byte Assignment - Data Pipeline Project

This project was created by Srushti as part of the 8Byte Assignment.
It demonstrates the use of Apache Airflow with Docker to orchestrate a data pipeline.

# Setup & Installation

## 1. Clone & Extract Project
```
git clone https://github.com/srushti2432/8byteAI-assignment-.git
cd 8Byte-Assignment-Srushti
```
Or extract the provided ZIP file into your working directory.


## 2. Generate Required Keys

### Alpha Vantage API Key

* Go to (Alpha Vantage)[https://www.alphavantage.co/support/#api-key]
* Sign up and obtain your API Key.
* Update your .env with:

```
ALPHA_VANTAGE_API_KEY=your_api_key_here

```
### Fernet Key & Secret Key

Airflow requires a Fernet key and a Webserver Secret key.

* Generate Fernet Key:

```
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### Generate Secret Key:

```
python -c "import secrets; print(secrets.token_hex(32))"
```

### Update your .env file:

```
AIRFLOW_CORE_FERNET_KEY=your_fernet_key_here
AIRFLOW_WEBSERVER_SECRET_KEY=your_secret_key_here
```

## 3. Start Airflow Services

```
docker-compose up -d --build
```
<img width="1595" height="830" alt="assignment" src="https://github.com/user-attachments/assets/1591a86d-a7c9-4707-823d-eb7f278bf8e8" />

⚡ Important Notes

_Do not try to access Airflow Web UI (localhost:8080) immediately after running init._

The web server starts only when:

* **Airflow init process has exited successfully.**

* **Airflow Webserver starts with Gunicorn 2020.**

* **You should see a log line indicating:**

```
Listening at: http://0.0.0.0:8080
```

Once you see this message, open (http://localhost:8080)[http://localhost:8080] in your browser.

## Data Fetching

The script `fetch_and_store.py` fetches daily data by default.

If required, you can modify it to fetch hourly data instead (by updating the API call parameters in the script).

## Usage

* Log in to the Airflow Web UI.
* _username = admin7_
* _password = admin7_
  
<img width="1570" height="588" alt="image" src="https://github.com/user-attachments/assets/4cb7c318-c945-4d3f-b968-92197dc04c65" />


* Trigger your DAGs.
  
 <img width="1597" height="623" alt="image" src="https://github.com/user-attachments/assets/af96acbc-e086-4880-9cb3-550bbe8103b9" />



* Monitor logs, tasks, and data pipeline execution.
  
<img width="1600" height="786" alt="Capture2" src="https://github.com/user-attachments/assets/b2566b5f-cf3d-4ea5-9be2-6394633e7601" />

  

## Checking the Postgres Database

* Access the Postgres shell inside the container:

```
docker exec -it postgres psql -U postgres -d stockdb
```

* List all tables:

```
\dt
```

* View the first 10 rows of a specific table:

```
SELECT * FROM stock_prices LIMIT 10;
```

<img width="1105" height="510" alt="Capture3" src="https://github.com/user-attachments/assets/349f64f5-c346-4454-b773-4be6d915812e" />


## Author

This assignment was done by Srushti for the 8Byte Assignment.
