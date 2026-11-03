# 📈 Predictive Sales Forecasting & Business Analytics System

A comprehensive, production-grade Web Application built for sales trend analysis, inventory metrics, predictive revenue modeling, and forecast accuracy evaluation.

Developed as a **Second-Year B.Tech Computer Science & Engineering (CSE) Major Project**.

---

## 🌟 Key Highlights & Features

- **📊 Executive Dashboard (`/`)**: Real-time KPI summary cards (Total Revenue, Units Sold, Active Products, Total Records), interactive historical sales velocity chart, latest forecast summary, and database status indicator.
- **📁 Data Import & Multi-Rule Validation (`/upload`)**: Upload CSV files with automated checks for required columns, unparseable dates, negative prices/quantities, and empty datasets. Includes sample CSV download and one-click sample loader.
- **📉 Business Analytics (`/analytics`)**: Daily and monthly aggregations, total revenue over time, top 10 best-selling products by revenue, category market share distributions, regional territory performance, and statistical summaries (mean, median, peak, standard deviation).
- **🔮 Predictive Sales Forecasting (`/forecasting`)**:
  - **Moving Average Baseline (SMA)**: Dynamic rolling window smoothing with multi-step future extrapolation.
  - **Scikit-Learn Linear Regression**: Trend fitting using Ordinary Least Squares ($y = m \cdot t + c$) with $R^2$ score and regression equation.
  - **Comparative Forecast**: Side-by-side visualization of both algorithms over a customizable future horizon (7, 14, 30, 60, 90 days).
  - **Database Persistence**: Store forecast results directly into the MySQL `forecasts` table.
- **🎯 Holdout Model Evaluation (`/evaluation`)**:
  - **Strict Chronological Split**: Earliest 80% used for training, latest 20% reserved for testing. **Never randomly shuffled** to avoid data leakage.
  - **Error Metrics**: Mean Absolute Error (MAE), Root Mean Squared Error (RMSE), and Mean Absolute Percentage Error (MAPE).
  - **Plain-English Explanations**: Automatic identification of the winning model and contextual explanation in currency terms.
- **📑 Executive Reporting & Export (`/reports`)**: Printable layout (`@media print`), analytical assumptions, data limitations, and CSV export for forecast predictions.
- **💾 Dual-Engine Storage Architecture**:
  - **CSV Mode**: Works immediately out-of-the-box with zero configuration using bundled sample data.
  - **MySQL Mode**: Full schema, seed data, and automated initialization/sync functions for MySQL (`sales_forecasting_db`).

---

## 🛠️ Technology Stack

| Layer | Technologies Used |
| :--- | :--- |
| **Frontend** | HTML5, CSS3 (Modern, Responsive, Card Layout), Jinja2 Templating |
| **Backend Framework** | Python 3, Flask 3.x |
| **Data Processing & Analysis** | Pandas, NumPy |
| **Data Visualization** | Matplotlib (Headless Agg backend, Base64 PNG embedded rendering) |
| **Machine Learning** | Scikit-learn (`LinearRegression`) |
| **Database** | MySQL (with `mysql-connector-python`) & Local CSV Fallback Engine |

---

## 📐 Mathematical Formulations & Models

### 1. Revenue Calculation
$$\text{Revenue} = \text{Quantity} \times \text{Unit Price}$$

### 2. Simple Moving Average (SMA)
For historical smoothing with window size $W$:
$$\hat{y}_t = \frac{1}{W} \sum_{i=1}^{W} y_{t-i}$$

For future multi-step forecasting across horizon $H$, each forecasted point iteratively updates the historical window:
$$\hat{y}_{N+k} = \frac{1}{W} \sum_{j=1}^{W} \hat{y}_{N+k-j}$$

### 3. Linear Regression Trend
Fits an optimal Ordinary Least Squares (OLS) line over time index $t \in [0, N-1]$:
$$\hat{y}_t = m \cdot t + c$$
Where:
$$m = \frac{\sum (t - \bar{t})(y - \bar{y})}{\sum (t - \bar{t})^2}, \quad c = \bar{y} - m\bar{t}$$

### 4. Evaluation Metrics
- **Mean Absolute Error (MAE)** (Average deviation in actual currency):
  $$\text{MAE} = \frac{1}{n} \sum_{t=1}^{n} |y_t - \hat{y}_t|$$

- **Root Mean Squared Error (RMSE)** (Penalizes larger outliers more heavily):
  $$\text{RMSE} = \sqrt{\frac{1}{n} \sum_{t=1}^{n} (y_t - \hat{y}_t)^2}$$

- **Mean Absolute Percentage Error (MAPE)**:
  $$\text{MAPE} = \frac{100\%}{n} \sum_{t=1}^{n} \left| \frac{y_t - \hat{y}_t}{y_t} \right|$$

---

## 📁 Project Structure

```text
sales-forecasting-analytics/
│
├── app.py                      # Main Flask web application & route controller
├── requirements.txt            # Python dependencies
├── README.md                   # Comprehensive documentation & viva guide
├── .env.example                # Sample environment variables for MySQL
├── .gitignore                  # Git ignore rules
├── test_app.py                 # Automated test suite (validation, models, routes)
│
├── templates/                  # Jinja2 HTML templates
│   ├── base.html               # Navigation bar, notifications, footer
│   ├── index.html              # Page 1: Executive Dashboard
│   ├── upload.html             # Page 2: CSV Data Upload & Preview
│   ├── analytics.html          # Page 3: Business Analytics & Trends
│   ├── forecasting.html        # Page 4: Sales Forecasting (MA & LinReg)
│   ├── evaluation.html         # Page 5: Holdout Evaluation & Accuracy Metrics
│   └── reports.html            # Page 6: Executive Reports & Printable Audit
│
├── static/
│   ├── css/
│   │   └── style.css           # Clean, professional styling
│   └── images/                 # Static visual assets
│
├── src/                        # Modular Python backend logic
│   ├── __init__.py             # Package marker
│   ├── data_loader.py          # Dual storage loader (CSV & MySQL state management)
│   ├── validation.py           # Robust CSV schema, date, & numeric checks
│   ├── preprocessing.py        # Aggregation (daily/monthly), product & category KPIs
│   ├── forecasting.py          # Moving average & linear regression models + charts
│   ├── evaluation.py           # Chronological holdout split, MAE/RMSE calculation
│   └── database.py             # MySQL connector, schema execution & queries
│
├── data/
│   ├── sample_sales.csv        # Realistic 600+ record sample dataset (Retail Electronics)
│   └── uploads/                # Directory for user-uploaded CSV datasets
│
└── sql/
    ├── schema.sql              # MySQL DDL (products, sales, forecasts tables)
    └── seed_data.sql           # Starter SQL records for MySQL
```

---

## 💻 Windows Setup Instructions

Follow these exact steps on your Windows computer:

### Step 1: Open Terminal (PowerShell or Command Prompt)
Press `Win + R`, type `powershell` (or `cmd`), and press **Enter**. Navigate to the project directory:
```powershell
cd c:\Users\prani\Desktop\project.2py
```

### Step 2: Verify Python Installation
Ensure Python 3.10+ is installed:
```powershell
python --version
```

### Step 3: Create & Activate Virtual Environment (Recommended)
```powershell
python -m venv venv
```
Activate on PowerShell:
```powershell
.\venv\Scripts\Activate.ps1
```
*(If PowerShell says script execution is disabled, run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` and retry, or use Command Prompt: `venv\Scripts\activate.bat`)*

### Step 4: Install Dependencies
Install all required packages from `requirements.txt`:
```powershell
python -m pip install -r requirements.txt
```

### Step 5: (Optional) MySQL Database Setup
> 💡 **Notice**: The application works immediately in **CSV Mode** out-of-the-box without MySQL! If you wish to demonstrate MySQL integration for college marks:

1. Start your local MySQL server (via MySQL Workbench, XAMPP, or Services).
2. Copy `.env.example` to `.env`:
   ```powershell
   Copy-Item .env.example .env
   ```
3. Update `.env` with your MySQL credentials:
   ```ini
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=root
   DB_PASSWORD=your_password_here
   DB_NAME=sales_forecasting_db
   ```
4. On the web dashboard, click the button **"🛠️ Initialize MySQL DB"**, then click **"⬆️ Push Data to MySQL"**.

### Step 6: Start the Flask Application
Run:
```powershell
python app.py
```

You will see:
```text
==================================================================
🚀 Predictive Sales Forecasting & Business Analytics System
🌐 Running on http://127.0.0.1:5000
📂 Data mode: Dual Engine (CSV Out-of-the-box & MySQL Ready)
==================================================================
```

### Step 7: Open in Your Browser
Open your browser and visit:
👉 **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 🧪 Running the Automated Test Suite

To verify all validation rules, algorithms, and web routes:
```powershell
python test_app.py
```
This runs 15 unit and integration tests across data validation, moving average calculations, linear regression fitting, holdout error evaluation, and Flask routing.

---

## 🎓 College Viva / Project Presentation Questions & Answers

### Q1: Why do we never randomly shuffle time-series data for train/test split?
> **Answer**: In standard cross-sectional machine learning (e.g., classifying pictures of cats vs dogs), each observation is independent. In sales time series, observations have strong temporal sequence and auto-correlation (sales today depend on sales yesterday). If we shuffle data randomly, future points would leak into the training set, causing **data leakage (lookahead bias)**. The model would achieve unrealistically low errors during testing that fail in real-world deployment. Therefore, we strictly perform a **chronological holdout split** (training on earlier dates, testing on later dates).

### Q2: What is the business interpretation of Mean Absolute Error (MAE)?
> **Answer**: MAE represents the average magnitude of prediction errors in the original units of measurement (dollars/rupees). If MAE is $\$142.50$, it means that on an average day, our forecast deviated by $\$142.50$ from actual revenue.

### Q3: How does Root Mean Squared Error (RMSE) differ from MAE?
> **Answer**: MAE treats all errors linearly. RMSE squares errors before averaging and taking the square root. Because errors are squared, RMSE heavily penalizes large errors and outliers. If RMSE is substantially higher than MAE, it indicates that the model made a few very large forecasting errors.

### Q4: When would Moving Average outperform Linear Regression, and vice versa?
> **Answer**:
> - **Moving Average** performs better when sales fluctuate around a local mean without a sustained long-term slope, quickly adapting to recent shifts in consumer demand.
> - **Linear Regression** performs better when there is a steady secular trend (consistent year-over-year growth or decline), as moving average will constantly lag behind a steep upward or downward trend.

---

## 📜 License & Academic Integrity
This project is prepared for educational purposes as a B.Tech Computer Science and Engineering Capstone Project.
Feel free to extend and customize for academic presentations and demonstrations.
