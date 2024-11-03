# streamlit-solar-dashboard
This project is about keeping a daily updated dashboard live using Streamlit.

#### Steps
1. Adding the following libraries: 
```
streamlit
pandas
numpy
psycopg2-binary 
python-dotenv
sqlalchemy
```
2. Write `get_data.py` script
3. Write `dashboard.py` script
4. Create dockerfile
5. Create docker image with ` docker build -t streamlit-solar-dashboard .`
6. Create docker container with `docker run --network local-network  -p 8501:8501 streamlit-solar-dashboard`

