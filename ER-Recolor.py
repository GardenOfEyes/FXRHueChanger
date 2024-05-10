import xml.etree.ElementTree as ET
import os
import colorsys
import sys
import configparser


def set_hue(rgb, new_hue_fraction):
    r, g, b = [x / 255.0 for x in rgb]
    _, s, v = colorsys.rgb_to_hsv(r, g, b)
    r_new, g_new, b_new = colorsys.hsv_to_rgb(new_hue_fraction, s, v)
    return [int(x * 255) for x in (r_new, g_new, b_new)]


def set_value(element, value):
    if int(value) == value:
        element.set('Value', f"{int(value)}")
    else:
        element.set('Value', f"{value:.6f}")


def process_color_stops(fields, num_stops, new_hue_fraction):
    for i in range(1, 9, 4):
        rgba_values = [fields[i+j].get('Value') for j in range(4)]
        rgba = [float(value) for value in rgba_values]
        rgb = [int(rgba[j] * 255) for j in range(3)]
        rgb_set = set_hue(rgb, new_hue_fraction)
        for j in range(3):
            set_value(fields[i+j], rgb_set[j] / 255.0)

    skip_index = 9 + num_stops
    for i in range(skip_index, len(fields), 4):
        if i + 3 < len(fields):
            rgba_values = [fields[i+j].get('Value') for j in range(4)]
            rgba = [float(value) for value in rgba_values]
            rgb = [int(rgba[j] * 255) for j in range(3)]
            rgb_set = set_hue(rgb, new_hue_fraction)
            for j in range(3):
                set_value(fields[i+j], rgb_set[j] / 255.0)
        else:
            break


def process_constant_color_fields(fields, new_hue_fraction):
    rgba_values = [field.get('Value') for field in fields]
    rgba = [float(value) for value in rgba_values]
    rgb = [int(rgba[j] * 255) for j in range(3)]
    rgb_set = set_hue(rgb, new_hue_fraction)
    for j in range(3):
        set_value(fields[j], rgb_set[j] / 255.0)


def process_xml_file(file_path, new_hue_fraction):
    tree = ET.parse(file_path)
    root = tree.getroot()

    for property in root.findall(".//Property[@PropertyType='Color'][@InterpolationType='Linear'][@IsLoop='false']"):
        fields = property.find('Fields')
        if fields is not None:
            int_element = fields.find('Int')
            if int_element is not None:
                num_stops = int(int_element.get('Value'))
                process_color_stops(list(fields), num_stops, new_hue_fraction)

    for property in root.findall(".//Property[@PropertyType='Color'][@InterpolationType='Constant'][@IsLoop='false']"):
        fields = property.find('Fields')
        if fields is not None:
            process_constant_color_fields(list(fields), new_hue_fraction)

    tree.write(file_path)


def main():
    config = configparser.ConfigParser()
    config.read('config.ini')

    if 'Hue' in config['Settings']:
        new_hue_degrees = float(config['Settings']['Hue'])
    else:
        print("Hue value not found in config.ini.")
        sys.exit(1)

    new_hue_fraction = new_hue_degrees / 360.0

    for file_name in os.listdir('.'):
        if file_name.endswith('.xml'):
            process_xml_file(file_name, new_hue_fraction)


if __name__ == "__main__":
    main()
