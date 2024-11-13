import streamlit as st
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import re

# Hard-coded sender email credentials
FROM_EMAIL = "my.projects.testt@gmail.com"
FROM_PASSWORD = "rtta abci arqp syhl"

def get_price(url):
    try:
        response = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Safari/605.1.15',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'DNT': '1',
            'Cache-Control': 'max-age=0'
        })
        soup = BeautifulSoup(response.content, 'html.parser')

        price_element = soup.select_one('.a-price-whole')  # For Amazon prices

        if price_element:
            price_text = price_element.text.strip()
            price_number = re.findall(r'[\d,]+', price_text)
            if price_number:
                price = float(price_number[0].replace(',', ''))
                return price
        return None
    except Exception as e:
        st.error(f"Error fetching price: {e}")
        return None

def send_email(subject, body, to_email):
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = FROM_EMAIL
        msg['To'] = to_email
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(FROM_EMAIL, FROM_PASSWORD)
        server.send_message(msg)
        server.quit()
        st.success("Email sent successfully!")
    except Exception as e:
        st.error(f"Error sending email: {e}")

def main():
    st.title("Amazon Price Tracker")
    st.markdown(
        "Track product prices on Amazon and receive email notifications when the price drops below your target price."
    )

    with st.form("price_tracker_form"):
        url = st.text_input("Amazon Product URL", placeholder="https://www.amazon.in/dp/product_id")
        target_price = st.number_input("Target Price (₹)", min_value=0, step=100, format="%.2f")
        to_email = st.text_input("Your Email Address")
        submit = st.form_submit_button("Start Tracking")

    if submit:
        if url and target_price > 0 and to_email:
            st.info("Fetching current price...")
            current_price = get_price(url)
            if current_price is not None:
                st.write(f"Current Price: ₹{current_price}")
                if current_price <= target_price:
                    st.success("Price is already below your target price!")
                    subject = "Product Price Dropped!"
                    body = f"The price dropped to ₹{current_price}!\nCheck the product here: {url}"
                    send_email(subject, body, to_email)
                else:
                    st.warning(
                        f"Current price ₹{current_price} is higher than your target price ₹{target_price}. Try again later."
                    )
            else:
                st.error("Could not retrieve the current price. Check the URL or try again later.")
        else:
            st.error("Please fill in all the fields correctly!")

if __name__ == "__main__":
    main()
