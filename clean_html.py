#!/usr/bin/env python3
"""Clean HTML file by removing base64 embedded content."""

import re

def clean_html(input_path: str, output_path: str) -> dict:
    """Remove base64 embedded images and fonts from HTML file.

    Returns dict with statistics about what was removed.
    """
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_size = len(content)
    stats = {
        'original_size': original_size,
        'data_images_removed': 0,
        'font_faces_removed': 0,
    }

    # Remove data:image/* URLs (base64 encoded images)
    content, count = re.subn(
        r'url\(["\']?data:image/[^)]+\)["\']?\)',
        'url("")',
        content
    )
    stats['data_images_removed'] += count

    # Remove data:application/octet-stream (typically fonts)
    content, count = re.subn(
        r'url\(["\']?data:application/[^)]+\)["\']?\)',
        'url("")',
        content
    )
    stats['data_images_removed'] += count

    # Remove entire @font-face blocks with embedded data
    content, count = re.subn(
        r'@font-face\s*\{[^}]*src:\s*url\(["\']?\)[^}]*\}',
        '',
        content
    )
    stats['font_faces_removed'] += count

    # Remove inline base64 src attributes in img tags
    content, count = re.subn(
        r'src="data:[^"]*"',
        'src=""',
        content
    )
    stats['data_images_removed'] += count

    stats['final_size'] = len(content)
    stats['reduction_percent'] = round((1 - len(content) / original_size) * 100, 1)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return stats


if __name__ == '__main__':
    input_file = '/Users/adamradvan/histali/source/pdf24.html'
    output_file = '/Users/adamradvan/histali/pdf24_clean.html'

    stats = clean_html(input_file, output_file)

    print(f"Original size: {stats['original_size']:,} bytes")
    print(f"Final size: {stats['final_size']:,} bytes")
    print(f"Reduction: {stats['reduction_percent']}%")
    print(f"Data URLs removed: {stats['data_images_removed']}")
    print(f"Font-face blocks removed: {stats['font_faces_removed']}")
