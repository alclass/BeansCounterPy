# -*- coding: utf-8 -*-
"""
Coleta de preços (faixa histórica) para NSNs/URLs e geração de CSV/JSON,
com logs detalhados e captura de fragmentos de tela via Selenium.

Autor: M365 Copilot
Data: 2026-01-07 (GMT-03)

Uso:
  python nsn_scraper.py --input urls.txt --outdir resultados --screenshot

Formato de 'urls.txt':
  Uma URL por linha (ex.: https://nationalstocknumber.info/national-stock-number/6150-01-514-6686)
  Você também pode misturar linhas com NSN simples (ex.: 6150-01-514-6686).
"""

import os
import re
import csv
import json
import time
import logging
import argparse
from datetime import datetime
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Opcional: Selenium + Pillow para screenshots
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from PIL import Image
except Exception:
    webdriver = None
    ChromeOptions = None
    Image = None


# -----------------------------
# Configuração de logging
# -----------------------------
def setup_logging(outdir: str) -> logging.Logger:
    logger = logging.getLogger("nsn_scraper")
    logger.setLevel(logging.DEBUG)

    # Console
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch_fmt = logging.Formatter("[%(levelname)s] %(message)s")
    ch.setFormatter(ch_fmt)

    # Arquivo
    os.makedirs(outdir, exist_ok=True)
    log_path = os.path.join(outdir, f"nsn_scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh_fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    fh.setFormatter(fh_fmt)

    logger.addHandler(ch)
    logger.addHandler(fh)
    return logger


# -----------------------------
# Sessão HTTP com retry/backoff
# -----------------------------
def retry_session(total=3, backoff_factor=0.5, status_forcelist=(429, 500, 502, 503, 504)):
    session = requests.Session()
    retry = Retry(
        total=total,
        read=total,
        connect=total,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=frozenset(["GET"]),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (compatible; Petrobras-OSD-PriceBot/1.0; +https://petrobras.com.br)"
    })
    return session


# -----------------------------
# Helpers de parsing
# -----------------------------
PRICE_PATTERNS = [
    # Padrões comuns de faixa: "Historical data shows pricing from $162.93 to $271.55"
    re.compile(r"pricing\s+from\s+\$?\s*([0-9.,]+)\s*(?:to|\-)\s*\$?\s*([0-9.,]+)", re.IGNORECASE),
    re.compile(r"price\s*range\s*[:\-]\s*\$?\s*([0-9.,]+)\s*(?:–|-|to)\s*\$?\s*([0-9.,]+)", re.IGNORECASE),
]

def parse_price_range(soup: BeautifulSoup) -> str | None:
    """
    Tenta recuperar a faixa de preço exibida em texto livre.
    Retorna uma string, por ex: 'Price Range: $162.93 – $271.55'
    """
    # 1) Busca por textos chave
    possible_texts = soup.find_all(string=lambda t: isinstance(t, str) and ("price" in t.lower() or "pricing" in t.lower()))
    for txt in possible_texts:
        t = " ".join(txt.strip().split())
        # Tenta casar padrão de faixa
        for rx in PRICE_PATTERNS:
            m = rx.search(t)
            if m:
                low, high = m.group(1), m.group(2)
                return f"Price Range: ${low} – ${high}"
    # 2) Fallback: vasculha parágrafos
    for p in soup.find_all(["p", "li", "div"]):
        content = p.get_text(" ", strip=True)
        for rx in PRICE_PATTERNS:
            m = rx.search(content)
            if m:
                low, high = m.group(1), m.group(2)
                return f"Price Range: ${low} – ${high}"
    return None


def parse_history_table(soup: BeautifulSoup) -> list[dict]:
    """
    Tenta recuperar uma tabela de histórico (datas e fonte/preço).
    Retorna lista de dicts: [{'date': ..., 'source': ..., 'price': ...}]
    """
    history = []
    tables = soup.find_all("table")
    for tb in tables:
        headers = [th.get_text(strip=True).lower() for th in tb.find_all("th")]
        rows = tb.find_all("tr")
        # Heurística: se há cabeçalho com "date" ou "historical", considerar
        if any("date" in h or "history" in h for h in headers) or len(headers) == 0:
            for row in rows[1:]:
                cols = [c.get_text(strip=True) for c in row.find_all(["td", "th"])]
                if len(cols) >= 2:
                    date = cols[0]
                    val = cols[1]
                    # Tenta separar 'source' e 'price' se houver padrão monetário
                    price_match = re.search(r"\$?\s*([0-9.,]+)", val)
                    price_value = price_match.group(1) if price_match else None
                    history.append({
                        "date": date,
                        "source_or_desc": val,
                        "price": price_value
                    })
    return history


def normalize_id_from_url(url: str) -> str:
    """
    Extrai um ID amigável (NSN ou último segmento da URL) para nomear arquivos.
    """
    # Se for NSN simples
    if re.match(r"^\d{4}-\d{2}-\d{3}-\d{4}$", url) or re.match(r"^\d{4}-\d{2}-\d{6}$", url):
        return url.replace("-", "")
    # Se for URL
    path = urlparse(url).path.strip("/")
    return path.split("/")[-1] or "item"


def build_target_url(item: str) -> str:
    """
    Aceita NSN ou URL. Se for NSN, monta a URL padrão do domínio 'nationalstocknumber.info'.
    """
    if item.startswith("http://") or item.startswith("https://"):
        return item
    # Monta a URL do info (alvo principal com preço impresso)
    # Ex.: https://nationalstocknumber.info/national-stock-number/6150-01-514-6686
    return f"https://nationalstocknumber.info/national-stock-number/{item}"


# -----------------------------
# Salvamento CSV/JSON
# -----------------------------
def save_outputs(outdir: str, item_id: str, price_range: str | None, history: list[dict], html: str):
    os.makedirs(outdir, exist_ok=True)

    # JSON
    payload = {
        "item_id": item_id,
        "price_range": price_range,
        "historical_data": history,
        "extraction_timestamp": datetime.now().isoformat(),
        "source_domain": "nationalstocknumber.info"
    }
    json_path = os.path.join(outdir, f"{item_id}_price.json")
    with open(json_path, "w", encoding="utf-8") as jf:
        json.dump(payload, jf, indent=2, ensure_ascii=False)

    # CSV
    csv_path = os.path.join(outdir, f"{item_id}_price.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as cf:
        w = csv.writer(cf)
        w.writerow(["Item ID", item_id])
        w.writerow(["Price Range", price_range or ""])
        w.writerow([])
        w.writerow(["Date", "Source/Desc", "Price"])
        for row in history:
            w.writerow([row.get("date", ""), row.get("source_or_desc", ""), row.get("price", "")])

    # HTML bruto (opcional, útil para auditoria)
    html_path = os.path.join(outdir, f"{item_id}.html")
    with open(html_path, "w", encoding="utf-8") as hf:
        hf.write(html)

    return json_path, csv_path, html_path


# -----------------------------
# Screenshot da área de preço
# -----------------------------
def screenshot_price_fragment(url: str, outdir: str, item_id: str, logger: logging.Logger) -> str | None:
    if webdriver is None or ChromeOptions is None or Image is None:
        logger.warning("Selenium/Pillow não disponíveis. Pulei a captura de tela.")
        return None

    # Configura Chrome headless
    options = ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,2000")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 15)

    try:
        driver.get(url)
        # Espera que algum texto com 'price range' ou 'pricing' apareça
        # Heurística: busca elementos que contenham 'pricing' ou '$'
        candidate = None
        # 1) Tenta localizar por texto 'Price Range'
        try:
            candidate = wait.until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(translate(text(),'PRICE','price'),'price') or contains(translate(text(),'PRICING','pricing'),'pricing') or contains(text(),'$')]"))
            )
        except Exception:
            pass

        # 2) Fallback: tenta uma seção de Q&A que cite 'Historical data shows'
        if candidate is None:
            try:
                candidate = wait.until(
                    EC.presence_of_element_located((By.XPATH, "//*[contains(translate(text(),'HISTORICAL','historical'),'historical') and contains(translate(text(),'PRICING','pricing'),'pricing')]"))
                )
            except Exception:
                logger.info("Não encontrei elemento textual óbvio; farei screenshot da seção principal.")

        # Faz screenshot (elemento, se disponível; senão, página inteira)
        out_png = os.path.join(outdir, f"{item_id}_price.png")
        os.makedirs(outdir, exist_ok=True)

        if candidate:
            candidate.screenshot(out_png)
        else:
            driver.save_screenshot(out_png)

        # Opcional: recorte adicional com Pillow, se página inteira
        if candidate is None and Image is not None:
            # Heurística: recorta parte superior (onde geralmente fica o conteúdo principal)
            img = Image.open(out_png)
            w, h = img.size
            crop_box = (0, 0, w, min(h, 900))  # recorte até ~900px de altura
            img_crop = img.crop(crop_box)
            img_crop.save(out_png)

        logger.info(f"Screenshot salvo: {out_png}")
        return out_png

    except Exception as e:
        logger.error(f"Falha ao capturar screenshot: {e}")
        return None
    finally:
        driver.quit()


# -----------------------------
# Pipeline principal
# -----------------------------
def process_item(session: requests.Session, item: str, outdir: str, logger: logging.Logger, do_screenshot=False):
    url = build_target_url(item)
    item_id = normalize_id_from_url(item)

    logger.info(f"Processando: {item} -> {url}")

    try:
        resp = session.get(url, timeout=20)
        resp.raise_for_status()
        html = resp.text
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro HTTP ao acessar {url}: {e}")
        return None

    soup = BeautifulSoup(html, "html.parser")

    price_range = parse_price_range(soup)
    if price_range:
        logger.info(f"Faixa encontrada: {price_range}")
    else:
        logger.warning("Faixa de preço não encontrada no HTML.")

    history = parse_history_table(soup)
    logger.info(f"Entradas históricas identificadas: {len(history)}")

    json_path, csv_path, html_path = save_outputs(outdir, item_id, price_range, history, html)
    logger.info(f"Arquivos salvos: {json_path}, {csv_path}, {html_path}")

    if do_screenshot:
        screenshot_price_fragment(url, outdir, item_id, logger)

    # Retorno para uso programático
    return {
        "item": item,
        "url": url,
        "item_id": item_id,
        "price_range": price_range,
        "history_count": len(history),
        "json_path": json_path,
        "csv_path": csv_path,
        "html_path": html_path
    }


def read_input_list(path: str) -> list[str]:
    items = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            items.append(s)
    return items


def main():
    parser = argparse.ArgumentParser(description="Coleta de faixa de preço e histórico para NSNs/URLs.")
    parser.add_argument("--input", required=True, help="Arquivo texto com uma URL ou NSN por linha.")
    parser.add_argument("--outdir", default="resultados", help="Diretório de saída.")
    parser.add_argument("--screenshot", action="store_true", help="Capturar fragmento de tela da área de preço (Selenium).")
    parser.add_argument("--delay", type=float, default=1.5, help="Delay (segundos) entre itens para reduzir carga no site.")
    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    logger = setup_logging(args.outdir)
    session = retry_session(total=5, backoff_factor=0.8)

    items = read_input_list(args.input)
    logger.info(f"Itens carregados: {len(items)}")

    results = []
    for item in items:
        r = process_item(session, item, args.outdir, logger, do_screenshot=args.screenshot)
        if r:
            results.append(r)
        time.sleep(args.delay)

    # Resumo em um JSON agregador
    summary_path = os.path.join(args.outdir, "summary.json")
    with open(summary_path, "w", encoding="utf-8") as sf:
        json.dump({"generated_at": datetime.now().isoformat(), "results": results}, sf, indent=2, ensure_ascii=False)

    logger.info(f"Pipeline concluído. Resumo: {summary_path}")


if __name__ == "__main__":
    main()
