# Программа формирует html-код и выводит его либо в файл (если задан соответствующий параметр в контекстном менеджере with HTML(...)) либо в консоль
class Tag:
    
    def __init__(self, tag, level = 1, is_single = False, klass=None, **kwargs):
        self.tag = tag # Имя тега HTML-документа
        self.text = "" # Текст, обёрнутый в тег (текст внутри тега)
        self.attributes = {} # Создаём пустой словарь для атрибутов тега, передаваемых через **kwargs
        self.level = level # Уровень вложенности тегов: 0 - TopLevel, 1 - первый после TopLevel, 2 - второй и т. д. По умолчанию level = 1
        self.tab = 4 # Количество отступов в коде для вложенных тегов. По умолчанию = 4 (tabindent = 4)
        self.is_single = is_single # Признак парности тегов. По умолчанию - парные (is_single = False)
        self.children = [] # Создаём пустой список для хранения тегов, являющихся дочерними для тега, передаваемого через self  
        self.entry = "" #" Тег полностью (открывающий, атрибуты, содержимое (включая вложенные теги), закрывающий)     

        if klass is not None: # Если в аргументе klass передано название класса для тега
            self.attributes["class"] = " ".join(klass) # Добавляем имена классов в словарь как значения ключа "class"
        for attr, value in kwargs.items():
            if "_" in attr:
                attr = attr.replace("_", "-") # Замена символа "_" на "-" в именах классов, названиях типов, id ... , как это принято в html
            self.attributes[attr] = value # Добавляем исправленное значение в словарь

    def __enter__(self):
        # Возвращаем объект          
        return self

    def __exit__(self, type, value, traceback):
        # Если у self есть вложенные теги (список self.children не пустой)
        if self.children:
            # Для всех вложенных тегов
            for child in self.children:
                # Добавляем каждый вложенный тег к self
                self.entry += '\n' + ' ' * self.tab * child.level + str(child)
            # Если тег парный, добавляем на следующей строке кода отступ, соответствующий уровню вложенности (child.level) и закрывающий тег
            if not self.is_single:
                self.entry += '\n' + ' ' * self.tab * self.level + "</%s>" % self.tag

                #print('\n' + ' ' * self.tab * self.level + "</%s>" % self.tag) # Для отладки
      
    def __iadd__(self, other):
        # Добавляем очередной тег к списку вложенных тегов
        self.children.append(other)
        #Для дочерних тегов (НО только для тех, у кого level > 0, то есть тех, которые созданы как with Tag(...). При создании тега как with TopLevelTag(...) level всегда = 0) увеличиваем уровень вложенности. В результате отступ в коде увеличивается на количество пробелов, равное self.tab * self.level  
        if other.level > 0:
            other.level = self.level + 1
        # Возвращаем объект  
        return self            

    def __str__(self):
    #if self.attributes:
        # Создаём пустой список для атрибутов
        attrs = []
        # Для каждой пары (ключ: значение) из словаря self.attributes.items()
        for attribute, value in self.attributes.items():
            # Добавляем к списку attrs строку ' атрибут="значение"'
            attrs.append(' %s="%s"' % (attribute, value))
        # Сцепляем между собой атрибуты в одну строку
        attrs = "".join(attrs)
        # Для одиночных (не парных) тегов
        if self.is_single:
            # Формируем тег
            self.entry = f"<{self.tag}{attrs}/>"
        # Для парных тегов
        else:
            # Формируем тег. При этом закрывающий тег в той же строке, что и открывающий, добавляется только в том случае, если у self нет потомков (вложенных тегов)
            self.entry = f"<{self.tag}{attrs}>{self.text}{self.entry}" + f"</{self.tag}>" * int(not self.children)
        # Возвращаем текстовое представление тега
        return self.entry

class TopLevelTag(Tag):

    def __init__(self, tag, **kwargs):
        # Инициализируем объект при помощи метода __init__ родительского класса Tag, указывая принудительно нулевой уровень вложенности level = 0 (без отступов)        
        Tag.__init__(self, tag, level = 0, **kwargs)

    def __exit__(self, type, value, traceback):
        # Для всех вложенных тегов
        for child in self.children:
            # Добавляем к тегу верхнего уровня (TopLevelTag) с переносом на новую строку каждый вложенный тег. При этом отступ добавляем только для тех, у которых уровень вложенности больше (level > 0)
            self.entry += "\n" + (" " * self.tab) * (child.level > 0) + str(child)
        # добавляем с переносом на новую строку закрывающий тег
        self.entry += "\n</%s>" % self.tag

        #print(self.entry) # Для отладки

class HTML(TopLevelTag):

    def __init__(self, output = "", **kwargs):
        # Инициализируем объект при помощи метода __init__ родительского класса Tag, указывая принудительно имя тега tag = "html" и нулевой уровень вложенности level = 0 (без отступов)
        Tag.__init__(self, tag = "html", level = 0, **kwargs)
        # Присваиваем переменной имя файла, переданное через аргумент output при создании экземпляра класса
        self.fn = output

    def __exit__(self, type, value, traceback):
        # Вызываем метод __exit__ родительского класса TopLevelTag.      
        TopLevelTag.__exit__(self, type, value, traceback)
        # Если в output передано имя файла (output != ""), производим запись сформированного HTML-документа в файл
        if self.fn:

            print(str(self)) # Для отладки. Для вывода в файл закомментируйте ЭТУ строку и раскомментируйте две следующие строки

            #with open(self.fn, "w") as f:
            #   f.write(str(self))

        # Если в output не передано имя файла (output = ""), производим вывод сформированного HTML-документа в консоль
        else:
            print(str(self))


# Образец вывода из примера на платформе:

# <html>
# <head>
#   <title>hello</title>
# </head>
# <body>
#     <h1 class="main-text">Test</h1>
#     <div class="container container-fluid" id="lead">
#         <p>another test</p>
#         <img src="/icon.png" data-image="responsive"/>
#     </div>
# </body>
# </html>


# Мы хотим написать примерно такой код (вариант из задания на платформе):

if __name__ == "__main__":
    with HTML(output="test.html") as doc:
        with TopLevelTag("head") as head:
            with Tag("title") as title:
                title.text = "hello"
                head += title
            doc += head

        with TopLevelTag("body") as body:
            with Tag("h1", klass=("main-text",)) as h1:
                h1.text = "Test"
                body += h1

            with Tag("div", klass=("container", "container-fluid"), id="lead") as div:
                with Tag("p") as paragraph:
                    paragraph.text = "another test"
                    div += paragraph

                with Tag("img", is_single=True, src="/icon.png", data_image="responsive") as img: # Я добавил запятую перед data_image (её не было в задании)
                    div += img

                body += div

            doc += body


# Этот вариант тоже работает и создаёт точно такой же html-код

# with HTML(output="test.html") as doc:
#     with TopLevelTag("head") as head:
#         doc += head        
#         with Tag("title") as title:
#             head += title
#             title.text = "hello"            


#     with TopLevelTag("body") as body:
#         doc += body        
     
#         with Tag("h1", klass=("main-text",)) as h1:
#             body += h1 
#             h1.text = "Test"


#         with Tag("div", klass=("container", "container-fluid"), id="lead") as div:
#             body += div            
#             with Tag("p") as paragraph:
#                 div += paragraph                
#                 paragraph.text = "another test"


#             with Tag("img", is_single=True, src="/icon.png", data_image="responsive") as img: # Я добавил запятую перед data_image (её не было в задании)
#                 div += img







# Мой текст. Для проверки полнофункциональности кода. Можно его раскомментировать (предварительно закомментировав код из примера)

# if __name__ == "__main__":
#     with HTML(lang="en", output = "test.html") as doc:
#         with TopLevelTag("head", klass=("ГОЛОВА",)) as head:
#             with Tag("title") as title:
#                 title.text = "hello"
#                 head += title
#             with Tag("header") as header:
#                 header.text = "Проверка"
#                 head += header
#             doc += head
#         with TopLevelTag("body", klass=("ТЕЛО",)) as body:
#             with Tag("h1", klass=("main-text",)) as h1:
#                 h1.text = "Test"
#                 body += h1
#             with Tag("div", klass=("container", "container-fluid"), id="lead") as div:
#                 with Tag("p") as paragraph:
#                     paragraph.text = "another test"
#                     div += paragraph
#                 with Tag("img", is_single=True, src="/icon.png", data_image="responsive") as img: # Я добавил запятую перед data_image (её не было в задании)
#                     div += img
#                 with Tag("intro", klass=("intro",)) as intro:
#                     intro.text = "Текст в intro"
#                     div += intro
#                     with Tag("div1", id="div1") as div1:
#                         div1.text = "div1"
#                         intro += div1
#                         with Tag("div2", id="div2") as div2:
#                             div2.text = "div2"
#                             div1 += div2  
#                             with Tag("div3", id="div3") as div3:
#                                 div3.text = "div3"
#                                 div2 += div3
#                 body += div
#             doc += body
#         with TopLevelTag("footer", klass=("НОГИ",)) as footer: 
#             with Tag("a", href="#", klass=("info",)) as a:
#                 a.text = "Пишите, звоните"
#                 footer += a
#             doc += footer

