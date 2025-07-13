# 🔗 IEEE Crawler Project: Automated Web Data Extraction with Python

## 📊 Advanced Python Programming — Final Project

👨‍💼 Author: Maor Nave

📂 Institution: Bar-Ilan University, Department of Information Science

🖊️ Submission Date: 17/08/2023

## 📌 Project Overview

This project delivers a fully-automated web crawler built in Python, targeting academic article metadata from the IEEE Journal platform. It is engineered to support scholarly research by systematically extracting data and organizing outputs into structured folders.

The system navigates journal issues from 2015 to 2023, processes article content, and stores metadata and article figures as JPG images. Each result is compiled into a clean and structured Excel file output.

The crawler uses a secure Windows Authenticator login, integrates Google Chrome + WebDriver, and depends on a flexible YAML-based configuration system.

## 📓 Features

### 📦 Data Extraction

Crawls IEEE article pages across defined years

Filters cover articles and invalid content

Captures: authors (with gender API), DOI, tables, figures, text, and publication metadata

### 📈 Output Organization

Excel File: All article records saved to output.xlsx

Figures Folder: JPGs (600x800 px), named by article and year

Repository Structure: Matches article names and decades for intuitive navigation

## ⚖️ Technical Considerations

Secure login via Windows Authenticator (academic credentials)

Selenium WebDriver for automated browser control

Smart folder management, image handling, and retry mechanisms for long crawls

## 🔧 System Components

### 💡 Configuration-Driven

YAML config files control login, browser paths, scraping options, and folder output

### 🕹️ Libraries Used

selenium, yaml, pandas, numpy, os, re, pickle, urllib, datetime, keyboard, genderize, time

## 📊 Functionality Highlights

Gender API integration with request quota handling

Resilient retry logic using call_function_with_retry

Modular design: separate modules for crawling, data extraction, login, and Excel export

## 📑 Key Project Files

| File / Folder                 | Purpose                                 |
|------------------------------|-----------------------------------------|
| `Main.py`                    | Entry point with crawl toggle settings  |
| `ActivationFunctions.py`     | All modular crawler functions           |
| `output.xlsx`                | Final article data summary              |
| `articels_figures_by_rev_year/` | JPG figures by year & article       |
| `articels_data_by_rev_year/` | Raw metadata (grouped by 10)            |
| `articels_lists_by_rev_year/`| All yearly article links                |
| `names_dict/`                | Gender API cache                        |
| `cover_list/`                | List of skipped cover articles          |



## 🔍 More Information

For full implementation details, function breakdowns, and setup instructions, please refer to the attached documentation files:

Code_guide.docx — Functional overview and logic

Full_Code.docx — Complete source code with inline comments

## 📧 Contact Me

I'm always open to feedback, collaboration, and new research opportunities.

📬 Email: maornanibar@gmail.com

💬 LinkedIn: linkedin.com/in/maornave

🧠 Research Interests:Computer Vision – Advanced image processing and physical simulationsData Analytics – Statistical analysis and database optimizationAI Applications – Machine & Deep learning
