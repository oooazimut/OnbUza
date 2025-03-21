import asyncio
from collections.abc import Iterable

from PIL import Image, ImageDraw, ImageFont

from config import settings


class ImageService:
    _font_cache = {}
    _image_cache = {}

    @staticmethod
    def _get_font(
        font_path: str = "fonts/Ubuntu-R.ttf", font_size: int = 28
    ) -> ImageFont.FreeTypeFont:
        key = (font_path, font_size)
        if key not in ImageService._font_cache:
            ImageService._font_cache[key] = ImageFont.truetype(
                font_path, size=font_size, encoding="UTF-8"
            )
        return ImageService._font_cache[key]

    @staticmethod
    async def paste_row(
        bg: Image.Image,
        values: Iterable,
        name: str,
        ordinata: int,
        abcissa: int = 30,
        size: int = 150,
        step: int = 200,
    ):
        draw = ImageDraw.Draw(bg)
        font = ImageService._get_font(font_size=38)
        path = f"images/templates/{name}"

        image_cache = ImageService._image_cache.setdefault(name, {})

        for position, val in enumerate(values, start=1):
            if val not in image_cache:
                element_path = f"{path}{str(val)}.png"
                element = Image.open(element_path).resize((size, size)).convert("RGBA")
                image_cache[val] = element
            element = image_cache[val]

            bg.paste(element, (abcissa, ordinata), element)
            draw.text(
                (abcissa + 60, ordinata + 60),
                f"УЗА-{str(position)}",
                fill="black",
                font=font,
            )
            abcissa += step

        bg.save(settings.common_img, optimize=True)

    @staticmethod
    async def print_text(
        img: Image.Image,
        text_list: list[str | int],
        point: tuple[float, float],
        step: int = 200,
        fontsize=33,
    ):
        draw = ImageDraw.Draw(img)
        font = ImageService._get_font("fonts/Ubuntu-R.ttf", font_size=fontsize)
        for item in text_list:
            draw.text(point, str(item), fill="black", font=font)
            point = (point[0] + step, point[1])

        img.save(settings.common_img, optimize=True)


async def common_info(data):
    bg_img = Image.new("RGBA", (1000, 1400), (255, 255, 255))
    await asyncio.gather(
        ImageService.paste_row(bg_img, data["uzas"], "uza", 50),
        ImageService.print_text(bg_img, data["selectors"], (50, 200)),
        ImageService.print_text(bg_img, data["temperatures"], (50, 300)),
        ImageService.print_text(bg_img, data["pumpworks"], (50, 400)),
        ImageService.print_text(bg_img, data["pressures"], (50, 500)),
    )
