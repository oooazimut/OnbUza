import asyncio
from collections.abc import Iterable, Sequence

from config import settings
from db.models import Gas_Sensor, Pump
from matplotlib import cm
from matplotlib import dates as mdates
from matplotlib import pyplot as plt
from PIL import Image, ImageDraw, ImageFont
from service.modbus import SELECTORS


class ImageService:
    _font_cache = {}
    _image_cache = {}

    @staticmethod
    def _get_font(
        font_path: str = "fonts/Ubuntu-R.ttf", font_size: int = 44
    ) -> ImageFont.FreeTypeFont:
        key = (font_path, font_size)
        if key not in ImageService._font_cache:
            ImageService._font_cache[key] = ImageFont.truetype(
                font_path, size=font_size, encoding="UTF-8"
            )
        return ImageService._font_cache[key]

    @staticmethod
    async def paste_icon(
        bg: Image.Image,
        name: str,
        point: list[int],
        size: tuple = (60, 60),
        step: int = 200,
    ):
        element_path = f"images/templates/{name}"
        element = Image.open(element_path).resize(size).convert("RGBA")
        for _ in range(5):
            bg.paste(element, tuple(point), element)
            point[0] += step
        bg.save(settings.common_img, optimize=True)

    @staticmethod
    async def paste_uza(
        bg: Image.Image,
        values: Iterable,
        name: str,
        ordinata: int,
        abcissa: int = 30,
        size: int = 150,
        step: int = 200,
    ):
        draw = ImageDraw.Draw(bg)
        font = ImageService._get_font(font_size=44)
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
                (abcissa + 60, ordinata + 80),
                f"УЗА-{str(position)}",
                fill="black",
                font=font,
            )
            abcissa += step

        bg.save(settings.common_img, optimize=True)

    @staticmethod
    async def print_text(
        img: Image.Image,
        text_list: list[str],
        point: tuple[float, float],
        step: int = 200,
        fontsize=44,
    ):
        draw = ImageDraw.Draw(img)
        font = ImageService._get_font("fonts/Ubuntu-R.ttf", font_size=fontsize)
        for item in text_list:
            draw.text(point, str(item), fill="black", font=font)
            point = (point[0] + step, point[1])

        img.save(settings.common_img, optimize=True)


async def common_info(data):
    bg_img = Image.new("RGBA", (1000, 800), (255, 255, 255))
    # draw = ImageDraw.Draw(bg_img)
    # font = ImageService._get_font()
    # draw.text((30, 400), "температура:", fill="black", font=font)
    # draw.text((30, 540), "наработка:", fill="black", font=font)
    # draw.text((3, 680), "давление:", fill="black", font=font)
    await asyncio.gather(
        ImageService.paste_uza(
            bg_img, data["uzas"], "uza", 10, abcissa=10, size=230, step=245
        ),
        ImageService.print_text(bg_img, data["selectors"], (70, 140), step=245),
        ImageService.print_text(
            bg_img, list(SELECTORS.values())[1::], (40, 300), fontsize=52
        ),
        ImageService.paste_icon(bg_img, "tempr.jpg", [30, 400]),
        ImageService.print_text(
            bg_img, [p.temperature for p in data["pumps"]], (30, 460)
        ),
        ImageService.paste_icon(bg_img, "clock.png", [30, 540]),
        ImageService.print_text(bg_img, [p.work for p in data["pumps"]], (30, 600)),
        ImageService.paste_icon(bg_img, "pressure.jpg", [30, 680]),
        ImageService.print_text(bg_img, [p.pressure for p in data["pumps"]], (30, 740)),
    )


async def gas_plot(data: Sequence[Gas_Sensor]):
    colors = cm.get_cmap("tab10")
    selected_date = data[0].dttm.date()

    plt.clf()
    for i in range(1, 5):
        x = [s.dttm for s in data if s.name == str(i)]
        y = [s.value for s in data if s.name == str(i)]
        plt.plot(x, y, label=f"Датчик {i}", color=colors(i - 1 % 4))

    plt.title(f"Датчики загазованности, {selected_date}")
    plt.legend()
    date_format = mdates.DateFormatter("%H:%M")
    plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=3))
    plt.gca().xaxis.set_major_formatter(date_format)
    plt.savefig(settings.archive_img)
    plt.close()


async def pump_plot(data: Sequence[Pump]):
    x = [p.dttm for p in data]
    pump_name = data[0].name
    selected_date = x[0].date()
    plt.clf()
    plt.plot(x, [p.pressure for p in data], label="Давление", color="blue")
    plt.plot(x, [p.temperature for p in data], label="Температура", color="red")
    plt.title(f"Насос {pump_name}: {selected_date}")
    plt.legend()
    date_format = mdates.DateFormatter("%H:%M")
    plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=3))
    plt.gca().xaxis.set_major_formatter(date_format)
    plt.savefig(settings.archive_img)
    plt.close()
