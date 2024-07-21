# Scraping-products-using-caching


To run the code-
1) install libraries from requirements.txt using - pip install -r requirements.txt
2) install redis-stack using docker using - docker run -d --name redis-stack -p 6379:6379 -p 8001:8001 redis/redis-stack:latest
3) Run fastapi server using - uvicorn main:app --reload
4) Test the endpoint using - curl -X POST "http://127.0.0.1:8000/scrape" -H "Authorization: Bearer secret-token"
