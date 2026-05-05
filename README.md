# 💳 Retail Payment Retry & Revenue Leakage Analytics

### 🔗 Live Interactive Dashboard  

👉 https://hzhpv5r3xbwjygsxwn8cku.streamlit.app/

> Explore real-time insights on payment failures, retry behavior, and revenue recovery.
> 
## 🚀 Project Overview

This project analyzes **payment failures, retry behavior, revenue leakage, and data quality** in a retail store environment.

The dataset is **simulated**, but the behavior is designed based on real-world experience working around **self-checkout systems** where:

- Customers try TAP → it fails  
- They try TAP again  
- Then switch to INSERT CARD or CASH  
- Eventually complete the payment  

This small observation turned into a full data engineering + analytics project.

---

## 🎯 Real Story Behind This Project

While working around self-checkout systems, I noticed something simple but important:

```text
TAP does not always work in first attempt
```

People don’t leave.

They retry.

Sometimes:
- 2–3 TAP attempts  
- Then switch to card  
- Sometimes even more retries  

This made me think:

```text
How much revenue is at risk?
How much is actually recovered through retries?
What is the real behavior behind failed payments?
```

That is exactly what this project answers.

---

## 🧠 What This Project Solves

1. Which store locations are losing the most revenue?
2. How much revenue is recovered through retries?
3. How customers behave across payment methods?
4. Why payments fail (root cause)?
5. How reliable the raw data is?

---

## ⚙️ Data Generation (Important)

The dataset is **fully simulated using Python**, but built to mimic real retail behavior:

- 95% customers try TAP first  
- Many retry TAP 2–3 times  
- Then switch to INSERT CARD or CASH  
- Only ~5% transactions cancel  
- Multiple failure reasons included:
  - network issues  
  - insufficient funds  
  - PIN failure  

👉 This is NOT random data — it is behavior-driven simulation.

---

## 🏗️ Data Pipeline Architecture

```text
RAW DATA (Simulated)
        ↓
SILVER LAYER (Clean + Validate)
        ↓
QUARANTINE (Bad Data)
        ↓
GOLD TABLES (Business Metrics)
        ↓
STREAMLIT DASHBOARD
```

---

## ⚙️ Layers Explained

### 🥉 Silver Layer
- Cleans data  
- Removes invalid records  
- Fixes timestamps and amounts  
- Deduplicates  

---

### ⚠️ Quarantine Layer
- Stores bad data separately  
- Tracks issues like:
  - null values  
  - negative amounts  
  - future timestamps  
  - invalid sequences  

```text
Never trust raw data blindly
```

---

### 🥇 Gold Tables

#### 📊 Gold 1 — Revenue Leakage
Shows:
- how much money is lost  
- how much is recovered  

---

#### 🔁 Gold 2 — Retry Recovery
Shows:
- which retry attempt saves revenue  

---

#### 📅 Gold 3 — Monthly Behavior
Shows:
- TAP → retry → switch behavior  
- success trends over time  

---

#### 🚨 Gold 4 — Failure Root Cause
Shows:
- why payments fail  
- which method fails more  

---

## 📊 Dashboard

Built using **Streamlit**.

Features:
- Interactive filters  
- Dynamic charts  
- Clear business storytelling  

The dashboard explains:

```text
What is happening
Why it is happening
How it impacts revenue
```

---

## 🤖 Credits

- Streamlit dashboard design and structure: **Built with assistance from OpenAI (ChatGPT)**  
- README structure and writing assistance: **OpenAI (ChatGPT)**  

All:
- Data modeling  
- SQL logic  
- Pipeline design  
- Business reasoning  

were implemented and validated by me.

---

## 📁 Project Structure

```text
project/
│
├── app.py
├── requirements.txt
│
├── data/
├── sql/
├── dataset_generator.py
```

---

## ▶️ Run Project

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## 💡 Key Learning

This project shows:

- Data engineering thinking  
- Business-driven analytics  
- Real-world behavior simulation  
- Data quality awareness  
- End-to-end pipeline design  

---

## 🔥 Final Thought

Most projects show:

```text
What happened
```

This project shows:

```text
What happened + Why + Impact + Can we trust the data
```
