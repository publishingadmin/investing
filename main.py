from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# 🔐 La tua API Key di ScraperAPI
api_key = "38d5cb26de37e1c35bb61c8d50406aaa"

@app.route('/dati', methods=['GET'])
def estrai_dati():
    slug = request.args.get('slug')
    if not slug:
        return jsonify({"error": "Missing slug"}), 400

    # 🌐 URL finale tramite ScraperAPI
    target_url = f"https://it.investing.com/equities/{slug}-ratios"
    url = f"http://api.scraperapi.com/?api_key={api_key}&url={target_url}&country_code=it"

    try:
        res = requests.get(url, timeout=20)
        soup = BeautifulSoup(res.text, 'html.parser')

        print("DEBUG HTML INIZIO ========")
        print(soup.prettify())
        print("DEBUG HTML FINE =========")

        tabella = soup.find('table')

        if not tabella:
            return jsonify({"error": "Table not found"}), 404

        valori = {
            "Diluted EPS": "N/D",
            "EPS YoY MRQ": "N/D",
            "Sales YoY MRQ": "N/D"
        }

        for row in tabella.find_all('tr'):
            celle = row.find_all('td')
            if len(celle) >= 2:
                nome = celle[0].text.strip()
                valore = celle[1].text.strip()

                if "Diluted EPS" in nome:
                    valori["Diluted EPS"] = valore
                elif "EPS(MRQ)" in nome:
                    valori["EPS YoY MRQ"] = valore
                elif "Sales (MRQ)" in nome:
                    valori["Sales YoY MRQ"] = valore

        return jsonify(valori)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ Necessario per il corretto deploy su Render
if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
