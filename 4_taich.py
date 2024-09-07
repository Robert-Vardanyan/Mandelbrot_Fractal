import pygame as pg
import numpy as np
import taichi as ti
import os

# настройки
res = width, height = 800, 450 # если видеокарта поддерживает CUDA, можно увеличить разрешение и использовать ti.cuda
offset = np.array([1.3 * width, height]) // 2  # центрирование фрактала по экрану
# загрузка текстуры
texture = pg.image.load('resources/texture_2.jpg')  # загрузка изображения
texture_size = min(texture.get_size()) - 1  # определение минимального размера текстуры
texture_array = pg.surfarray.array3d(texture).astype(dtype=np.uint32)  # преобразование текстуры в массив

@ti.data_oriented
class Fractal:
    def __init__(self, app):
        self.app = app
        # инициализация экрана чёрным цветом
        self.screen_array = np.full((width, height, 3), [0, 0, 0], dtype=np.uint32)
        # инициализация архитектуры taichi (можно использовать ti.cpu, ti.cuda и т.д.)
        ti.init(arch=ti.cpu)
        # создание полей для экрана и текстуры
        self.screen_field = ti.Vector.field(3, ti.uint32, (width, height))
        self.texture_field = ti.Vector.field(3, ti.uint32, texture.get_size())
        self.texture_field.from_numpy(texture_array)  # загрузка данных текстуры в поле
        # настройки управления
        self.vel = 0.008  # скорость перемещения
        self.zoom, self.scale = 2.2 / height, 0.993  # начальное увеличение и масштабирование
        self.increment = ti.Vector([0.0, 0.0])  # переменная для смещения
        self.max_iter, self.max_iter_limit = 30, 5500  # начальное количество итераций и лимит
        # delta_time для стабильной скорости отрисовки
        self.app_speed = 1 / 4000
        self.prev_time = pg.time.get_ticks()  # начальное время

    def delta_time(self):
        # вычисление времени, прошедшего с последнего кадра
        time_now = pg.time.get_ticks() - self.prev_time
        self.prev_time = time_now
        return time_now * self.app_speed

    @ti.kernel
    def render(self, max_iter: ti.int32, zoom: ti.float32, dx: ti.float32, dy: ti.float32):
        # основной цикл отрисовки фрактала
        for x, y in self.screen_field:  # параллельный цикл
            # координаты для фрактала с учётом смещения и увеличения
            c = ti.Vector([(x - offset[0]) * zoom - dx, (y - offset[1]) * zoom - dy])
            z = ti.Vector([0.0, 0.0])  # начальные значения z
            num_iter = 0  # счётчик итераций
            for i in range(max_iter):  # итерации для вычисления фрактала
                z = ti.Vector([(z.x ** 2 - z.y ** 2 + c.x), (2 * z.x * z.y + c.y)])  # вычисление нового z
                if z.dot(z) > 4:  # выход из цикла, если расстояние велико
                    break
                num_iter += 1
            col = int(texture_size * num_iter / max_iter)  # вычисление цвета по количеству итераций
            self.screen_field[x, y] = self.texture_field[col, col]  # установка цвета пикселя

    def control(self):
        # управление перемещением и масштабированием
        pressed_key = pg.key.get_pressed()
        dt = self.delta_time()  # получение времени между кадрами
        # перемещение
        if pressed_key[pg.K_a]:
            self.increment[0] += self.vel * dt
        if pressed_key[pg.K_d]:
            self.increment[0] -= self.vel * dt
        if pressed_key[pg.K_w]:
            self.increment[1] += self.vel * dt
        if pressed_key[pg.K_s]:
            self.increment[1] -= self.vel * dt

        # стабильное увеличение и перемещение
        if pressed_key[pg.K_UP] or pressed_key[pg.K_DOWN]:
            inv_scale = 2 - self.scale  # обратный масштаб
            if pressed_key[pg.K_UP]:
                self.zoom *= self.scale  # увеличение масштаба
                self.vel *= self.scale  # увеличение скорости
            if pressed_key[pg.K_DOWN]:
                self.zoom *= inv_scale  # уменьшение масштаба
                self.vel *= inv_scale  # уменьшение скорости

        # изменение количества итераций для фрактала
        if pressed_key[pg.K_LEFT]:
            self.max_iter -= 1  # уменьшение итераций
        if pressed_key[pg.K_RIGHT]:
            self.max_iter += 1  # увеличение итераций
        # ограничение количества итераций в пределах лимита
        self.max_iter = min(max(self.max_iter, 2), self.max_iter_limit)

    def update(self):
        # обновление экрана фрактала
        self.control()  # обработка управления
        self.render(self.max_iter, self.zoom, self.increment[0], self.increment[1])  # рендеринг фрактала
        self.screen_array = self.screen_field.to_numpy()  # преобразование поля в массив

    def draw(self):
        # отрисовка фрактала на экране
        pg.surfarray.blit_array(self.app.screen, self.screen_array)

    def run(self):
        # основной цикл обновления и отрисовки
        self.update()
        self.draw()


class App:
    def __init__(self):
        # создание окна и инициализация фрактала
        self.screen = pg.display.set_mode(res, pg.SCALED)
        self.clock = pg.time.Clock()
        self.fractal = Fractal(self)

        # создание папки для скриншотов
        if not os.path.exists('screenshots'):
            os.makedirs('screenshots')

    def run(self):
        # основной цикл приложения
        while True:
            self.screen.fill('black')  # очистка экрана
            self.fractal.run()  # выполнение фрактала
            pg.display.flip()  # обновление экрана

            # проверка событий для выхода
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    exit()

            # проверка нажатия клавиш
            pressed_key = pg.key.get_pressed()
            if pressed_key[pg.K_x]:
                # создание имени для скриншота и сохранение изображения
                screenshot_name = f'screenshots/screenshot_{pg.time.get_ticks()}.png'
                pg.image.save(self.screen, screenshot_name)
                print(f'Screenshot saved: {screenshot_name}')
            
            
            self.clock.tick()  # обновление времени
            pg.display.set_caption(f'FPS: {self.clock.get_fps() :.2f}')  # вывод FPS в заголовке окна


if __name__ == '__main__':
    # запуск приложения
    app = App()
    app.run()
