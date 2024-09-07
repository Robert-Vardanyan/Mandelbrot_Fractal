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

    # Метод для рендеринга фрактала
    def render(self):
        # Проходим по каждому пикселю экрана
        for x in range(width):
            for y in range(height):
                # Переводим координаты пикселя в комплексное число c, чтобы использовать его в уравнении фрактала
                c = (x - offset[0]) * zoom + 1j * (y - offset[1]) * zoom
                z = 0  # Инициализируем начальное значение z как 0 (начальная точка)
                num_iter = 0  # Считаем количество итераций
                for i in range(max_iter):
                    # Основное уравнение фрактала: z = z^2 + c
                    z = z ** 2 + c
                    # Если модуль z больше 2, выходим из цикла (точка вне множества Мандельброта)
                    if abs(z) > 2:
                        break
                    num_iter += 1  # Увеличиваем счетчик итераций
                # Определяем цвет на основе количества итераций
                col = int(texture_size * num_iter / max_iter)
                # Устанавливаем цвет пикселя с использованием текстуры
                self.screen_array[x, y] = texture_array[col, col]

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
