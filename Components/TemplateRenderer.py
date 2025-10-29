import io
import math
import requests
from PIL import Image, ImageDraw, ImageFont, ImageShow
import colorsys


class TemplateRenderer:
    def __init__(self, tiers: list[str], show_preview: bool = False):
        self.tiers = tiers
        self.items = []
        self.show_preview = show_preview
        self._icon_cache = {}

    def _load_icon(self, url: str, size: int) -> Image.Image:
        if url in self._icon_cache:
            return self._icon_cache[url]

        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            icon = Image.open(io.BytesIO(response.content)).convert("RGBA")
            icon = icon.resize((size, size), Image.Resampling.LANCZOS)
            self._icon_cache[url] = icon
            # ImageShow.show(icon)
            return icon
        except Exception:
            img = Image.new("RGBA", (size, size))
            self._icon_cache[url] = img
            # ImageShow.show(img)
            return img
    
    def add_item(self, url: str, tier: str):
        self.items.append([url, tier])

    def create_colors(self):
        n = len(self.tiers)
        colors = {}
        for i in range(n):
            hue = i/n
            lightness = 0.4
            saturation = 0.9
            
            colors[self.tiers[i]] = tuple(int(c * 255) for c in colorsys.hls_to_rgb(hue, lightness, saturation))
        return colors
                
    def render(self):
        tier_colors = self.create_colors()
        # print(tier_colors)

        font_size = 24
        item_size = 80
        label_width = 80
        items_per_row = 10  # how many icons per row before wrapping
        
        font = ImageFont.truetype("arial.ttf", font_size)

        # compute tier heights
        row_heights = []
        for tier in self.tiers:
            count = sum(1 for utier in self.items if utier[1] == tier)
            rows_needed = max(1, math.ceil(count / items_per_row))
            row_heights.append(rows_needed * item_size)

        total_height = sum(row_heights)
        total_width = label_width + items_per_row * item_size

        img = Image.new("RGBA", (total_width, total_height))
        draw = ImageDraw.Draw(img)

        y_offset = 0
        for i, tier in enumerate(self.tiers):
            color = tier_colors.get(tier, (128, 128, 128))
            tier_height = row_heights[i]

            # draw background and label section
            draw.rectangle([0, y_offset, total_width, y_offset + tier_height], fill=(25, 25, 25))
            draw.rectangle([0, y_offset, label_width, y_offset + tier_height], fill=color)

            # draw label centered
            bbox = draw.textbbox((0, 0), tier, font=font)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            draw.text(
                ((label_width - tw) / 2, (y_offset + (tier_height - th) / 2)-font_size/8),
                tier,
                fill="white",
                font=font,
            )

            # draw tier items tightly packed
            urls = [url for url, utier in self.items if utier == tier]
            for idx, url in enumerate(urls):
                row = idx // items_per_row
                col = idx % items_per_row
                x = label_width + col * item_size + 1
                y = y_offset + row * item_size
                icon = self._load_icon(url, item_size)
                img.paste(icon, (x, y))

            y_offset += tier_height

        # return PNG bytes
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)

        if self.show_preview:
            ImageShow.show(img)

        return buf


if __name__ == "__main__":
    renderer = TemplateRenderer(
        tiers=["SS", "S", "A", "B", "Maid", "No life"],
        show_preview=True
    )
    
    renderer.items=[
            ["https://cdn.discordapp.com/avatars/1126495387683926036/ae020f5b5b3f8c695e88c15abade5689.png?format=webp&quality=lossless&width=282&height=282", "Maid"],
            ["https://cdn.discordapp.com/avatars/1126495387683926036/ae020f5b5b3f8c695e88c15abade5689.png?format=webp&quality=lossless&width=282&height=282", "Maid"],
            ["https://cdn.discordapp.com/avatars/1126495387683926036/ae020f5b5b3f8c695e88c15abade5689.png?format=webp&quality=lossless&width=282&height=282", "Maid"],
            ["https://cdn.discordapp.com/avatars/1126495387683926036/ae020f5b5b3f8c695e88c15abade5689.png?format=webp&quality=lossless&width=282&height=282", "Maid"],
            ["https://cdn.discordapp.com/avatars/1126495387683926036/ae020f5b5b3f8c695e88c15abade5689.png?format=webp&quality=lossless&width=282&height=282", "Maid"],
            ["https://cdn.discordapp.com/avatars/1126495387683926036/ae020f5b5b3f8c695e88c15abade5689.png?format=webp&quality=lossless&width=282&height=282", "Maid"],
            ["https://cdn.discordapp.com/avatars/1126495387683926036/ae020f5b5b3f8c695e88c15abade5689.png?format=webp&quality=lossless&width=282&height=282", "Maid"],
            ["https://cdn.discordapp.com/avatars/1126495387683926036/ae020f5b5b3f8c695e88c15abade5689.png?format=webp&quality=lossless&width=282&height=282", "Maid"],
            ["https://cdn.discordapp.com/avatars/1126495387683926036/ae020f5b5b3f8c695e88c15abade5689.png?format=webp&quality=lossless&width=282&height=282", "Maid"],
            ["https://cdn.discordapp.com/avatars/1126495387683926036/ae020f5b5b3f8c695e88c15abade5689.png?format=webp&quality=lossless&width=282&height=282", "Maid"],
            ["https://cdn.discordapp.com/avatars/1126495387683926036/ae020f5b5b3f8c695e88c15abade5689.png?format=webp&quality=lossless&width=282&height=282", "Maid"],
            ["https://cdn.discordapp.com/avatars/1126495387683926036/ae020f5b5b3f8c695e88c15abade5689.png?format=webp&quality=lossless&width=282&height=282", "Maid"],
            ["https://cdn.discordapp.com/avatars/334528593323622402/d556ed8ba7449dd672105d63799827f9.png", "S"],
            ["https://cdn.discordapp.com/avatars/334528593323622402/d556ed8ba7449dd672105d63799827f9.png", "S"],
            ["https://cdn.discordapp.com/avatars/334528593323622402/d556ed8ba7449dd672105d63799827f9.png", "S"],
            ["https://cdn.discordapp.com/avatars/334528593323622402/d556ed8ba7449dd672105d63799827f9.png", "S"],
            ["https://cdn.discordapp.com/avatars/334528593323622402/d556ed8ba7449dd672105d63799827f9.png", "S"],
            ["https://cdn.discordapp.com/avatars/334528593323622402/d556ed8ba7449dd672105d63799827f9.png", "S"],
            ["https://cdn.discordapp.com/avatars/334528593323622402/d556ed8ba7449dd672105d63799827f9.png", "S"],
            ["https://cdn.discordapp.com/avatars/334528593323622402/d556ed8ba7449dd672105d63799827f9.png", "S"],
            ["https://cdn.discordapp.com/avatars/334528593323622402/d556ed8ba7449dd672105d63799827f9.png", "S"],
            ["https://cdn.discordapp.com/avatars/334528593323622402/d556ed8ba7449dd672105d63799827f9.png", "S"],
            ["https://cdn.discordapp.com/avatars/334528593323622402/d556ed8ba7449dd672105d63799827f9.png", "S"],
            ["https://cdn.discordapp.com/avatars/334528593323622402/d556ed8ba7449dd672105d63799827f9.png", "S"],
            ["https://cdn.discordapp.com/avatars/334528593323622402/d556ed8ba7449dd672105d63799827f9.png", "S"]
        ]
    renderer.render()
    # print(colorsys.hls_to_rgb(0.33, 0.5, 1))
