import math
import os
import pickle

import pygame

RADIUS = 15
ALPHABET_ENG = {chr(i): True for i in range(ord('a'), ord('z') + 1)}
INDEX = 0
COLOR_WHITE = pygame.Color('white')
COLOR_BLACK = pygame.Color('black')
COLOR_ACTIVE_INPUT_TEXT = pygame.Color('dodgerblue2')
COLOR_INACTIVE_INPUT_TEXT = pygame.Color('lightskyblue3')
DIRECTORY_FOR_IMAGES = 'gui_images'


def resource_path(relative_path):
    return relative_path


def draw_ang(screen, arrow, angle, pos):
    nar = pygame.transform.rotate(arrow, angle)
    nrect = nar.get_rect(center=pos)
    screen.blit(nar, nrect)


def unselect(self):
    self.message = ''
    self.main_gui.active = False
    self.load_or_save_graph = None
    self.text = ''
    self.input_text = False
    self.wait_for_node = False
    self.selected_node = None
    self.input_weight = False
    self.selected_rib = None


def dijkstra(graph, node):
    result = {node_.name: None if node_ != node else 0 for node_ in graph.nodes}
    current_nodes = [node]
    while current_nodes:
        current_node = current_nodes.pop(0)
        for rib in current_node.out_ribs:
            if result[rib.input_node.name] is None or \
                    result[rib.input_node.name] > result[current_node.name] + rib.weight:
                result[rib.input_node.name] = result[current_node.name] + rib.weight
                current_nodes.append(rib.input_node)
            if result[rib.out_node.name] is None or result[rib.out_node.name] > result[
                current_node.name] + rib.weight:
                result[rib.out_node.name] = result[current_node.name] + rib.weight
                current_nodes.append(rib.out_node)
    return 1, node, result


def calculate_the_ways(graph, node):
    if not all(map(lambda x: x.oriented, graph.ribs)):
        return False
    result = {node_.name: 0 if node_ != node else 1 for node_ in graph.nodes}
    current_nodes = [node]
    current_node = current_nodes.pop(0)
    while True:
        for rib in current_node.out_ribs:
            result[rib.input_node.name] = sum(
                [result[rib.out_node.name] for rib in rib.input_node.input_ribs])
            current_nodes.append(rib.input_node)
        if not current_nodes:
            break
        current_node = current_nodes.pop(0)
        if current_node == node:
            return False
    return 2, node, result


class Gui:
    def __init__(self):
        self.node = self.load_image(resource_path(DIRECTORY_FOR_IMAGES + '/node.png'))
        self.oriented_rib = self.load_image(
            resource_path(DIRECTORY_FOR_IMAGES + '/orientedrib.png'))
        self.no_oriented_rib = self.load_image(
            resource_path(DIRECTORY_FOR_IMAGES + '/noorientedrib.png'))
        self.delete = self.load_image(resource_path(DIRECTORY_FOR_IMAGES + '/delete.png'))
        self.delete_rect = self.delete.get_rect().move(754, 5)
        self.node_rect = self.node.get_rect().move(604, 5)
        self.no_oriented_rib_rect = self.no_oriented_rib.get_rect().move(654, 5)
        self.oriented_rib_rect = self.oriented_rib.get_rect().move(704, 5)
        self.node_rect.x -= 2
        self.node_rect.w += 4
        self.node_rect.y -= 2
        self.node_rect.h += 4
        self.no_oriented_rib_rect.x -= 2
        self.no_oriented_rib_rect.w += 4
        self.oriented_rib_rect.x -= 2
        self.oriented_rib_rect.w += 4
        self.no_oriented_rib_rect.y -= 2
        self.no_oriented_rib_rect.h += 4
        self.oriented_rib_rect.y -= 2
        self.oriented_rib_rect.h += 4
        self.delete_rect.x -= 2
        self.delete_rect.w += 4
        self.delete_rect.y -= 2
        self.delete_rect.h += 4
        self.save = pygame.Rect(605, 80, 80, 32)
        self.load = pygame.Rect(718, 80, 80, 32)
        self.input_text = pygame.Rect(605, 114, 194, 32)
        self.active = False

    def collide(self, pos):
        if self.node_rect.collidepoint(pos):
            return [1, 0, 0, 0]
        elif self.no_oriented_rib_rect.collidepoint(pos):
            return [0, 1, 0, 0]
        elif self.oriented_rib_rect.collidepoint(pos):
            return [0, 0, 1, 0]
        elif self.delete_rect.collidepoint(pos):
            return 3
        elif self.save.collidepoint(pos):
            return 1
        elif self.load.collidepoint(pos):
            return 2
        return False

    def draw_gui(self, win, active=None):
        # pygame.draw.rect(win, COLOR_WHITE, (602, 28, 196, 49), 2)
        pygame.draw.rect(win, COLOR_WHITE, self.node_rect, 2)
        pygame.draw.rect(win, COLOR_WHITE, self.delete_rect, 2)
        pygame.draw.rect(win, COLOR_WHITE, self.oriented_rib_rect, 2)
        pygame.draw.rect(win, COLOR_WHITE, self.no_oriented_rib_rect, 2)
        if self.active:
            pygame.draw.rect(win, COLOR_ACTIVE_INPUT_TEXT, self.input_text, 4)
        else:
            pygame.draw.rect(win, COLOR_INACTIVE_INPUT_TEXT, self.input_text, 4)
        if active is not None:
            if active[0]:
                pygame.draw.rect(win, pygame.Color('red'), self.node_rect, 2)
            elif active[1]:
                pygame.draw.rect(win, pygame.Color('red'), self.no_oriented_rib_rect, 2)
            elif active[2]:
                pygame.draw.rect(win, pygame.Color('red'), self.oriented_rib_rect, 2)
        win.blit(self.node, (self.node_rect.x + 2, self.node_rect.y + 2))
        win.blit(self.delete, (self.delete_rect.x + 2, self.delete_rect.y + 2))
        win.blit(self.oriented_rib, (self.oriented_rib_rect.x + 2, self.oriented_rib_rect.y + 2))
        win.blit(self.no_oriented_rib,
                 (self.no_oriented_rib_rect.x + 2, self.no_oriented_rib_rect.y + 2))
        pygame.draw.rect(win, (22, 171, 168), self.save)
        pygame.draw.rect(win, (22, 171, 168), self.load)
        font = pygame.font.Font(None, 30)
        text = font.render('save', True, COLOR_WHITE)
        x_text = self.save.x + (self.save.w - text.get_width()) // 2
        y_text = self.save.y + (self.save.h - text.get_height()) // 2
        win.blit(text, (x_text, y_text))
        text = font.render('load', True, COLOR_WHITE)
        x_text = self.load.x + (self.load.w - text.get_width()) // 2
        y_text = self.load.y + (self.load.h - text.get_height()) // 2
        win.blit(text, (x_text, y_text))

    def load_image(self, name, colorkey=None):
        pygame.init()
        fullname = os.path.join(name)
        image = pygame.image.load(fullname)
        if colorkey is not None:
            image = image.convert()
            if colorkey == -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey)
        else:
            image = image.convert_alpha()
            image = pygame.transform.scale(image, (45, 45))
        return image


class Main:
    def __init__(self, win):
        self.graph_edit = Graph()
        self.win = win
        self.running = True
        self.gui = pygame.Surface((205, 600))
        self.main_gui = Gui()

        # params for main cycle
        self.selected = [0, 0, 0, 0]
        self.text = ''
        self.wait_for_node = False
        self.selected_node = None
        self.input_weight = False
        self.selected_rib = None
        self.input_text = False
        self.load_or_save_graph = 0
        self.message = ''
        self.result = None
        self.run()

    def run(self):
        global INDEX
        # main cycle
        while self.running:
            for event in pygame.event.get():
                # quit
                if event.type == pygame.QUIT:
                    self.running = False
                pos = pygame.mouse.get_pos()
                # input weight for rib
                if self.input_weight:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            self.selected_rib.set_weight(self.text)
                            self.selected_rib = None
                            self.input_weight = False
                            self.text = ''
                        elif event.key == pygame.K_BACKSPACE:
                            self.text = self.text[:-1]
                            self.selected_rib.set_weight(self.text)
                        elif event.key == pygame.K_ESCAPE:
                            unselect(self)
                        else:
                            if self.selected_rib:
                                if event.unicode.isdigit():
                                    self.text += event.unicode
                                    self.selected_rib.set_weight(self.text)
                elif self.input_text:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            if self.load_or_save_graph == 1:
                                self.save(self.text)
                            elif self.load_or_save_graph == 2:
                                self.load(self.text)
                            self.text = ''
                            self.main_gui.active = False
                            self.input_text = False
                        elif event.key == pygame.K_BACKSPACE:
                            self.text = self.text[:-1]
                        elif event.key == pygame.K_ESCAPE:
                            unselect(self)
                        else:
                            self.text += event.unicode
                # detect mouse event
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        selected = self.main_gui.collide(pos)
                        if selected:
                            if selected == 2:
                                unselect(self)
                                self.selected = [0, 0, 0, 0]
                                self.main_gui.active = True
                                self.input_text = True
                                self.load_or_save_graph = 2
                            elif selected == 1:
                                unselect(self)
                                self.selected = [0, 0, 0, 0]
                                self.main_gui.active = True
                                self.input_text = True
                                self.load_or_save_graph = 1
                            elif selected == 3:
                                self.delete_node_or_rib()
                            elif not selected:
                                pass
                            else:
                                self.selected = selected

                        else:
                            # mode to choose node
                            if self.selected[0]:
                                rect = self.gui.get_rect()
                                rect.x = 590
                                rect.y = 0
                                if not rect.collidepoint(pos):
                                    f = True
                                    for node in self.graph_edit.nodes:
                                        x, y = node.get_pos()
                                        if ((x - pos[0]) ** 2 + (
                                                y - pos[1]) ** 2) ** 0.5 < RADIUS * 2:
                                            f = False
                                    if f:
                                        name = min(filter(lambda x: self.graph_edit.ALPHABET_ENG[x],
                                                          self.graph_edit.ALPHABET_ENG.keys()))
                                        self.graph_edit.ALPHABET_ENG[name] = False
                                        node = Node(*pos, name)
                                        INDEX += 1
                                        self.graph_edit.add_node(node)
                            elif self.selected[1]:
                                self.wait_for_node = True
                            elif self.selected[2]:
                                self.wait_for_node = True

                            # create new rib
                            if self.selected_node and (self.selected[1] or self.selected[2]):
                                for node in self.graph_edit.nodes:
                                    x, y = node.get_pos()
                                    if ((x - pos[0]) ** 2 + (y - pos[1]) ** 2) ** 0.5 < RADIUS:
                                        if node is self.selected_node or \
                                                node in self.selected_node.get_liaison_nodes() or \
                                                self.selected_node in node.get_liaison_nodes():
                                            continue
                                        self.input_weight = True
                                        if self.selected[1]:
                                            self.text = ''
                                            rib = NoOrientedRib(0)
                                            rib.set_nodes([self.selected_node, node])
                                            self.graph_edit.ribs.append(rib)
                                            node.add_out_rib(rib)
                                            node.add_input_rib(rib)
                                            self.selected_node.add_out_rib(rib)
                                            self.selected_node.add_input_rib(rib)
                                            self.selected_rib = rib
                                            break
                                        elif self.selected[2]:
                                            self.text = ''
                                            rib = OrientedRib(0)
                                            rib.set_out_node(self.selected_node)
                                            rib.set_input_node(node)
                                            node.add_input_rib(rib)
                                            self.selected_node.add_out_rib(rib)
                                            self.graph_edit.add_rib(rib)
                                            self.selected_rib = rib
                                            break
                                        else:
                                            self.input_weight = False
                                else:
                                    unselect(self)
                                self.selected_node = None

                            # choose the node
                            elif self.selected == [0, 0, 0, 0]:
                                for node in self.graph_edit.nodes:
                                    x, y = node.get_pos()
                                    if ((x - pos[0]) ** 2 + (y - pos[1]) ** 2) ** 0.5 <= RADIUS:
                                        self.selected_node = node
                                        self.selected_rib = None
                                        break
                                for rib in self.graph_edit.ribs:
                                    if rib.rect_for_text.collidepoint(pos):
                                        self.selected_rib = rib
                                        self.input_weight = True
                                        self.text = '' if not rib.weight else str(rib.weight)
                                        self.selected_node = None
                                        break
                            # choose the node or rib
                            elif self.wait_for_node:
                                for node in self.graph_edit.nodes:
                                    x, y = node.get_pos()
                                    if ((x - pos[0]) ** 2 + (y - pos[1]) ** 2) ** 0.5 <= RADIUS:
                                        self.selected_node = node
                                        self.selected_rib = None
                                        break
                                for rib in self.graph_edit.ribs:
                                    try:
                                        if rib.rect_for_text.collidepoint(pos):
                                            self.selected_rib = rib
                                            self.input_weight = True
                                            self.text = '' if not rib.weight else str(rib.weight)
                                            self.selected_node = None
                                            break
                                    except Exception as ex:
                                        pass

                # detect press keys
                if event.type == pygame.KEYDOWN and not self.input_text:
                    if event.key == pygame.K_n:
                        self.selected = [1, 0, 0, 0]
                        unselect(self)
                    elif event.key == pygame.K_ESCAPE:
                        self.selected = [0, 0, 0, 0]
                        unselect(self)
                    elif event.key == pygame.K_r:
                        self.selected = [0, 1, 0, 0]
                        unselect(self)
                    elif event.key == pygame.K_o:
                        self.selected = [0, 0, 1, 0]
                        unselect(self)
                    elif event.key == pygame.K_d and (self.selected_node or self.selected_rib):
                        self.delete_node_or_rib()
                    elif event.key == pygame.K_b and self.selected_node:
                        self.result = dijkstra(self.graph_edit, self.selected_node)
                        self.create_message_from_result()
                    elif event.key == pygame.K_c and self.selected_node:
                        self.result = calculate_the_ways(self.graph_edit, self.selected_node)
                        self.create_message_from_result()
                    elif event.key == pygame.K_s:
                        unselect(self)
                        self.input_text = True
                        self.main_gui.active = True
                    elif event.key == pygame.K_l:
                        unselect(self)
                        self.input_text = True
                        self.main_gui.active = True

            # print(self.selected, self.wait_for_node, self.selected_node, self.selected_rib,
            # self.load_or_save_graph)  # debug
            #  print(self.selected_node, self.graph_edit.nodes, self.graph_edit.ribs)
            # print(self.input_text, self.text)
            # try:
            #     print('text', self.text, 'weight', self.selected_rib.weight)
            # except:
            #     print(self.text)

            self.draw()
        pygame.quit()

    def draw(self):
        # main def for draw
        self.win.fill(COLOR_WHITE)
        self.gui.fill((120, 120, 120))
        for rib in self.graph_edit.ribs:
            rib.draw(self.win)
        for node in self.graph_edit.nodes:
            node.draw(self.win, active=node == self.selected_node)
        self.draw_gui()
        pygame.display.flip()
        pygame.display.update()

    def draw_gui(self):
        font = pygame.font.Font(None, 30)
        if self.selected_rib:
            pygame.draw.rect(self.win, (255, 0, 0), self.selected_rib.rect_for_text, 2)
            text = font.render(f"Selected - {self.selected_rib}", True, COLOR_WHITE)
            x_text = 5
            y_text = 47 + text.get_height() // 2
            self.gui.blit(text, (x_text, y_text))
        elif self.selected_node:
            text = font.render(f"Selected - {self.selected_node.name}", True, COLOR_WHITE)
            x_text = 5
            y_text = 47 + text.get_height() // 2
            self.gui.blit(text, (x_text, y_text))
        self.win.blit(self.gui, (600, 0))
        font_for_message = pygame.font.Font(None, 28)
        x_text = 605
        y_text = 130
        for line in self.message.split('\n'):
            text = font_for_message.render(line, True, COLOR_WHITE)
            y_text += 24
            self.win.blit(text, (x_text, y_text))
        if self.input_text:
            text = font.render(f"{self.text}", True, COLOR_WHITE)
            x_text = self.main_gui.input_text.x + 6
            y_text = self.main_gui.input_text.y + 6
            self.win.blit(text, (x_text, y_text))
        self.main_gui.draw_gui(self.win, active=self.selected)

    def delete_node_or_rib(self):
        try:
            self.graph_edit.remove_node(self.selected_node)
            copy_ribs = self.graph_edit.ribs[:]
            self.text = ''

            for rib in copy_ribs:
                if self.selected_node in rib.nodes:
                    self.graph_edit.remove_rib(rib)
            self.selected_node = None
        except Exception as ex:
            self.graph_edit.remove_rib(self.selected_rib)
            self.selected_rib = None
        finally:
            unselect(self)

    def save(self, filename):
        with open(f'{filename}.graph', 'wb') as f:
            pickle.dump(self.graph_edit, f)
            self.message = 'Граф успешно \nсохранён'

    def load(self, filename):
        if os.path.exists(f"{filename}.graph"):
            with open(f'{filename}.graph', 'rb') as f:
                self.graph_edit = pickle.load(f)
        else:
            self.message = 'Такого файла не\n существует'

    def create_message_from_result(self):
        text = None
        if self.result:
            if self.result[0] == 1:
                text = f'Кратчайшие пути \nиз точки {self.result[1]}\n'
                result = self.result[2]
                for key, value in result.items():
                    text += f'{self.result[1]} -> {key} = {value if value is not None else "Нет пути"}\n'
            elif self.result[0] == 2:
                text = f'Кол-во путей \nиз точки {self.result[1]}\n'
                result = self.result[2]
                if result:
                    for key, value in result.items():
                        text += f'{self.result[1]} -> {key} = {value if value else "Нет пути"}\n'
        else:
            text = 'Граф содержит \nциклы'
        self.message = text


class Node:
    def __init__(self, x, y, name):
        self.name = name
        self.x = x
        self.y = y
        self.out_ribs = []
        self.input_ribs = []
        self.power = 0

    def get_pos(self):
        return self.x, self.y

    def add_out_rib(self, rib):
        self.out_ribs.append(rib)

    def add_input_rib(self, rib):
        self.input_ribs.append(rib)

    def remove_rib(self, rib):
        if rib in self.out_ribs:
            self.out_ribs.remove(rib)
        if rib in self.input_ribs:
            self.input_ribs.remove(rib)

    def draw(self, win, active=False):
        if active:
            pygame.draw.circle(win, COLOR_BLACK, (self.x, self.y), RADIUS)
            font = pygame.font.Font(None, 30)
            text = font.render(f"{self.name}", True, pygame.Color('red'))
            x_text = self.x - text.get_width() // 2
            y_text = self.y - text.get_height() // 2
            win.blit(text, (x_text, y_text))
        else:
            pygame.draw.circle(win, COLOR_BLACK, (self.x, self.y), RADIUS)
            font = pygame.font.Font(None, 30)
            text = font.render(f"{self.name}", True, COLOR_WHITE)
            x_text = self.x - text.get_width() // 2
            y_text = self.y - text.get_height() // 2
            win.blit(text, (x_text, y_text))

    def get_liaison_nodes(self):
        result = []
        for rib in self.out_ribs:
            result.append(rib.input_node)
        return result

    def __repr__(self):
        return f'{self.name}'


class Rib:
    def __init__(self, weight=0):
        self.nodes = [None, None]
        self.out_node = None
        self.input_node = None
        self.weight = weight
        self.rect_for_text = None
        self.oriented = False

    def set_weight(self, weight):
        try:
            if not weight:
                self.weight = 0
            self.weight = int(weight)
        except Exception as ex:
            return ex

    def draw(self, win, arrow=False):
        points = [node.get_pos() for node in self.nodes]
        if self.oriented:  # draw an arrow if rib is oriented
            len_ = ((points[0][0] - points[1][0]) ** 2 + (points[0][1] - points[1][1]) ** 2) ** 0.5
            ratio = len_ / (len_ - RADIUS)
            x1 = -(self.nodes[0].x - self.nodes[1].x) / ratio + self.nodes[0].x
            y1 = -(self.nodes[0].y - self.nodes[1].y) / ratio + self.nodes[0].y
            pos2 = x1, y1
            pos1 = points[0]
            x, y = 30, 12
            arrow = pygame.Surface((x, y), pygame.SRCALPHA)
            arrow.fill((255, 255, 255, 0))
            pygame.draw.line(arrow, COLOR_BLACK, (0, 0), (x // 2, y // 2), 3)
            pygame.draw.line(arrow, COLOR_BLACK, (0, y), (x // 2, y // 2), 3)
            angle = math.atan2(-(pos1[1] - pos2[1]), pos1[0] - pos2[0])
            angle = math.degrees(angle) + 180
            draw_ang(win, arrow, angle, pos2)
        # main draw the rib
        pygame.draw.line(win, COLOR_BLACK, points[0], points[1], 3)
        font = pygame.font.Font(None, 30)
        text = font.render(f"{self.weight}", True, COLOR_BLACK)
        x_text, y_text = self.get_cords_for_text()
        x_text -= 5
        y_text -= 2
        self.rect_for_text = pygame.Rect(x_text, y_text, 15, 20)
        self.rect_for_text.w = max(15, text.get_width() + 10)
        win.blit(text, self.get_cords_for_text())

    def get_cords_for_text(self):
        x1 = self.nodes[0].x
        y1 = self.nodes[0].y
        x2 = self.nodes[1].x
        y2 = self.nodes[1].y
        x = abs(x1 + x2) // 2
        y = abs(y1 + y2) // 2
        if y2 > y1:
            y -= 12
        else:
            y += 15
        x += 12
        return x, y

    def __repr__(self):
        return str(self.nodes)


class OrientedRib(Rib):
    def __init__(self, weight=0):
        Rib.__init__(self, weight)
        self.oriented = True

    def set_out_node(self, node):
        self.out_node = node
        self.nodes[0] = node

    def set_input_node(self, node):
        self.input_node = node
        self.nodes[1] = node


class NoOrientedRib(Rib):
    def __init__(self, weight=0):
        self.nodes = []
        self.oriented = False
        Rib.__init__(self, weight)

    def set_nodes(self, nodes):
        self.nodes = nodes
        self.input_node = nodes[1]
        self.out_node = nodes[0]


class Graph:
    def __init__(self):
        self.ALPHABET_ENG = ALPHABET_ENG.copy()
        self.nodes = []
        self.ribs = []

    def add_node(self, node):
        self.nodes.append(node)

    def add_rib(self, rib):
        self.ribs.append(rib)

    def remove_node(self, node):
        ALPHABET_ENG[node.name] = True
        self.nodes.remove(node)

    def remove_rib(self, rib):
        self.ribs.remove(rib)
        for node in rib.nodes:
            node.remove_rib(rib)


if __name__ == '__main__':
    pygame.init()
    print(os.listdir('.'))
    win = pygame.display.set_mode((805, 600))
    pygame.display.set_caption('Graph_drwer')
    icon = pygame.image.load(resource_path('icon.png'))
    icon = icon.convert_alpha()
    pygame.display.set_icon(icon)
    main = Main(win)
