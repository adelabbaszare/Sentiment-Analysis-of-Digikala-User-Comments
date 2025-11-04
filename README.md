# Sentiment Analysis of Digikala User Comments

This project performs a complete Sentiment Analysis on the user comments from the Digikala website. The project workflow includes automatic data collection via web scraping, cleaning and preprocessing of Persian text, Exploratory Data Analysis (EDA) to discover patterns, and finally, training and evaluating several machine learning models to classify comments into positive and negative categories.

## Project Structure

The file and folder structure is organized as follows:

```
SentimentProject/
├── data/
│   ├── digikala_comments.csv
│   └── ccleaned_digikala_comments.csv
├── notebooks/
│   ├── Sentiment Project Notebook.ipynb
│   ├── Digikala Web Scraping.py
│   ├── persian_stopwords.txt
│   └── B Lotus Bold.ttf
├── figures/
│   ├── positive_wordcloud.png
│   ├── negative_frequent_words.png
│   └── ... (Other images)
├── reports/
│   └── final_report.pdf
├── README.md
└── requirements.txt
```

## Main Project Steps
- **Web Scraping:** Extracting user comments from various product pages on Digikala using Selenium and BeautifulSoup.
- **Text Preprocessing:** Preparing Persian comments for analysis, including normalization, tokenization, stemming, and removal of stopwords.
- **Exploratory Data Analysis (EDA):** Visualizing the data to better understand the distribution of ratings, sentiments, and the most frequent words in positive and negative comments through charts and Word Clouds.
- **Text Vectorization:** Converting the cleaned texts into numerical vectors using the TF-IDF model for use in machine learning models.
- **Modeling and Evaluation:** Training and evaluating four different models (Logistic Regression, Naive Bayes, SVM, Random Forest) and comparing their performance using metrics like Accuracy and the Confusion Matrix.

---

## Setup and Installation

Follow the steps below to run this project.

### 1. Clone Repository
First, clone the project from GitHub (or any other source):
```bash
git clone <your-project-URL>
cd SentimentProject
```

### 2. Create a Virtual Environment
To avoid library conflicts, create a virtual environment named `venv`:
```bash
python -m venv venv
```

### 3. Activate the Virtual Environment
Execute the appropriate command depending on your operating system:

- **On Windows:**
  ```bash
  venv\Scripts\activate
  ```

- **On macOS/Linux:**
  ```bash
  source venv/bin/activate
  ```
After running this command, the name of the virtual environment `(venv)` will appear at the beginning of your command prompt.

### 4. Install Required Libraries
All necessary libraries are listed in the `requirements.txt` file. Install them with the following command:
```bash
pip install -r requirements.txt
```
**Note:** If you don't have the `requirements.txt` file, you can create it with the following content:
<details>
  <summary>requirements.txt content</summary>
  
  ```
  pandas
  numpy
  hazm
  arabic_reshaper
  bidi
  parsivar
  matplotlib
  seaborn
  wordcloud
  scikit-learn
  selenium
  beautifulsoup4
  ipykernel
  ```
</details>

### 5. Add the Virtual Environment as a Jupyter Kernel
To be able to run the notebook with the libraries installed in the virtual environment, you need to add this environment as a kernel to Jupyter.

- First, ensure `ipykernel` is installed (it is included in the `requirements.txt` file).
- Then, run the following command in the terminal (while the virtual environment is activated):
  ```bash
  python -m ipykernel install --user --name=sentiment-env --display-name "Python (Sentiment Env)"
  ```
This command adds a new kernel with the display name `Python (Sentiment Env)` to Jupyter.

---

## How to Run the Project

### Step 1: Data Collection
1.  Navigate to the `notebooks` folder:
    ```bash
    cd notebooks
    ```
2.  Run the web scraping script to collect comments and save them in the `data` folder:
    ```bash
    python "Digikala Web Scraping.py"
    ```
    This process may take a few minutes.

### Step 2: Run the Analysis Notebook
1.  In the project's root directory (`SentimentProject/`), launch Jupyter Lab or Jupyter Notebook:
    ```bash
    jupyter lab
    # or
    # jupyter notebook
    ```
2.  In the Jupyter environment, navigate to the `notebooks` folder and open the `Sentiment Project Notebook.ipynb` file.
3.  From the notebook's top menu, change the kernel to `Python (Sentiment Env)` (or whatever name you chose in step 5).
4.  You can now run the notebook cells sequentially.

## Outputs
After a full run of the project, the following files will be generated:
- **`data/digikala_comments.csv`**: Raw data scraped from Digikala.
- **`data/ccleaned_digikala_comments.csv`**: The final dataset after cleaning and preprocessing.
- **Images in the `figures/` folder**: All charts, word clouds, and confusion matrices will be saved in this directory.