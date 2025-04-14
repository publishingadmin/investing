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

    try:
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')

        tabella = soup.find('table')
        if not tabella:
            return jsonify({"error": "Table not found"}), 404

        valori = {
            "EPS Diluiti ANN": "N/D",
            "EPS MRQ YoY": "N/D",
            "Vendite MRQ YoY": "N/D"
        }

        for row in tabella.find_all('tr'):
            celle = row.find_all('td')
            if len(celle) >= 2:
                nome = celle[0].text.strip()
                valore = celle[1].text.strip()

                if "Diluted EPS" in nome:
                    valori["EPS Diluiti ANN"] = valore
                elif "EPS(MRQ) vs Qtr. 1 Yr. AgoMRQ" in nome:
                    valori["EPS MRQ YoY"] = valore
                elif "Sales (MRQ) vs Qtr. 1 Yr. AgoMRQ" in nome:
                    valori["Vendite MRQ YoY"] = valore

        return jsonify(valori)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

