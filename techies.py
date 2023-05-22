import tkinter as tk
from random import shuffle
from tkinter.messagebox import showinfo, showerror
from tkinter import font
from pygame import mixer

mixer.init()

# Цвета для цифр
colors = {
    0: 'white',
    1: '#0a03ff',
    2: '#089c00',
    3: '#f00505',
    4: '#000085',
    5: '#854500',
    6: '#be02f7',
    7: '#940148',
    8: '#ff0000'
}


# Цвета для поля
lightgreen='#59b33b' 
darkgreen='#34751e'


class MyButton(tk.Button):

    def __init__(self, master, color, x, y, number=0, *args, **kwargs):
        # Наследуем класс кнопка и передаём значения
        super(MyButton, self).__init__(master, bg= color, borderwidth=7, overrelief='raised' ,relief='flat' ,width = 3, font='Calibri 15 bold', *args, **kwargs)
        self.x = x
        self.y = y
        self.number = number
        self.is_mine = False
        self.count_bomb = 0
        self.is_open = False

# Счётчик времени
time=0


class MineSweeper:


    # Создаём окно игры
    window = tk.Tk()
    window.title('Minesweeper')
    window.iconbitmap(default='icon.ico')
    window.resizable(False, False)


    # Шрифт для текста
    font2 = font.Font(family= "Verdana", size=15, weight="bold", slant="roman")


    
    # Значения поля
    ROW = 7
    COLUMNS = 10
    MINES = 4
    FLAGS = MINES


    # Значения для окончания игры и первого клика
    IS_GAME_OVER = False
    IS_FIRST_CLICK = True

    
    

    def __init__(self): # Инициализация

        #Двумерные списки для мин, флагов и кнопок
        self.mines_list = []
        self.flags_list = []
        self.buttons = [] 


        # Создаём поле на котором будет время и кол-во флагов
        self.canvas = tk.Canvas(MineSweeper.window, bg='#2a4008', borderwidth=0, border=0, height=100)
        self.canvas.grid(row=0, column=1, stick ='NWES')
        self.canvas2 = tk.Canvas(MineSweeper.window, borderwidth=0, border=0)
        self.canvas2.grid(row=1, column=1, stick ='NWES')



        # Текст для начала игры
        self.available_flags = tk.Label(self.canvas, text='Open one cell       ', font=self.font2, fg='red', justify='left', background='#2a4008')
        self.available_flags.grid(row=0, column=1)
        

        # Создаём кнопки, при это создав дополнительные поля вокруг основных кнопок для удобного подсчёта бомб
        for i in range(MineSweeper.ROW+2):
            temp = []
            for j in range(MineSweeper.COLUMNS+2):

                # Чередование цвета поля
                if (i+j)%2==0:
                    color=lightgreen
                else:
                    color = darkgreen

                btn = MyButton(self.canvas2, color, x=i, y=j)
                btn.config(command = lambda button=btn: self.click(button)) # Биндим кнопки на функцию
                btn.bind('<Button-3>', self.right_click) # Добавляем флажок
                temp.append(btn)

            self.buttons.append(temp)
            


    def right_click(self, event): # Функция для флажка

        # Если игра закончена то не добавляем ничего
        if MineSweeper.IS_GAME_OVER:
            return
        
        # Условие для того чтобы в начале иггры нельзя было поставить флаг так как поле мин ещё не создано
        if not MineSweeper.IS_FIRST_CLICK:
            cur_btn = event.widget

            if cur_btn['state'] == 'normal' and not len(self.flags_list)==len(self.mines_list): # Ставим флаг
                cur_btn['state'] = 'disabled' # Переключаем состояние кнопки
                cur_btn['text'] = '🚩' 
                cur_btn['disabledforeground'] = 'red'

                mixer.music.load('tick.mp3')
                mixer.music.play()

                self.flags_list.append((cur_btn.x, cur_btn.y)) # Добавляем флаг в лист флагов
                
                if sorted(self.mines_list) == sorted(self.flags_list): # Провека на победу
                    MineSweeper.IS_GAME_OVER=True
                    mixer.music.load('VI KA.mp3')
                    mixer.music.play()
                    showinfo('Victory', f'You are win\nIt took you {time} seconds!')
                    mixer.music.stop()
                    self.open_all_buttons()
                    
            elif cur_btn['text'] == '🚩': # Снимаем флаг
                cur_btn['text'] = ''
                cur_btn['state'] = 'normal'
                self.flags_list.remove((cur_btn.x, cur_btn.y))
            
            # Показываем значение оставшихся доступных флагов
            self.available_flags.config(text=f'🚩 {len(self.mines_list)-len(self.flags_list)}                      ')


    def open_all_buttons(self): # Показать все бомбы на панеле

        for i in range(1, MineSweeper.ROW+1):
            for j in range(1, MineSweeper.COLUMNS+1):
                cur_btn = self.buttons[i][j]
                color = colors.get(cur_btn.count_bomb, 'black')

                if cur_btn.is_mine:
                    cur_btn.config(text = '*', background='Green', disabledforeground='black')

                elif cur_btn.count_bomb != 0:
                    if cur_btn['bg']==darkgreen:
                        color_bg = '#e3c77f'
                    else:
                        color_bg = '#9e8c5d'
                    cur_btn.config(text=cur_btn.count_bomb, state='disabled', disabledforeground=color, relief='sunken', bg=color_bg)

                else:
                    cur_btn.config(text='')


    def click(self, clicked_button:MyButton): # Фукнция для нажатия на кнопку

        
        if MineSweeper.IS_GAME_OVER:
            return
        

        if MineSweeper.IS_FIRST_CLICK: # Если это первый клик
            self.insert_mines(clicked_button.number) # Добавляем бомбы после первого клика
            self.count_mines_in_buttons() # Подсчёт бомб вокруг каждой клетки
            self.print_buttons() # Вывод схемы бомб в консоль
            MineSweeper.IS_FIRST_CLICK = False


        self.available_flags.config(text=f'🚩 {len(self.mines_list)-len(self.flags_list)}                      ')


        if clicked_button.is_mine: # Событие для окончания игры при нажатии на бомбу

            img=tk.PhotoImage(file='bomb.png') 
            clicked_button.config(background='red', image=img, compound='center')

            MineSweeper.IS_GAME_OVER = True
            mixer.music.load('lose.mp3')
            mixer.music.play()

            # Показываем места где были бомбы
            for i in range(1, MineSweeper.ROW+1):
                for j in range(1, MineSweeper.COLUMNS+1):
                    btn = self.buttons[i][j]
                    if btn.is_mine:
                        btn.config(text='*',font=self.font2, image=img, compound='center')

            showinfo('Game Over', f'Game Over! \nDuration of the game: {time} seconds')
            
            
        else:
            
            # Получаем цвета для цифр
            color = colors.get(clicked_button.count_bomb)
            
            if clicked_button.count_bomb != 0: # Красим цифры

                if clicked_button['bg']==darkgreen:
                    color_bg = '#e3c77f'
                else:
                    color_bg = '#9e8c5d'

                clicked_button.config(text=clicked_button.count_bomb, disabledforeground=color, bg=color_bg)
                clicked_button.is_open = True

            else: # Если нажали не на бомбу, и кол-во мин вокруг этой клетки ноль, то начинаем поиск в ширину
                self.breath_first_search(clicked_button)

        # Переключаем кнопку
        clicked_button.config(state='disabled', relief=tk.SUNKEN)


    def breath_first_search(self, btn: MyButton): # Нотация что btn принадлежит MyButton
        queue = [btn]
        while queue:

            cur_btn = queue.pop() # Достаём кнопку из очереди для проверки
            color = colors.get(cur_btn.count_bomb, 'black')

            if cur_btn['text']=='🚩': # Если клетка помечена, то пропускаем ее
                continue

            if cur_btn.count_bomb != 0: # Случай если кнопка имеет бомбы вокруг

                if cur_btn['bg']==darkgreen:
                    color_bg = '#e3c77f'
                else:
                    color_bg = '#9e8c5d'
                cur_btn.config(text=cur_btn.count_bomb, disabledforeground=color, bg=color_bg)

            else: # Случай когда кнопка не имеет бомб вокруг
                if cur_btn['bg']==darkgreen:
                    color_bg = '#e3c77f'
                else:
                    color_bg = '#9e8c5d'
                cur_btn.config(text='', bg=color_bg)

            cur_btn.is_open = True # Отмечаем что клетка открыта чтобы не добавить её в очередь снова
            cur_btn.config(state='disabled', relief='sunken')

            
            if cur_btn.count_bomb==0: # Если вокруг клетки нету бомб, то проверяем соседние
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        next_btn = self.buttons[cur_btn.x+dx][cur_btn.y+dy]
                        if not next_btn.is_open and 1<=next_btn.x<=MineSweeper.ROW and \
                            1<=next_btn.y<=MineSweeper.COLUMNS and next_btn not in queue:
                            queue.append(next_btn)

         
    def reload(self): # функция для перезагрузки игры
        MineSweeper.IS_GAME_OVER = False
        global time # Выставляем счётчик времени на 0
        time = 0
        for el in self.window.winfo_children(): # Уничтожаем все виджеты
            el.destroy()
        self.__init__() # Создаём новое поле и виджеты
        self.create_widgets()
        MineSweeper.IS_FIRST_CLICK = True
         

    def create_settings_window(self): # Функция описывающая окно для изменения столбцов и строк игры

        win_settings = tk.Toplevel(self.window)
        win_settings.wm_title('Settings')

        tk.Label(win_settings, text='Number of rows: ').grid(row=0, column=0)
        tk.Label(win_settings, text='Number of columns: ').grid(row=1, column=0)
        tk.Label(win_settings, text='Number of mines: ').grid(row=2, column=0)

        row_entry = tk.Entry(win_settings)
        row_entry.insert(0, MineSweeper.ROW)
        row_entry.grid(row=0, column = 1,padx=20, pady=20)

        column_entry = tk.Entry(win_settings)
        column_entry.insert(0, MineSweeper.COLUMNS)
        column_entry.grid(row=1, column=1, padx=20, pady=20)

        mines_entry = tk.Entry(win_settings)
        mines_entry.insert(0, MineSweeper.MINES)
        mines_entry.grid(row=2, column=1, padx=20, pady=20)
        
        # Кнопка сохранения которая будет вызывать функцию изменения настроек
        save = tk.Button(win_settings, text='Save', command=lambda: self.change_settings(row_entry, column_entry, mines_entry), padx=40)
        save.grid(row=3, column=1, pady=20)


    def change_settings(self, row, column, mines): # Применение новых настроек
        
        # Если количество мин больше чем полей
        if int(mines.get()) >= int(row.get())*int(column.get()):
            showerror("Error", 'Please, write smaller number of mines!')
            return
        
        # Если введено не целое число
        try:
            int(row.get()), int(column.get()), int(mines.get())
        except ValueError:
            showerror("Error", 'Please, write a number')

        # Сохранение настроек и перезагрузка
        MineSweeper.ROW = int(row.get())
        MineSweeper.COLUMNS = int(column.get())
        MineSweeper.MINES = int(mines.get())
        MineSweeper.FLAGS = MineSweeper.MINES
        self.reload()


    def set_difficulty(self, difficult): # Устанавливаем сложность

        if difficult=='Easy':
            MineSweeper.ROW = 5
            MineSweeper.COLUMNS = 5
            MineSweeper.MINES = 5
            MineSweeper.FLAGS = 5
            self.reload()
        if difficult=='Medium':
            MineSweeper.ROW = 8
            MineSweeper.COLUMNS = 8
            MineSweeper.MINES = 13
            MineSweeper.FLAGS = 13
            self.reload()
        if difficult=='Hard':
            MineSweeper.ROW = 10
            MineSweeper.COLUMNS = 10
            MineSweeper.MINES = 35
            MineSweeper.FLAGS = 35
            self.reload()


    def rickroll(self): # Секрет :)
        mixer.music.load('NeverGonnaGiveYouUp.mp3')
        mixer.music.play()
        showinfo('Capibara', 'Capibara')


    def create_widgets(self): # Создание кнопок и меню
        

        menubar = tk.Menu(self.window) # создаём меню
        self.window.config(menu=menubar)

        # Окно для выбора сложности игры
        difficulty = tk.Menu(menubar, tearoff=0)
        difficulty.add_command(label='Easy', command=lambda:self.set_difficulty('Easy'))
        difficulty.add_command(label='Medium',command=lambda:self.set_difficulty('Medium'))
        difficulty.add_command(label='Hard', command=lambda:self.set_difficulty('Hard'))

        # Добавляем кнопки на поле меню
        menubar.add_cascade(label='Difficulty', menu=difficulty)
        menubar.add_command(label="Restart", command=self.reload)
        menubar.add_command(label='Settings', command = self.create_settings_window)


        #  Отрисовываем кнопки
        count=1
        for i in range(1, MineSweeper.ROW+1):
            for j in range(1, MineSweeper.COLUMNS+1):
                btn = self.buttons[i][j]
                btn.number = count # Назначение номера кнопки для дальнейшего выбора мины
                btn.grid(row=i, column = j, stick ='NWES') 
                count+=1


        # Секретная кнопка посередине
        btn=tk.Button(self.canvas, font='Arial 17 bold', command=self.rickroll, justify='right', fg='black', bg='#e3c77f', borderwidth=3, relief='ridge', overrelief='groove')
        btn['text']='😎'
        btn.grid(row=0, column=2)


        # Отсчёт времени отложенной задачей
        def tick():
            if not MineSweeper.IS_GAME_OVER:
                label.after(1000, tick)
                global time
                time+=1
                label['text'] = f'                  Time: {time}'
        label = tk.Label(self.canvas,font='sans 20 bold', bg='#2a4008', justify='center', fg='#ccb12d', relief='sunken')
        label.grid(row=0, column=3)
        label.after_idle(tick)


        # Растягиваем кнопки
        for i in range(1, MineSweeper.ROW+1):
            tk.Grid.rowconfigure(self.canvas2, i, weight = 1) 

        for i in range(1, MineSweeper.COLUMNS + 1):
            tk.Grid.columnconfigure(self.canvas2, i, weight = 1)


    def start(self): # Начало игры
        self.create_widgets()
        MineSweeper.window.mainloop()


    def print_buttons(self): # Вывод схемы бомб в консоль для удобства при создании и тесте игры
        for i in range(1, MineSweeper.ROW+1):
            for j in range(1, MineSweeper.COLUMNS+1):
                btn = self.buttons[i][j]
                if btn.is_mine:
                    print('B', end='')
                else:
                    print(btn.count_bomb, end='')
            print()


    def insert_mines(self, number):  # Вставляем бомбы
        index_mines = self.get_mines_places(number) # Получаем координаты мин случайным образом исключая кнопку по которой сделали первый клик чтобы не проиграть сразу
        for i in range(1, MineSweeper.ROW+1):
            for j in range(1, MineSweeper.COLUMNS+1):
                btn = self.buttons[i][j]
                if btn.number in index_mines: # Если номер числа находится в списке координат мин, то изменяем значение
                    btn.is_mine = True
                    self.mines_list.append((btn.x, btn.y))
        print(self.mines_list)


    def count_mines_in_buttons(self): # Подсчёт бомб вокруг
        for i in range(1, MineSweeper.ROW+1):
            for j in range(1, MineSweeper.COLUMNS+1):
                btn = self.buttons[i][j]
                count_bomb=0
                if not btn.is_mine:
                    for row_dx in [-1, 0, 1]:
                        for col_dx in [-1, 0, 1]:
                            neighbour = self.buttons[i+row_dx][j+col_dx]
                            if neighbour.is_mine:
                                count_bomb+=1
                btn.count_bomb = count_bomb


    @staticmethod # Статический метод
    def get_mines_places(exclude_number): # Случайные индексы для бомбы
        indexes = list(range(1, MineSweeper.COLUMNS * MineSweeper.ROW + 1)) # Лист номеров всех кнопок
        indexes.remove(exclude_number) # Исключаем из списка первую нажатую кнопку
        shuffle(indexes) # Перемешиваем список случайным образом чтобы не было повторений
        return indexes[:MineSweeper.MINES] # Возвращаем список такой длины, сколько мин у нас должно быть создано




game = MineSweeper()
game.start()  # Запуск