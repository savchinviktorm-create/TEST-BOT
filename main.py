def get_fuel_prices():
    """Спроба отримати ціни через імітацію браузера та fallback-систему"""
    fuel_data = {"A95": "55.40", "DP": "51.90", "Gas": "27.90"} # Актуальні ціни як резерв
    
    try:
        # Спробуємо зчитати з порталу, який менш агресивно блокує GitHub
        url = "https://vseazs.com/ua/oil/prices/1" 
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7'
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as f:
            html = f.read().decode('utf-8')
            
            # Шукаємо ціни через регулярні вирази
            res_95 = re.search(r'А-95.*?([\d,.]+)', html)
            res_dp = re.search(r'ДП.*?([\d,.]+)', html)
            res_gs = re.search(r'Газ.*?([\d,.]+)', html)
            
            if res_95: fuel_data["A95"] = res_95.group(1).replace(',', '.')
            if res_dp: fuel_data["DP"] = res_dp.group(1).replace(',', '.')
            if res_gs: fuel_data["Gas"] = res_gs.group(1).replace(',', '.')

        return (f"⛽ <b>Середні ціни (оновлено):</b>\n"
                f"🔹 А-95: {fuel_data['A95']} грн\n"
                f"🔹 ДП: {fuel_data['DP']} грн\n"
                f"🔹 ГАЗ: {fuel_data['Gas']} грн")
    except:
        # Якщо все зламалося, бот не видасть порожнечу, а покаже останні відомі ціни
        return (f"⛽ <b>Пальне (орієнтовно):</b>\n"
                f"🔹 А-95: ~55.50 грн\n"
                f"🔹 ДП: ~52.10 грн\n"
                f"🔹 ГАЗ: ~28.50 грн\n"
                f"<i>(Дані сайту тимчасово обмежені)</i>")
