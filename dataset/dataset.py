import os
import argparse
import xml.etree.ElementTree as ET
import csv


def parse_kanjivg(kvg_path):
    """
    Parse the KANJIVG XML and extract SVG path data for each kanji.
    Returns a dict: {character: svg_content_string}
    """
    tree = ET.parse(kvg_path)
    root = tree.getroot()
    data = {}
    # KANJIVG uses <kanji id="kvg:kanji_xxxxx"><g>...<path d="..."/></g></kanji>
    for kanji in root.findall('.//kanji'):
        kanji_id = kanji.attrib.get('id', '')
        hex_code = kanji_id.split('_')[-1]
        try:
            char = chr(int(hex_code, 16))
        except ValueError:
            continue
        paths = kanji.findall('.//path')
        if not paths:
            continue
        # build SVG with no fill and black strokes for clear line art
        svg_content = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 109 109" '
            'stroke="black" fill="none" stroke-width="3">'
        )
        for p in paths:
            d = p.attrib.get('d')
            svg_content += f'<path d="{d}" />'
        svg_content += '</svg>'
        data[char] = svg_content
    return data


def parse_kanjidic(kdic_path):
    """
    Parse the KANJIDIC2 XML and extract English meanings for each kanji.
    Returns a dict: {character: prompt_string}
    """
    tree = ET.parse(kdic_path)
    root = tree.getroot()
    meanings = {}
    for entry in root.findall('.//character'):
        literal = entry.findtext('literal')
        if not literal:
            continue
        m_elems = entry.findall('.//meaning')
        eng = [m.text for m in m_elems if m.text and (m.attrib.get('m_lang') in (None, '', 'en'))]
        if not eng:
            continue
        prompt = ', '.join(sorted(set(eng)))
        meanings[literal] = prompt
    return meanings


def write_dataset(kvg_data, kd_data, out_dir):
    """
    For each character in both datasets, write an SVG file and record the prompt.
    Also prints total count.
    """
    os.makedirs(out_dir, exist_ok=True)
    images_dir = os.path.join(out_dir, 'svgs')
    os.makedirs(images_dir, exist_ok=True)
    mapping_file = os.path.join(out_dir, 'prompts.csv')

    count = 0
    with open(mapping_file, 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['character', 'prompt', 'svg_path'])
        for char, svg in kvg_data.items():
            prompt = kd_data.get(char)
            if not prompt:
                continue
            svg_filename = f"{ord(char):x}.svg"
            svg_path = os.path.join(images_dir, svg_filename)
            with open(svg_path, 'w', encoding='utf-8') as f:
                f.write(svg)
            writer.writerow([char, prompt, svg_path])
            count += 1

    print(f"Total paired entries (images + prompts): {count}")
    print(f"SVG files located in: {images_dir}")
    print(f"Prompt CSV generated at: {mapping_file}")


def main():
    # Args
    parser = argparse.ArgumentParser(description="Extract KANJIVG SVGs and KANJIDIC prompts")
    parser.add_argument('--kvg', required=True, help='Path to kanjivg XML file')
    parser.add_argument('--dic', required=True, help='Path to kanjidic2 XML file')
    parser.add_argument('--out', default='kanji_dataset', help='Output directory')
    args = parser.parse_args()

    # kanjivg.xml Parser
    print("Parsing KANJIVG...")
    kvg_data = parse_kanjivg(args.kvg)
    print(f"Found {len(kvg_data)} SVG entries in KANJIVG.")

    # kanjidic2.xml Parser
    print("Parsing KANJIDIC2...")
    kd_data = parse_kanjidic(args.dic)
    print(f"Found {len(kd_data)} English meanings in KANJIDIC2.")

    write_dataset(kvg_data, kd_data, args.out)

if __name__ == '__main__':
    main()