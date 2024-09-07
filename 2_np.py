import pygame as pg  
import numpy as np  

# Определяем разрешение экрана (ширина и высота)
res = width, height = 800, 450

# Определяем сдвиг для центра изображения и нормируем его
offset = np.array([1.3 * width, height]) // 2

# Максимальное количество итераций для фрактала
max_iter = 30

# Коэффициент масштабирования фрактала (уменьшение или увеличение фрактала)
zoom = 2.2 / height

# Загружаем текстуру для наложения на фрактал
texture = pg.image.load('resources/texture.jpg')

# Определяем минимальный размер текстуры для работы с ней
texture_size = min(texture.get_size()) - 1

# Преобразуем изображение текстуры в массив для работы с пикселями
texture_array = pg.surfarray.array3d(texture)

# Класс для работы с фракталом
class Fractal:
    def __init__(self, app):
        self.app = app  # Получаем ссылку на приложение (экран, управление)
        # Инициализируем массив для отображения экрана (RGB), изначально заполняем черным цветом
        self.screen_array = np.full((width, height, 3), [0, 0, 0], dtype=np.uint8)

        # Создаем массивы координат x и y для векторизации вычислений
        self.x = np.linspace(0, width, num=width, dtype=np.float32)
        self.y = np.linspace(0, height, num=height, dtype=np.float32)

    # Метод для рендеринга фрактала
    def render(self):
        # Переводим координаты x и y в комплексное число c для использования в уравнении фрактала
        x = (self.x - offset[0]) * zoom
        y = (self.y - offset[1]) * zoom
        c = x + 1j * y[:, None]  # Создаем двумерное комплексное число c

        # Инициализируем массивы для количества итераций и значений z
        num_iter = np.full(c.shape, max_iter)
        z = np.empty(c.shape, np.complex64)

        # Основной цикл итераций
        for i in range(max_iter):
            mask = (num_iter == max_iter)  # Маска для нерасчетанных пикселей
            z[mask] = z[mask] ** 2 + c[mask]  # Выполняем итерации уравнения фрактала
            num_iter[mask & (z.real ** 2 + z.imag ** 2 > 4.0)] = i + 1  # Обновляем количество итераций, если значение z выходит за пределы

        # Определяем цвет на основе количества итераций
        col = (num_iter.T * texture_size / max_iter).astype(np.uint8)
        # Заполняем массив экрана цветами из текстуры
        self.screen_array = texture_array[col, col]

    # Метод для обновления фрактала
    def update(self):
        self.render()  # Вызываем метод рендеринга

    # Метод для отображения фрактала на экране
    def draw(self):
        # Преобразуем массив экрана в изображение и выводим его на экран приложения
        pg.surfarray.blit_array(self.app.screen, self.screen_array)

    # Основной метод запуска фрактала
    def run(self):
        self.update()  # Обновляем фрактал
        self.draw()  # Рисуем фрактал на экране

# Класс для работы с основным приложением
class App:
    def __init__(self):
        # Создаем окно с заданным разрешением и включаем масштабирование
        self.screen = pg.display.set_mode(res, pg.SCALED)
        self.clock = pg.time.Clock()  # Инициализируем объект для управления временем и FPS
        self.fractal = Fractal(self)  # Создаем объект фрактала, передавая ссылку на приложение

    # Основной метод для запуска приложения
    def run(self):
        while True:  # Бесконечный цикл для работы приложения
            self.screen.fill('black')  # Очищаем экран, заполняя его черным цветом
            self.fractal.run()  # Запускаем рендеринг фрактала
            pg.display.flip()  # Обновляем экран (переключаем буферы)

            # Проверяем события и закрываем приложение, если было нажато закрытие окна
            [exit() for i in pg.event.get() if i.type == pg.QUIT]

            # Ограничиваем FPS для плавной работы
            self.clock.tick()

            # Обновляем заголовок окна с текущим FPS
            pg.display.set_caption(f'FPS: {self.clock.get_fps()}')

# Запуск приложения
if __name__ == '__main__':
    app = App()  # Создаем объект приложения
    app.run()  # Запускаем приложение
