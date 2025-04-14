from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

headers = {
    'User-Agent': 'Mozilla/5.0'
}

@app.route('/dati', methods=['GET'])
def estrai_dati():
    slug = request.args.get('slug')
    if not slug:
        return jsonify({"error": "Missing slug"}), 400

    url = f"https://it.investing.com/equities/{slug}-ratios"
    api_key = "38d5cb26de37e1c35bb61c8d50406aaa"
    proxy_url = f"http://api.scraperapi.com?api_key={api_key}&url={url}"

    try:
        res = requests.get(proxy_url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')

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
                elif "EPS (MRQ) vs" in nome:
                    valori["EPS YoY MRQ"] = valore
                elif "Sales (MRQ) vs" in nome:
                    valori["Sales YoY MRQ"] = valore

        return jsonify(valori)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


