
---
## 🔧 **Основні варіанти розгортання Apache Spark**
![[Основні варіанти розгортання Apache Spark | -]]

---

## 🧩 **Де може стояти Spark у архітектурі системи?**

**Spark** — це універсальний обчислювальний рушій, тому його можна інтегрувати на різних рівнях:

### 1. **ETL / Data Ingestion**
* Використовується для масового перетворення, очищення, об'єднання даних.
* Читає з Kafka, S3, HDFS, Redpanda, баз даних.
* Приклад: парсинг логів, трансформація сирих даних.
### 2. **Batch Processing**
* Аналітична обробка великих обсягів даних.
* Приклад: щоденний підрахунок метрик, тренування ML-моделей.
### 3. **Streaming / Near-Real-Time**
* Обробка потоку подій у реальному часі через `Spark Structured Streaming`.
* Приклад: аналіз поведінки користувачів у реальному часі.
### 4. **Machine Learning**
* Можна тренувати моделі через `MLlib` або інші бібліотеки.
* Приклад: кластеризація, рекомендаційні системи, anomaly detection.
### 5. **Serving Layer (рідше)**
* Не рекомендується для real-time inference, але іноді застосовується для підготовки попередньо оброблених даних для BI-систем.

---

## 📌 **Коли який варіант обрати?**

| Сценарій                                   | Рекомендований варіант       |
| ------------------------------------------ | ---------------------------- |
| Прототип/навчання                          | Local або Standalone         |
| Розгортання на локальному кластері         | Standalone або Docker        |
| Якщо вже є Hadoop                          | YARN                         |
| Обробка даних у хмарі                      | Cloud-native (Dataproc, EMR) |
| Хочете гнучке масштабування, DevOps-підхід | Kubernetes                   |
| CI/CD інтеграція                           | Docker + Kubernetes          |


---


## 🔁 **Альтернативи Apache Spark: за категоріями**

**DESC**: *Cучасні альтернативи Apache Spark, які частково або повністю закривають ті самі задачі: масштабована обробка даних, ETL, batch/streaming, аналітика, ML pipeline. Spark лишається потужним, але є нові й більш легковагові або гнучкі рішення — часто з кращою інтеграцією у cloud-native та microservice архітектури.*

### 🟠 **1. Universal Compute Engines**

| Технологія       | Основне                                                | Переваги                                            | Недоліки                                         |
| ---------------- | ------------------------------------------------------ | --------------------------------------------------- | ------------------------------------------------ |
| **Apache Flink** | Streaming-first (але й batch)                          | True real-time, low-latency, stateful               | Складніше в розгортанні, крутіша крива навчання  |
| **Apache Beam**  | Абстракція обчислень + runtime на Flink/Spark/Dataflow | Уніфікований API batch + streaming                  | Потрібен runner, складніший entry                |
| **Ray**          | Python-native, task-based                              | Чудово підходить для ML, DL, reinforcement learning | Не ETL-oriented, а скоріше паралельні обчислення |
| **Dask**         | Python-friendly аналог Spark                           | Працює з Pandas/Numpy, легкий для Python dev        | Менш масштабований, не для heavy-duty кластерів  |
| **Modin**        | Швидке масштабування Pandas                            | Проста заміна `import pandas`                       | Не для складних pipelines                        |
| **Mars**         | Tensor-based розподілена обробка                       | Альтернатива Spark + Dask з ML-нагрузкою            | Молодий проєкт                                   |
|                  |                                                        |                                                     |                                                  |
- [[Comparing Apache Spark vs Dask vs Ray]] :LiLink:

---

### 🟡 **2. Real-Time / Stream Processing (альтернатива Spark Streaming)**

|Технологія|Переваги|Для чого|
|---|---|---|
|**Kafka Streams**|Вбудовується у додатки, простий, масштабований|Streaming, windowing, aggregation|
|**ksqlDB**|SQL-підхід до потоків у Kafka|BI, аналітика в реальному часі|
|**Materialize**|PostgreSQL-like SQL поверх стрімів|Live dashboards, real-time views|
|**Redpanda WASM / Smart Modules**|Обробка прямо в брокері|Мінімізує затримку, гнучко|
|**Bytewax**|Pythonic, stateful streaming|Молодий, гарний для ML preprocessing|

---

### 🟢 **3. Data Lakes / Lakehouse Engines (альтернатива Spark SQL / batch)**

|Технологія|Пояснення|
|---|---|
|**Trino (ex-Presto)**|Distributed SQL for anything: S3, Hive, Delta, Kafka|
|**ClickHouse**|Ultrafast column store, особливо добре для time-series|
|**DuckDB**|Local OLAP DB, супер для embedded аналітики|
|**DataFusion / Ballista (Rust)**|Сучасний compute engine, альтернатива Spark в Arrow-екосистемі|
|**Velox (Meta)**|Новий рушій від Meta для compute pushdown, SQL, ML — ще молодий|

---

### 🔵 **4. ML Pipelines & Distributed ML (альтернатива MLlib)**

|Технологія|Переваги|
|---|---|
|**Ray + Ray Datasets + Ray Train**|Масштабовані ML pipelines|
|**Horovod**|Масштабоване DL тренування|
|**Kubeflow / Metaflow**|MLOps пайплайни|
|**MLflow**|Експерименти, моделі, сервіси|
|**HuggingFace Datasets + Accelerate**|Для роботи з DL-моделями у розподілених середовищах|

---

## 🔍 **Порівняння архітектурно**

| Питання                | Apache Spark                   | Альтернативи                               |
| ---------------------- | ------------------------------ | ------------------------------------------ |
| **Простота запуску**   | Складно (особливо в кластері)  | Dask, Ray — значно легші                   |
| **Streaming**          | Micro-batch (затримка ~100ms+) | Flink, Kafka Streams — true real-time      |
| **Latency**            | Секунди                        | Мілісекунди (Flink, ClickHouse)            |
| **ML**                 | Базова підтримка (MLlib)       | Ray, PyTorch, scikit-learn — повна свобода |
| **Хмара/Cloud Native** | Не cloud-first, але підтримує  | Beam, Flink, Ray — краще інтегруються      |
|                        |                                |                                            |

---

## 🔮 **Коли варто замінювати Spark?**

|Сценарій|Альтернатива|
|---|---|
|Потрібен **низький latency**, realtime обробка|**Apache Flink**, **Kafka Streams**, **Materialize**|
|**Python-heavy ML / SciPy stack**|**Ray**, **Dask**|
|Легкий, **single-node SQL-аналітика**|**DuckDB**, **ClickHouse**|
|Хочеш просту стрім-аналітику SQL|**ksqlDB**, **Redpanda + SmartModules**|
|Побудова **Lakehouse + SQL BI**|**Trino**, **Delta Lake + DuckDB**|
|MLOps / orchestration|**MLflow**, **Metaflow**, **Airflow + DVC**|

---

## 🧑‍🏫  use-case

| Завдання      | Spark         | Краще                        |
| ------------- | ------------- | ---------------------------- |
| Batch ETL     | 👍            | Trino, Dask (Modin)          |
| Streaming     | 👎 (затримка) | Flink, Kafka Streams, Bytwax |
| ML pipelines  | 😐            | Ray, Metaflow                |
| SQL-аналітика | 👍            | Trino, DuckDB, ClickHouse    |

---
