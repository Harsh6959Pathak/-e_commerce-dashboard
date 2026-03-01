# 📊 Business Intelligence Dashboard

A multi-page interactive Business Intelligence Dashboard built with **Streamlit** and **Plotly**, based on e-commerce sales data. Features a secure login system and three role-specific dashboards for CEO, Website Manager, and Marketing Manager.

---

## 🚀 Live Demo

> Deploy on Streamlit Community Cloud and paste your URL here.

---

## 🖼️ Preview

| Login Page | CEO Dashboard |
|---|---|
| Secure single-user login | KPIs, Revenue trends, Product analysis |

---

## 📁 Project Structure

```
cleaned/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── orders.csv                # Orders dataset
├── order_items.csv           # Order items dataset
├── order_item_refunds.csv    # Refunds dataset
├── products.csv              # Products dataset
└── README.md                 # Project documentation
```

---

## 📊 Dashboards

### 👔 CEO Dashboard
Provides a full executive overview of business performance.

- **KPIs:** Total Revenue, Total Profit, Total Orders, Profit Margin %, Conversion Rate, Revenue Growth %, Refund Amount, Refund Rate, Avg Order Value, Gross Margin %, Avg Items/Order
- **Charts:** New vs Returning Revenue, Revenue by Product, Revenue Trend, Cross Sell Analysis, Customer Growth Trend, Profit by Product, Top Products, Refund Rate Trend, Product Launch Analysis

### 🌐 Website Manager Dashboard
Tracks website traffic, sessions, and conversion performance.

- **KPIs:** Total Sessions, Users, Bounce Rate, Conversion Rate, Revenue/Session, Total Orders, Total Revenue, Cart Abandonment Rate
- **Charts:** Traffic Source Split, Sessions by Device, Sessions Trend, Bounce Rate by Device, Top Website Pages, Gsearch Non-Brand Funnel, Landing Page A/B Test

### 📣 Marketing Manager Dashboard
Monitors traffic sources, repeat visitors, and campaign effectiveness.

- **KPIs:** Gsearch Conversion, Total Sessions, Repeat Visitors, Repeat Session Rate, Avg Gap Days, Repeat Sessions, Conversion (Repeat)
- **Charts:** Traffic Source Volume, Conversion Rate by Source, Traffic Breakdown, New vs Repeat Sessions, Gsearch Traffic Trend, Repeat Rate by Channel, Avg Days Between Visits

---

## 🔐 Login Credentials

| Username | Password |
|---|---|
| `admin` | `admin123` |

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| [Streamlit](https://streamlit.io) | Web app framework |
| [Plotly](https://plotly.com) | Interactive charts |
| [Pandas](https://pandas.pydata.org) | Data manipulation |
| [NumPy](https://numpy.org) | Numerical operations |

---

## ⚙️ Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/bi-dashboard.git
cd bi-dashboard
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the app
```bash
streamlit run app.py
```

### 4. Open in browser
```
http://localhost:8501
```

---

## 📦 Dataset

The dashboard uses 4 CSV files representing a real e-commerce business from **2012 to 2015**:

| File | Description | Rows |
|---|---|---|
| `orders.csv` | Order-level data with revenue, cost, product info | ~32,000 |
| `order_items.csv` | Item-level breakdown per order | ~40,000 |
| `order_item_refunds.csv` | Refund transactions | ~1,700 |
| `products.csv` | Product catalog with launch dates | 4 |

**Products included:**
- The Original Mr. Fuzzy
- The Forever Love Bear
- The Birthday Sugar Panda
- The Hudson River Mini Bear

---

## ☁️ Deployment (Streamlit Community Cloud)

1. Push your project to a **GitHub repository**
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Sign in with GitHub
4. Click **"New app"** and select your repository
5. Set **Main file path** to `app.py`
6. Click **Deploy** ✅

---

## 🎛️ Filters

All dashboards support the following sidebar filters:

- **Year Range** — Slider to filter data by year (2012–2015)
- **Product** — Filter charts by a specific product
- **Items Purchased** — Filter by order size (1 or 2 items)

---

## 📄 License

This project was built for educational and portfolio purposes.

---

## 🙋‍♂️ Author

Built with ❤️ using Streamlit & Plotly.  
Feel free to fork, modify, and use for your own projects!
