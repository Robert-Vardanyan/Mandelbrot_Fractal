import pygame as pg
import numpy as np
import numba as nb

res = width, height = 800, 450
offset = np.array([1.3 * width, height]) // 2
max_iter = 30
zoom = 2.2 / height
scale = 0.993  # Коэффициент масштабирования

texture = pg.image.load('resources/texture_2.jpg')
texture_size = min(texture.get_size()) - 1
texture_array = pg.surfarray.array3d(texture)

class Fractal:
    def __init__(self, app):
        self.app = app
        self.screen_array = np.full((width, height, 3), [0, 0, 0], dtype=np.uint8)
        self.increment = np.array([0.0, 0.0], dtype=np.float32)
        self.vel = 500.0  # Скорость перемещения
        self.zoom = zoom  # Коэффициент масштабирования
        self.scale = scale  # Коэффициент изменения масштаба
        self.max_iter = max_iter
        self.max_iter_limit = 5500  # Максимально допустимое количество итераций

    @staticmethod
    @nb.njit(fastmath=True, parallel=True)
    def render(screen_array, offset, zoom, max_iter, texture_array, texture_size):
        for x in nb.prange(width):
            for y in nb.prange(height):
                c = (x - offset[0]) * zoom + 1j * (y - offset[1]) * zoom
                z = 0
                num_iter = 0
                for i in range(max_iter):
                    z = z ** 2 + c
                    if z.real ** 2 + z.imag ** 2 > 4:
                        break
                    num_iter += 1
                col = int(texture_size * num_iter / max_iter)
                screen_array[x, y] = texture_array[col, col]
        return screen_array

    def update(self):
        self.control()  # Добавляем управление перед обновлением и рисованием
        # self.render(self.max_iter, self.zoom, self.increment[0], self.increment[1])
        self.screen_array = self.render(self.screen_array, offset, self.zoom, self.max_iter, texture_array, texture_size)

    def draw(self):
        pg.surfarray.blit_array(self.app.screen, self.screen_array)

    def control(self):
        pressed_key = pg.key.get_pressed()
        dt = self.app.clock.get_time() / 1000.0  # Используем время между кадрами для плавности

        # Управление перемещением
        if pressed_key[pg.K_a]:
            offset[0] += self.vel * dt
        if pressed_key[pg.K_d]:
            offset[0] -= self.vel * dt
        if pressed_key[pg.K_w]:
            offset[1] += self.vel * dt
        if pressed_key[pg.K_s]:
            offset[1] -= self.vel * dt

        # Управление масштабированием
        if pressed_key[pg.K_UP] or pressed_key[pg.K_DOWN]:
            inv_scale = 2 - self.scale
            if pressed_key[pg.K_UP]:
                self.zoom *= self.scale
                self.vel *= self.scale
            if pressed_key[pg.K_DOWN]:
                self.zoom *= inv_scale
                self.vel *= inv_scale

        # Управление разрешением Mandelbrot
        if pressed_key[pg.K_LEFT]:
            self.max_iter = max(2, self.max_iter - 1)
        if pressed_key[pg.K_RIGHT]:
            self.max_iter = min(self.max_iter_limit, self.max_iter + 1)

    def run(self):
        self.update()
        self.draw()

class App:
    def __init__(self):
        self.screen = pg.display.set_mode(res, pg.SCALED)
        self.clock = pg.time.Clock()
        self.fractal = Fractal(self)

    def run(self):
        while True:
            self.screen.fill('black')
            self.fractal.run()
            pg.display.flip()

            [exit() for i in pg.event.get() if i.type == pg.QUIT]
            self.clock.tick()
            pg.display.set_caption(f'FPS: {self.clock.get_fps()}')

if __name__ == '__main__':
    app = App()
    app.run()