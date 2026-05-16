# URL Shortener API

A simple URL shortener built using FastAPI and SQLite.

---

## Features

- Shorten long URLs
- Redirect using short codes
- Integration testing with pytest
- SQLite database
- FastAPI + SQLAlchemy

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd YOUR_REPOSITORY
```

---

### 2. Create virtual environment

```bash
python -m venv venv
```

---

### 3. Activate virtual environment

#### Windows

```bash
venv\Scripts\activate
```

#### Mac/Linux

```bash
source venv/bin/activate
```

---

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 5. Run the FastAPI server

```bash
uvicorn main:app --reload
```

---

## API Documentation

Open Swagger UI:

```text
http://127.0.0.1:8000/docs
```

---

## API Endpoints

### POST /shorten

Shortens a long URL.

Example Request:

```json
{
  "url": "https://example.com"
}
```

Example Response:

```json
{
  "short_code": "abc123"
}
```

---

### GET /redirect?code=abc123

Redirects to the original URL.

---

## Running Tests

Run all tests using:

```bash
pytest
```

Expected Output:

```text
1 passed
```

---

## Project Structure

```text
.
├── main.py
├── db.py
├── models.py
├── test_main.py
├── requirements.txt
├── README.md
└── .gitignore
```

### Test Execution

![Tests Passed](screenshots/test-passed.png)


## Load Testing

Load testing was performed using k6 with 10 simultaneous virtual users.

Command used:

```bash
k6 run load_test.js
```

### Load Test Result

![k6 Load Test](screenshots/k6-load-test.png)


## Performance Testing

Load testing was performed using k6.

### Run Load Test

Start the FastAPI server:

```bash
uvicorn main:app --reload
```

Run the k6 test:

```bash
k6 run load_test.js
```

---

### Export Performance Metrics

To export detailed metrics including p50, p90, p95, and p99:

```bash
k6 run --summary-export=summary.json load_test.js
```

This generates a `summary.json` file containing performance statistics.

---

### Percentile Metrics

The following metrics can be found inside `summary.json` under `http_req_duration`:

- p50
- p90
- p95
- p99

Example:

```json
{
  "p(50)": 4.12,
  "p(90)": 7.88,
  "p(95)": 8.91,
  "p(99)": 10.45
}
```

These values represent API response time percentiles in milliseconds.

---

### Load Test Configuration

- 10 simultaneous virtual users (VUs)
- 10 second test duration
- Tested endpoints:
  - `POST /shorten`
  - `GET /redirect`

### Performance Test Summary

![Performance Summary](screenshots/summary.png)

## Load Testing Results

| Concurrent Users | p50 | p90 | p95 | p99 |
|------------------|------|------|------|------|
| 50  | 7.57 ms | 63.02 ms | 162.97 ms | 427.20 ms |
| 100 | 30198.61 ms | 30312.81 ms | 30312.81 ms | 30331.36 ms |
| 200 | 32572.59 ms | 32631.38 ms | 32638.02 ms | 32643.56 ms |
| 500 | time out | time out | time out | time out |

## Latency Graph

![Latency Graph](screenshots/latency_graph.png)

## Load Testing Results

| Concurrent Users | Status |
|------------------|---------|
| 10   | Stable |
| 50   | Stable |
| 100  | Stable |
| 200  | Slight latency increase |
| 500  | API started failing / timing out |


## Observations

- The FastAPI application handled low and medium traffic efficiently.
- Latency increased as concurrent users increased.
- At 500 concurrent users, the server stopped responding correctly.
- SQLite and synchronous request handling became bottlenecks under high concurrency.

## Duplicate URL Handling

If the same URL is shortened multiple times, the API returns the existing short code instead of creating a new one.

This behavior is verified using automated integration tests.

## Duplicate URL Test

The API returns the same short code when the same URL is shortened multiple times.

### Test Result

![Duplicate URL Test](screenshots/duplicate-url-test.png)