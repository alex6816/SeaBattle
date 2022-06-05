from random import randint


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f'({self.x}, {self.y})'


class FieldException(Exception):
    pass


class FieldOutException(FieldException):
    def __str__(self):
        return 'Вы пытаетесь выстрелить за пределы поля!'


class FieldUsedException(FieldException):
    def __str__(self):
        return 'Вы уже стреляли в эту клетку!'


class FieldWrongShipException(FieldException):
    pass


class Boat:
    def __init__(self, bow, len, dir):
        self.bow = bow  # координаты носа корабля
        self.len = len  # длина корабля
        self.dir = dir  # ориентация корабля
        self.life = len  # количетсво жизней корабля

    @property
    def kit(self):
        boat_kit = []  # список точек корабля
        for i in range(self.len):
            coor_x = self.bow.x
            coor_y = self.bow.y
            if self.dir == 0:
                coor_x += i
            elif self.dir == 1:
                coor_y += i
            boat_kit.append(Point(coor_x, coor_y))
        return boat_kit


class Field:
    def __init__(self, hid=False, size=6):
        self.hid = hid
        self.size = size

        self.lost = 0  # количество уничтоженных кораблей
        self.buzy = []  # список занятых точек
        self.boats = []  # список кораблей

        self.court = [[' '] * size for _ in range(size)]  # создаем пустое игровое поле

    def __str__(self):
        res = ''
        res += '     1   2   3   4   5   6  '

        for i, row in enumerate(self.court):
            res += f'\n   -------------------------\n {i + 1} | ' + ' | '.join(row) + ' |'

        if self.hid:
            res = res.replace('■', ' ')

        return res + '\n   -------------------------'

    def outline(self, boat, verb=False):  # обводим корабль по контуру
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]

        for d in boat.kit:
            for dx, dy in near:
                cont = Point(d.x + dx, d.y + dy)
                if not self.out(cont) and cont not in self.buzy:
                    if verb:
                        self.court[cont.x][cont.y] = '.'
                    self.buzy.append(cont)  # добавляем точки вокруг корабля в список занятых

    def add_boat(self, boat):  # добавляем корабль на поле
        for d in boat.kit:
            if self.out(d) or d in self.buzy:
                raise FieldWrongShipException()
        for d in boat.kit:
            self.court[d.x][d.y] = '■'
            self.buzy.append(d)

        self.boats.append(boat)  # добавляем в список кораблей
        self.outline(boat)  # обводим корабль по контуру

    def shot(self, d):  # производим выстрел
        if self.out(d):
            raise FieldOutException()
        if d in self.buzy:
            raise FieldUsedException()

        self.buzy.append(d)  # добавляем точку в список занятых

        for boat in self.boats:
            if d in boat.kit:  # при попадании
                boat.life -= 1  # уменьшаем количество жизней
                self.court[d.x][d.y] = 'X'
                if boat.life == 0:
                    self.lost += 1
                    self.outline(boat, verb=True)
                    print('Корабль уничтожен!')
                    return False
                else:
                    print('Корабль ранен!')
                    return True

        self.court[d.x][d.y] = '.'
        print('Мимо!')
        return False

    def onset(self):  # обнуляем список занятых точек
        self.buzy = []

    def out(self, p):  # проверка не выходит ли точка за пределы поля
        return not ((0 <= p.x < self.size) and (0 <= p.y < self.size))


class Player:
    def __init__(self, field, enemy):
        self.field = field  # игровое поле пользователя
        self.enemy = enemy  # игровое поле противника

    def ask(self):
        raise NotImplementedError()

    def step(self):  # ход игрока или компьютера
        while True:
            try:
                target = self.ask()  # получаем точку для атаки
                repeat = self.enemy.shot(target)  # делаем выстрел
                return repeat
            except FieldException as e:
                print(e)


class AI(Player):
    def ask(self):
        d = Point(randint(0, 5), randint(0, 5))
        print(f'Ход компьютера: {d.x + 1} {d.y + 1}')
        return d


class User(Player):
    def ask(self):  # проверка введенных данных пользователя
        while True:
            coords = input('Ваш ход: ').split()

            if len(coords) != 2:
                print('Введите 2 координаты!')
                continue

            x, y = coords

            if not (x.isdigit()) or not (y.isdigit()):
                print('Введите числа! ')
                continue

            x, y = int(x), int(y)
            return Point(x - 1, y - 1)


class Game:

    def __init__(self, size=6):
        self.size = size
        pl = self.random_field()  # игровое поле пользователя
        comp = self.random_field()  # игровое поле компьютера
        comp.hid = True

        self.ai = AI(comp, pl)
        self.user = User(pl, comp)

    def try_field(self):  # создание игрового поля с кораблями
        lens = [3, 2, 2, 1, 1, 1, 1]
        field = Field(size=self.size)
        attempts = 0  # количество попыток создания поля
        for ln in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                boat = Boat(Point(randint(0, self.size), randint(0, self.size)), ln, randint(0, 1))
                try:
                    field.add_boat(boat)
                    break
                except FieldWrongShipException:
                    pass
        field.onset()
        return field

    def random_field(self):
        field = None
        while field is None:
            field = self.try_field()
        return field

    def loop(self):  # игровой процесс
        count = 0  # количество ходов
        while True:
            print('-' * 20)
            print('Игровое поле пользователя:')
            print(self.user.field)
            print('-' * 20)
            print('Игровое поле компьютера:')
            print(self.ai.field)
            print('-' * 20)
            if count % 2 == 0:
                print('Стреляет пользователь!')
                repeat = self.user.step()
            else:
                print('Стреляет компьютер!')
                repeat = self.ai.step()
            if repeat:
                count -= 1

            if self.ai.field.lost == 7:  # уничтожены все 7 кораблей противника
                print('-' * 20)
                print('Пользователь выиграл!')
                break

            if self.user.field.lost == 7:
                print('-' * 20)
                print('Компьютер выиграл!')
                break
            count += 1

    def greet(self):
        print("-------------------")
        print("  Приветсвуем вас  ")
        print("      в игре       ")
        print("    морской бой    ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()
