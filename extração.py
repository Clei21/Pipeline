import fitz  
import pytesseract
from PIL import Image
import base64
import io
import re
import os
import json


pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def to_base64(pix):
    try:
        return "data:image/png;base64," + base64.b64encode(pix.tobytes("png")).decode()
    except:
        return ""

def extract_metadata(text):
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    title = lines[0] if lines else ""
    doc_id, rev, date = "", "", ""

    m = re.search(r"[A-Z]{2,}-[A-Z0-9]{2,}-\d+-\d+", text)
    if m: doc_id = m.group(0)

    r = re.search(r"Rev(?:ision)?[: ]*([A-Za-z0-9]+)", text, re.I)
    if r: rev = r.group(1)

    d = re.search(r"\b\d{2}/\d{2}/\d{4}\b", text)
    if d: date = d.group(0)

    return title, doc_id, rev, date

def content_area(page):
    rect = page.rect
    h = rect.height

    return fitz.Rect(0, h * 0.09, rect.width, h * 0.91)

def ocultar_logo_posicao_fixa(page):
   
    try:
        h = page.rect.height
        posicao_x_inicio = 20 
        posicao_x_fim = 200
        posicao_y_topo = h - 75
        posicao_y_base = h - 5
        
        area_logo_fixa = fitz.Rect(posicao_x_inicio, posicao_y_topo, posicao_x_fim, posicao_y_base)
        
        page.add_redact_annot(area_logo_fixa, fill=(1, 1, 1)) 
        page.apply_redactions()
        
        shape = page.new_shape()
        shape.draw_rect(area_logo_fixa)
        shape.finish(fill=(1, 1, 1), color=(1, 1, 1), fill_opacity=1, stroke_opacity=0)
        shape.commit()
        
    except Exception as e:
        print(f"Aviso ao ocultar logo fixa: {e}")

def extract_page(page, num, meta, dpi=300):
    try:
       
        ocultar_logo_posicao_fixa(page)

      
        area = content_area(page)
        
        zoom = dpi / 72
        
      
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), clip=area, alpha=False)
        
        if pix.width > 100 and pix.height > 100:
            img = to_base64(pix)
            if img:
                return {
                    "imagem": img,
                    "metadata": {
                        "title": meta["title"],
                        "doc_id": meta["doc_id"],
                        "page": num,
                        "date": meta["date"],
                        "revision": meta["revision"]
                    }
                }
        return None
    except Exception as e:
        print(f"Erro página {num}: {e}")
        return None

def doc_metadata(doc, path):
    try:
        text = doc[0].get_text()
        title, doc_id, rev, date = extract_metadata(text)
        if not title:
            pix = doc[0].get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            ocr = pytesseract.image_to_string(img, lang="por+eng")
            title, doc_id, rev, date = extract_metadata(ocr)
        if not title: title = os.path.basename(path).replace(".pdf", "")
        return {"title": title, "doc_id": doc_id or "N/A", "revision": rev or "0", "date": date or "N/A"}
    except:
        return {"title": os.path.basename(path).replace(".pdf", ""), "doc_id": "N/A", "revision": "0", "date": "N/A"}

def process_pdf(pdf_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    try:
        doc = fitz.open(pdf_path)
    except:
        print("Erro ao abrir PDF")
        return

    try:
        meta = doc_metadata(doc, pdf_path)
        pages = []
        for i, page in enumerate(doc):
            p = extract_page(page, i + 1, meta)
            if p: pages.append(p)

        name = os.path.basename(pdf_path).replace(".pdf", "")
        out_path = os.path.join(output_dir, f"{name}.json")
        
        data = {
            "documento": {"title": meta["title"], "doc_id": meta["doc_id"], "revision": meta["revision"], "date": meta["date"], "total_paginas": len(doc)},
            "paginas_extraidas": len(pages),
            "paginas": pages
        }

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Salvo em: {out_path}")

    finally:
        doc.close()

if __name__ == "__main__":
    pdf_path = r"C:/Users/cleid/OneDrive/Documentos/BaseDados/Documentos/PCE-ENPP-3-948.pdf"
    output_dir = r"C:/Users/cleid/OneDrive/Documentos/BaseDados/json_saida"
    
    if os.path.exists(pdf_path):
        process_pdf(pdf_path, output_dir)