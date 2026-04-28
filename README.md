# YouTube ELT Pipeline

A data engineering project that extracts YouTube video statistics, loads them into PostgreSQL, and transforms them for analysis using Apache Airflow and Docker.

## Overview

This project implements an **ELT (Extract, Load, Transform)** pipeline that:

1. **Extracts** video statistics from a YouTube channel using the YouTube Data API
2. **Loads** the raw data into a PostgreSQL staging schema
3. **Transforms** the data and stores it in a core schema for analysis

The pipeline is orchestrated with **Apache Airflow** and runs on a schedule (daily by default). It includes data quality checks with **Soda** and containerization with **Docker**.

## Architecture

### DAGs

The project includes two main Apache Airflow DAGs:

- **`yt_elt_dag`** (Scheduled: Daily)
  - Extracts YouTube channel information using the YouTube Data API
  - Retrieves all video IDs from the channel's uploads playlist
  - Fetches detailed statistics for each video (views, likes, comments, duration, etc.)
  - Saves the raw data to a JSON file

- **`warehouse_dag`** (Scheduled: Daily)
  - Waits for `yt_elt_dag` to complete
  - Creates PostgreSQL schemas and tables (staging and core)
  - Loads extracted data into the staging schema
  - Deletes records for videos no longer in the channel
  - Transforms and loads data into the core schema for analysis
  - Runs data quality checks

### Database Schema

**Staging Schema** (`staging.yt_api`):
- Raw data from YouTube API
- Fields: `video_id`, `title`, `published_at`, `duration`, `view_count`, `like_count`, `comment_count`

**Core Schema** (`core.yt_api`):
- Transformed data for analysis
- Enhanced with `video_type` classification
- Optimized `duration` format (TIME instead of VARCHAR)

### File Structure

```
.
├── dags/                           # Airflow DAGs
│   ├── yt_elt_dag.py              # Extract DAG
│   ├── warehouse_dag.py           # Load & Transform DAG
│   ├── api/                       # YouTube API client
│   │   ├── video_stats.py         # YouTube API interactions
│   │   └── data_staging.py        # Data staging utilities
│   └── warehouse/                 # Database operations
│       ├── database.py            # PostgreSQL client
│       ├── data_loading.py        # JSON loading
│       └── data_transformation.py # Data transformations
├── data/                          # Raw extracted data (JSON files)
├── include/soda/                  # Data quality checks
│   ├── checks.yml                 # Soda check definitions
│   └── configuration.yml          # Soda configuration
├── tests/                         # Unit tests
├── docker/                        # Docker configuration
│   └── postgres/init-multiple-databases.sh  # Database initialization
├── docker-compose.yaml            # Docker services composition
├── dockerfile                     # Custom Airflow image
├── pyproject.toml                 # Project dependencies (uv)
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## Requirements

- Python 3.14+
- Docker & Docker Compose
- YouTube Data API key (from Google Cloud Console)
- Airflow 3.2.0+
- PostgreSQL 15+ (via Docker)

## Setup

### 1. Clone & Install Dependencies

```bash
# Clone the repository
cd ~/data_engineering/yt_elt

# Create and activate virtual environment (using uv)
uv venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
# or with uv:
uv pip install -r requirements.txt

# Install dev dependencies for Airflow
uv pip install apache-airflow>=3.2.0 apache-airflow-providers-postgres>=6.6.3
```

### 2. Configure Environment

Create a `.env` file with the required variables:

```bash
# YouTube API
API_KEY=your_youtube_api_key_here
CHANNEL_HANDLE=YourChannelHandle

# Airflow
_AIRFLOW_WWW_USER_USERNAME=airflow
_AIRFLOW_WWW_USER_PASSWORD=airflow
AIRFLOW_UID=50000
AIRFLOW_PROJ_DIR=.
```

To get a YouTube API key:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the YouTube Data API v3
4. Create an OAuth 2.0 credential (API key)

### 3. Start Services with Docker

```bash
# Build and start all services (Airflow, PostgreSQL, Redis, etc.)
docker-compose up -d

# Initialize Airflow database
docker-compose exec airflow-webserver airflow db init

# Create Airflow user
docker-compose exec airflow-webserver airflow users create \
    --username airflow \
    --password airflow \
    --firstname Airflow \
    --lastname Admin \
    --role Admin \
    --email admin@example.com
```

### 4. Access Airflow Web UI

- **URL**: http://localhost:8080
- **Username**: airflow
- **Password**: airflow

### 5. Set Airflow Variables

In the Airflow UI, set these variables under Admin → Variables:

- `API_KEY`: Your YouTube Data API key
- `CHANNEL_HANDLE`: The YouTube channel handle to track

## Usage

### Running the Pipeline

The pipelines are scheduled to run daily, but you can trigger them manually:

1. **Via Airflow UI**:
   - Navigate to DAGs section
   - Find `yt_elt_dag` or `warehouse_dag`
   - Click the "Trigger DAG" button

2. **Via CLI**:
   ```bash
   docker-compose exec airflow-webserver airflow dags trigger yt_elt_dag
   docker-compose exec airflow-webserver airflow dags trigger warehouse_dag
   ```

### Monitoring & Logs

- **Airflow Web UI**: Monitor task execution, view logs, and check DAG status
- **Logs Directory**: `./logs/` contains task-level logs organized by DAG and run ID

## Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_data_loading.py

# Run with coverage
pytest --cov=dags tests/
```

Test files are included for:
- Data loading and transformation
- Database operations
- Video statistics API client
- Data staging

## Data Quality

Soda checks are configured in `include/soda/` to validate:
- Data completeness (no null values in critical fields)
- Data freshness (recent timestamps)
- Value ranges and formats

Checks run automatically as part of the warehouse DAG.

## Development

### Project Structure

- **`dags/`**: Airflow DAG definitions
- **`dags/api/`**: YouTube API client and data staging
- **`dags/warehouse/`**: Database and transformation logic
- **`tests/`**: Unit tests
- **`include/soda/`**: Data quality check configurations
- **`docker/`**: Docker-specific configurations

### Dependencies

Managed via `pyproject.toml` using [uv](https://github.com/astral-sh/uv):

```toml
[project]
dependencies = [
    "requests>=2.33.1",           # HTTP client for API calls
    "python-dotenv>=1.2.2",       # Environment variable management
    "soda-core-postgres>=3.5.6",  # Data quality checks
    "pytest>=9.0.3",              # Testing framework
]

[tool.pytest.ini_options]
pythonpath = ["."]
```

## Troubleshooting

### Airflow not starting

```bash
# Check Docker logs
docker-compose logs airflow-webserver

# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Database connection errors

```bash
# Verify PostgreSQL is running
docker-compose ps

# Check PostgreSQL logs
docker-compose logs postgres
```

### API quota exceeded

- Monitor API usage in [Google Cloud Console](https://console.cloud.google.com/apis/dashboard)
- Adjust `MAX_RESULTS` in `dags/api/video_stats.py` if needed
- Consider implementing backoff/retry logic

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests: `pytest`
4. Commit and push
5. Submit a pull request

## License

This project is part of a data engineering learning initiative.

## Support

For issues or questions:
1. Check Airflow logs in the web UI
2. Review task logs in `./logs/` directory
3. Check database connection settings in Docker Compose
4. Verify YouTube API credentials and quotas
