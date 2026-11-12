import gzip
import urllib.request
import xml.etree.ElementTree as ET

# ==========================================
# यहाँ नीचे अपना 200 MB वाला EPG लिंक पेस्ट करें
# ==========================================
EPG_URL = "https://m3u-iptv.github.io/iptv/epg.xml.gz"

# इन सभी विदेशी हिंदी चैनलों के कीवर्ड्स को रखें
ALLOWED_INTL = [
    "&tv", "&amp;tv", "and tv", "andtv",
    "zee tv", "zee cinema", "sony kal", 
    "colors rishtey", "colors me", "colors apac", 
    "b4u movies", "b4u music"
]

def filter_epg(input_xml_path, output_gz_path):
    valid_channel_ids = set()
    new_root = ET.Element("tv")
    
    # बड़े XML को बिना RAM भरे लाइन-बाय-लाइन पढ़ें
    context = ET.iterparse(input_xml_path, events=("end",))
    
    for event, elem in context:
        if elem.tag == "channel":
            ch_id = elem.get("id", "").lower()
            disp_name = (elem.findtext("display-name") or "").lower()
            
            # India (.in, jiotv, tataplay) या हमारी 10 हिंदी चैनलों की लिस्ट चेक करें
            is_india = ".in" in ch_id or "jiotv" in ch_id or "tataplay" in ch_id
            is_allowed_hindi = any(name in disp_name or name in ch_id for name in ALLOWED_INTL)
            
            if is_india or is_allowed_hindi:
                valid_channel_ids.add(elem.get("id"))
                new_root.append(elem)
            else:
                elem.clear()
                
        elif elem.tag == "programme":
            if elem.get("channel") in valid_channel_ids:
                new_root.append(elem)
            else:
                elem.clear()

    # कंप्रेस करके .xml.gz में सेव करें
    tree = ET.ElementTree(new_root)
    with gzip.open(output_gz_path, "wb") as f:
        tree.write(f, encoding="utf-8", xml_declaration=True)

# 1. इंटरनेट से 200 MB फाइल डाउनलोड करें
print("EPG डाउनलोड हो रहा है...")
urllib.request.urlretrieve(EPG_URL, "raw_epg.xml")

# 2. उसे छोटा करके light_epg.xml.gz बनाएं
print("EPG फिल्टर हो रहा है...")
filter_epg("raw_epg.xml", "light_epg.xml.gz")
print("काम पूरा हो गया!")
