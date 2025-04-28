from flask import Flask, request as flask_request, render_template
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Flask App
app = Flask(__name__)

# Category mapping to Excel files
CATEGORIES = {
    "headphones": r"E:\DHP\Group_Project\Final_Fold_Group\Cleaned_H.xlsx",
    "phones": r"E:\DHP\Group_Project\Final_Fold_Group\Cleaned_P.xlsx",
    "laptops": r"E:\DHP\Group_Project\Final_Fold_Group\Cleaned_L.xlsx",
    "books": r"E:\DHP\Group_Project\Final_Fold_Group\Cleaned_B.xlsx"
}

BUYHATKE_URL = "https://buyhatke.com/"

def parse_price(price):
    try:
        return float(str(price).replace(",", "").strip())
    except:
        return float('inf')

def parse_rating(rating):
    try:
        return float(str(rating).strip())
    except:
        return 0.0

@app.route("/", methods=["GET"])
def homepage():
    return render_template("index.html", categories=CATEGORIES)

@app.route("/select-product", methods=["GET"])
def select_product():
    category = flask_request.args.get("category", "").lower()

    if category not in CATEGORIES:
        return render_template("error.html", message="Invalid category selected.", back_url="/")

    try:
        df = pd.read_excel(CATEGORIES[category])
    except Exception as e:
        return render_template("error.html", message=f"Failed to load data for {category}. Error: {str(e)}", back_url="/")

    products = df["Name"].dropna().tolist()
    return render_template("select_product.html", category=category, products=products)

@app.route("/compare", methods=["GET"])
def compare_product():
    category = flask_request.args.get("category", "").lower()
    product_name = flask_request.args.get("product", "")
    include_buyhatke = flask_request.args.get("include_buyhatke", "") == "yes"

    if category not in CATEGORIES:
        return render_template("error.html", message="Invalid category selected.", back_url="/")

    try:
        df = pd.read_excel(CATEGORIES[category])
    except Exception as e:
        return render_template("error.html", message=f"Failed to load data for {category}. Error: {str(e)}", back_url="/")

    if product_name not in df["Name"].values:
        return render_template("error.html", message=f"Product '{product_name}' not found.", back_url=f"/select-product?category={category}")

    product = df[df["Name"] == product_name].iloc[0]

    amazon_price = parse_price(product.get("Price in Amazon"))
    flipkart_price = parse_price(product.get("Price in Flipkart"))
    amazon_rating = parse_rating(product.get("Rating in Amazon"))
    flipkart_rating = parse_rating(product.get("Rating in Flipkart"))
    amazon_url = product.get("URL in Amazon", "")
    flipkart_url = product.get("URL in Flipkart", "")

    better_price = (
        "Amazon" if amazon_price < flipkart_price else
        "Flipkart" if flipkart_price < amazon_price else
        "Both (Same Price)"
    )
    better_rating = (
        "Amazon" if amazon_rating > flipkart_rating else
        "Flipkart" if flipkart_rating > amazon_rating else
        "Both (Same Rating)"
    )

    buyhatke_search_url = ""
    if include_buyhatke:
        product_url = amazon_url or flipkart_url
        if product_url:
            encoded_url = product_url.replace("&", "%26")
            buyhatke_search_url = f"{BUYHATKE_URL}?q={encoded_url}"

    return render_template("compare.html",
                           product_name=product_name,
                           amazon_price=amazon_price,
                           flipkart_price=flipkart_price,
                           amazon_rating=amazon_rating,
                           flipkart_rating=flipkart_rating,
                           better_price=better_price,
                           better_rating=better_rating,
                           amazon_url=amazon_url,
                           flipkart_url=flipkart_url,
                           buyhatke_search_url=buyhatke_search_url)

if __name__ == "__main__":
    app.run(debug=True)
