# E-Commerce Competitive Price Intelligence Pipeline

A modular, production-oriented **Data Engineering project** designed to ingest, validate, transform, store, and analyze historical e-commerce product pricing data.

The project simulates a real-world competitive price monitoring system that can help businesses track competitor prices, identify price fluctuations, compare merchants, and analyze pricing trends over time.

> **Project Status:** 🚧 In Development

---

## 🎯 Project Objective

The goal of this project is to build an end-to-end Data Engineering pipeline that takes raw e-commerce pricing data and converts it into reliable, queryable, and actionable data.

The final system will support:

* Data ingestion from real-world e-commerce pricing data
* Raw data storage and processing
* Data validation and quality checks
* Data transformation and cleaning
* Incremental data loading
* PostgreSQL-based data storage
* Historical price tracking
* Competitor price comparison
* Price fluctuation analysis
* Pipeline execution monitoring
* Interactive web dashboard

---

## 🏗️ Planned Architecture

```text
                 E-Commerce Pricing Data
                           │
                           ▼
                  ┌─────────────────┐
                  │ Data Ingestion  │
                  └────────┬────────┘
                           │
                           ▼
                    Raw Data Layer
                           │
                           ▼
                  ┌─────────────────┐
                  │ Data Validation │
                  └────────┬────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │ Data Transformation │
                └──────────┬──────────┘
                           │
                           ▼
                    PostgreSQL
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
          Products     Merchants    Price History
              │            │            │
              └────────────┼────────────┘
                           ▼
                     SQL Analytics
                           │
                           ▼
                    Flask Backend
                           │
                           ▼
                  HTML/CSS/JavaScript
                           │
                           ▼
                   Analytics Dashboard
```

---

## 🛠️ Technology Stack

### Data Engineering

* Python
* Pandas
* NumPy
* PyArrow
* Requests

### Database

* PostgreSQL
* SQLAlchemy
* Psycopg2

### Backend

* Flask

### Frontend

* HTML
* CSS
* JavaScript
* Plotly

### Configuration & Development

* YAML
* Python-dotenv
* Pytest
* Black
* Flake8
* Git & GitHub

---

## 📁 Project Structure

```text
HighVolumnEcommerceCompetitorPriceMonitor/
│
├── artifacts/
│   ├── raw/
│   ├── processed/
│   ├── failed/
│   └── reports/
│
├── config/
│   ├── config.yaml
│   └── schema.yaml
│
├── constants/
│
├── components/
│   ├── data_ingestion.py
│   ├── data_validation.py
│   ├── data_transformation.py
│   ├── data_loading.py
│   └── data_analysis.py
│
├── entity/
│   ├── config_entity.py
│   └── artifact_entity.py
│
├── exception/
│   └── exception.py
│
├── logger/
│   └── logger.py
│
├── utils/
│   ├── common.py
│   ├── database.py
│   ├── file_utils.py
│   └── validation_utils.py
│
├── pipeline/
│   └── main_pipeline.py
│
├── database/
│   ├── connection.py
│   ├── schema.sql
│   └── queries.sql
│
├── dashboard/
│   ├── app.py
│   ├── templates/
│   └── static/
│
├── tests/
│
├── notebooks/
│
├── docs/
│
├── logs/
│
├── .env
├── .env.example
├── .gitignore
├── main.py
├── requirements.txt
└── README.md
```

---

## 🔄 Data Pipeline

The planned pipeline consists of the following stages:

### 1. Data Ingestion

Collect raw e-commerce pricing data and store it without modifying the original source data.

```text
Source
  ↓
Ingestion
  ↓
artifacts/raw/
```

### 2. Data Validation

Validate:

* Required columns
* Data types
* Missing values
* Duplicate records
* Invalid prices
* Schema consistency

### 3. Data Transformation

Transform raw data into an analytical format by:

* Cleaning product information
* Normalizing columns
* Converting data types
* Processing timestamps
* Preparing historical price records

### 4. Data Loading

Load validated and transformed data into PostgreSQL using SQLAlchemy.

### 5. Analytics

Generate metrics such as:

* Current price
* Previous price
* Price difference
* Percentage price change
* Cheapest merchant
* Average competitor price
* Price change frequency
* Historical price trends

### 6. Dashboard

A Flask-based web application will provide:

* Product search
* Product price history
* Competitor comparison
* Price trend charts
* Pipeline execution status
* Data quality information

---

## 🗄️ Planned Database Model

The analytical database will use PostgreSQL.

The core model will contain:

```text
                    dim_product
                         │
                         │
                         ▼
dim_merchant ──── fact_price ──── dim_date
                         │
                         ▼
                  Price Analytics
```

### Main tables

#### `dim_product`

Stores product-level information.

#### `dim_merchant`

Stores competitor/merchant information.

#### `dim_date`

Provides date-related analytical attributes.

#### `fact_price`

Stores historical product pricing observations.

#### `ingestion_runs`

Tracks pipeline execution, processing statistics, failures, and execution status.

---

## 📊 Example Business Questions

The completed system will be able to answer questions such as:

* Which competitor currently has the lowest price?
* How much has a product's price changed?
* Which products experienced the largest price increase?
* Which products experienced the largest price decrease?
* Which merchant changes prices most frequently?
* What is the average price of a product across competitors?
* How has a product's price changed over time?
* When was the lowest recorded price?
* When was the highest recorded price?
* How many records were successfully processed during each pipeline run?

---

## 🔐 Configuration & Security

Sensitive credentials will not be stored directly in the source code.

Environment variables will be used for database credentials and other secrets.

Example:

```env
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
```

The `.env` file should never be committed to GitHub.

Only `.env.example` should be included in the repository.

---

## 🧪 Testing

The project will include unit tests for individual pipeline components.

Planned test coverage includes:

```text
Data Ingestion
       ↓
Data Validation
       ↓
Data Transformation
       ↓
Data Loading
       ↓
Database Operations
```

Testing framework:

```text
pytest
```

---

## ☁️ Future AWS Deployment

The initial implementation will run locally.

The planned AWS architecture is:

```text
                    AWS
                     │
               ┌─────▼─────┐
               │    S3     │
               │ Raw Data  │
               └─────┬─────┘
                     │
                     ▼
              Python ETL
                     │
                     ▼
             ┌──────────────┐
             │ RDS PostgreSQL│
             └──────┬───────┘
                    │
                    ▼
              Flask Dashboard
```

Potential AWS services:

* Amazon S3
* Amazon RDS for PostgreSQL
* Amazon EC2
* AWS IAM
* Amazon CloudWatch

AWS deployment will be implemented after the local pipeline is stable.

---

## 🚧 Current Development Status

### Completed

* [x] Initial project structure
* [x] Configuration directory
* [x] Initial YAML configuration
* [x] Python environment setup
* [x] Dependency management
* [x] Configuration entity design

### In Progress

* [ ] Configuration utility layer
* [ ] Custom exception handling
* [ ] Logging system
* [ ] Data ingestion
* [ ] Data validation
* [ ] Data transformation
* [ ] PostgreSQL schema
* [ ] Data loading
* [ ] Incremental processing
* [ ] Price analytics
* [ ] Pipeline orchestration
* [ ] Flask backend
* [ ] Web dashboard
* [ ] Unit testing
* [ ] Dockerization
* [ ] AWS deployment

---

## 🎓 Learning Goals

This project is being developed to gain practical experience with:

* ETL pipeline architecture
* Data quality and validation
* Batch data processing
* Relational database design
* SQL analytics
* Incremental data processing
* Pipeline observability
* Error handling
* Modular Python architecture
* Backend development
* Cloud deployment
* Data Engineering best practices

---

## 👨‍💻 Author

**Chinmay**

B.Tech Computer Science & Engineering (Data Science)

This project is part of my Data Engineering portfolio and is being developed with a focus on production-oriented pipeline design and cloud-ready architecture.
