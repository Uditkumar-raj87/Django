from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path('/workspaces/Django')

TARGETS = [
    (ROOT / 'courses' / 'models.py', ROOT / '01-models.png', ['class Question', 'class Choice', 'class Submission']),
    (ROOT / 'courses' / 'admin.py', ROOT / '02-admin-file.png', []),
    (ROOT / 'courses' / 'templates' / 'course_details_bootstrap.html', ROOT / '04-course-details.png', []),
    (ROOT / 'courses' / 'views.py', ROOT / '05-views.png', []),
    (ROOT / 'onlinecourse' / 'urls.py', ROOT / '06-urls.png', []),
]


def load_font(size):
    candidates = [
        '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',
        '/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf',
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def maybe_trim_text(text, must_include):
    if not must_include:
        return text

    lines = text.splitlines()
    indices = []
    for marker in must_include:
        for i, line in enumerate(lines):
            if marker in line:
                indices.append(i)
                break

    if not indices:
        return text

    start = max(min(indices) - 10, 0)
    end = min(max(indices) + 80, len(lines))
    return '\n'.join(lines[start:end])


def render_to_png(src_path, out_path, must_include):
    text = src_path.read_text(encoding='utf-8')
    text = maybe_trim_text(text, must_include)

    font = load_font(22)
    title_font = load_font(26)

    code_lines = text.splitlines() or ['']
    numbered = [f"{i+1:>4}  {line}" for i, line in enumerate(code_lines)]

    line_height = 34
    padding = 40
    title_height = 58
    width = 1800
    height = padding * 2 + title_height + max(1, len(numbered)) * line_height

    image = Image.new('RGB', (width, height), '#f5f7fb')
    draw = ImageDraw.Draw(image)

    draw.rectangle([0, 0, width, title_height + padding], fill='#111827')
    draw.text((padding, 18), f"{src_path.relative_to(ROOT)}", font=title_font, fill='#e5e7eb')

    y = padding + title_height
    for line in numbered:
        draw.text((padding, y), line, font=font, fill='#111827')
        y += line_height

    image.save(out_path)
    print(f"Created {out_path.name}")


if __name__ == '__main__':
    for src, out, must_include in TARGETS:
        render_to_png(src, out, must_include)
