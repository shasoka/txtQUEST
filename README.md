# **Командный проект. Текстовый КВЕСТ :joystick:**

![](https://img.shields.io/github/watchers/shasoka/prac_6?style=social)
![](https://img.shields.io/github/stars/shasoka/txtrpg?style=social)
![](https://img.shields.io/github/forks/shasoka/txtrpg?style=social)
![](https://sun9-33.userapi.com/impg/qdGjdhrG1rhLv02cTp6t5d-knroo7XH7-wMptA/LRzrBPH5oPc.jpg?size=874x366&quality=96&sign=b05482426147994f6c295c02cc5cfbf8&type=album)

## **1. Структура проекта**

:file_folder: Техническая составляющая проекта содержит три пакета: ```AI```, ```TUI``` и ```MAP (генератор карты)```.  Точка входа находится в модуле ```__main__.py``` пакета ```TUI``` (на самом деле это не совсем так; точка входа, которая должна начинаться с ```if __name__ == '__main__'``` нужна лишь для запуска ```.bat```, как альтернативный вариант запуска; в релизной версии точкой входа является функция ```main()```, которая вызывается из модуля ```__main__.py``` при запуске игры из ```CMD``` по команде).

```
----...\
    |
    |----MAP\  # Генератор карты
    |    |----AI\  # Генератор описаний (нейронная сеть)
    |    |    |----__init__.py
    |    |    |----text_generator.py
    |    |    |----data    
    |    |    |    |----char_to_idx.pickle
    |    |    |    |----entire_model.pt
    |    |    |    |----idx_to_char.pickle
    |    |    |    |----text.txt
    |	 |----__init__.py
    |    |----map_generator.py
    |    |----data
    |    |    |----map.json
    |
    |----TUI\  # Текстовый пользовательский интерфейс
    |    |----saves\
    |    |    |----.gitkeep
    |    |----data\
    |    |    |----helpstr.json
    |    |    |----intro.json
    |    |    |----intro.jpg
    |    |    |----lose.jpg
    |    |    |----outro.jpg
    |    |----__init__.py
    |    |----__main__.py  # Точка входа
    |    |----intro.py
    |    |----lose.py
    |    |----main_hero_class.py
    |    |----map_output.py
    |    |----outro.py
    |    |----quests.py
    |    |----words.py
    |
    |----setup.py  # Модуль для сборки и установки проекта
    |----run.bat # Запуск игры
```
## **2. Об этой игре**

:game_die: Текстовая РПГ по мотивам мастера ужасов Говарда Лавкрафта :skull:

### **Сюжет**

:closed_book: Игровой сюжет основывается на произведении «Храм» (первая публикация - сентябрь 1925 года):
> *Во время подъема на поверхность экипаж немецкой подводной лодки обнаружил на палубе труп неизвестного молодого человека, в руке которого была зажата статуэтка. Когда моряки попытались забрать ее, один из боцманов заметил, что мертвый юноша на мгновение открыл глаза и ухмыльнулся. После этого странного случая на борту стали происходить необъяснимые вещи: несколько матросов бесследно исчезли, а остальные начали сходить с ума от приступов панического страха и галлюцинаций . . .*

Это атмосферная, стильная, жуткая и затягивающая история, после которой в Вас точно проснется желание погрузиться в мир мистики и ужасов Лавкрафта :ocean:

После прохождения пролога, персонаж попадает в таинственный ХРАМ, но о том, что произойдет дальше Вам предстоит выяснить самим...

:closed_book: Прочесть произведение Вы можете [здесь](http://www.lib.ru/INOFANT/LAWKRAFT/hram.txt) (время прочтения ~30 минут).

### **Механики**

#### **:game_die: 1. Рассудок**
Основная характеристика персонажа. Очень важный аспект игры. При перемещении по ХРАМУ с некоторым шансом шкала в нижней части экрана может понизиться. Чем ниже рассудок, тем выше шанс попасть в неприятности. Ужасный головные боли и голоса будут препятствовать Вашим исследованиям. Будьте бдительны.

#### **:grey_question: 2. Активности**
Способ повышения уровня рассудка. При низком уровне рассудка с шансом в 10% Вы можете встретить мини-игру, результат которой либо повысит заветную шкалу, либо понизит ее. Все в Ваших руках.

#### **:cyclone: 3. Сюжетная линия**
В некоторых локациях Вы можете наткнуться на квесты, движущие вас по сюжету. Состояние текущего квеста всегда видно в соответствующем баре.
>*На момент релиза проекта сюжетная линия представлена несколькими небольшими задачами. Возможно, игра будет наполняться контентом и дальше...*

#### **:page_facing_up: 4. Самособирающаяся карта**
ХРАМ представляет собой уникальную обширную карту размером ```10x10``` клеток. Каждая новая игровая сессия - новая версия карты, которая генерируется буквально у вас под носом. Составление карты искусственным интеллектом задача не из простых, этот процесс занимает от 20 до 25 секунд. Если вдруг карта не успеет сгенерироваться, Вам будет предложен вариант прошлой карты.
>*На момент релиза проекта все ключевые предметы и квесты зафиксированы на карте и не перемешиваются.*

#### **:wrench: 5. Игровые предметы**
- #### **Люмен**
	Ваш союзник. Едва ли светящееся нечто, что помогает Вам не терять рассудок в кромешной темноте. Люмен гарантирует, что шкала рассудка не опустится ниже текущего значения. Однако, даже союзники могут предать Вас. С шансом в 15% люмен может пропасть из инвентаря. Запасайтесь светом!

- #### **Прах**
	Один из сюжетных предметов. Испол%з** №@#-_/ . . . .

- #### **Статуя** 
	Один из сюжетных предметов. Исп"льз** №>#-</ . . . .
>*Более подробно о каждом предмете Вы узнаете в процессе игры.*

#### **:file_folder: 6. Сохранения**
Доступны в главном меню. Всего имеется 5 ячеек для сохранения прогресса. Уникальных локаций довольно много и все они разбросаны случайным образом. Порой прохождение может занять у Вас довольно много времени, поэтому не лишним будет сохраниться!

## **3. Галерея скриншотов**
>*Нажимайте на изображения, чтобы разглядеть их получше.*

**Кадр из приветственного интро**
![](https://sun9-67.userapi.com/s/v1/if2/fuA4l5NgqWnZoCjvgZIumv2xOqT8MTN_7HxJtr8FN5psTlabRzNr4AvRITlGl81MdmvQiw7K2zMqjUMF0kbYGcjg.jpg?size=1894x987&quality=96&type=album)

**Главное меню**
![](https://sun9-59.userapi.com/s/v1/if2/eQHHwjmtTJRvSh37m5-HhGZln-J1hJoPPC6xm7d3gB8ddZqj9qv_BssX9n6PSUhm8_zGXVs4Gb6JuQGpgvSOemrw.jpg?size=1919x1006&quality=96&type=album)

**Игровая справка**
![](https://sun9-52.userapi.com/s/v1/if2/cqOp_gJKq5dlEAoqnWBvcid1iXybBcfh6-LQ-bXoDoh2B2GHgT3gp7uS7b_8yfCFp2i4ufKRNfpbvAclpoiV5Bxd.jpg?size=1919x1009&quality=96&type=album)

**Меню загрузки**
![](https://sun9-34.userapi.com/s/v1/if2/c0PW7bbwqbmPI7UObVGCz1MOunG1j-WWdSQ8avmKeOHCgcCRYe2on74l_AaXIX8MmZJGhFLBEsq8YAen3oubLF-0.jpg?size=1919x1007&quality=96&type=album)

**Успешное выполнение сюжетного задания**
![](https://sun9-62.userapi.com/s/v1/if2/IsNWTfVRvqSb4mu8SrBMJqbtwiCEbc0Utq7MI54Y_Ap-LR1Op_aWy-9kNHhCQvzSgSl5dDQBQWzpA2gbBAko2JRZ.jpg?size=1919x1005&quality=96&type=album)

**Мини-игра**
![](https://sun9-15.userapi.com/s/v1/if2/LeVk_4z4leHQ68GgsyhB3_sT4CsA4Ci9hjgYH0uyrzSorTTP-inCYZsjsCdKFLUyzUrSk25QIt5xuYZsz9aXFTcK.jpg?size=1919x1008&quality=96&type=album)

**Встреча с новым предметом**
![](https://sun1.megafon-irkutsk.userapi.com/s/v1/if2/tYZMPwhttxF2Wkvr65_9ydY_SBjHwdVXEWD-VkeiWli9qD4bMIxIWSINyoVnSvXpUKDFC_ILrbCPVWXxpWX6jEOj.jpg?size=1919x1004&quality=96&type=album)

**Поражение**
![](https://sun9-29.userapi.com/s/v1/if2/rRWtMOp9SaDiGWRwioL0TfFFMl8kLlc3OEb_N3XTGC2Ss00C_KBT6TPJ4YAw0VS64vL9qpEfH-6v9IbCNl228MMT.jpg?size=1919x1003&quality=96&type=album)

**Кадр из аутро в случае проигрыша**
![](https://sun2.megafon-irkutsk.userapi.com/s/v1/if2/vnRuopQo7xJ4Z9jpmcMQ0BORMfGPC8ljycTGp-yjjeIA6Kmv7cCPZgSwgT4_uYW4r_gjuqTJfsGVzBIl4NOWflgG.jpg?size=1890x979&quality=96&type=album)

## **4. Почему ХРАМ?**
Вы когда-нибудь видели что-то подобное? Нет, даже не так... Вы когда-нибудь видели полноценную игру с TUI в CMD Windows, да еще и с нейронной сетью, генерирующей описания локаций!? Мы сомневаемся в этом.

Однозначно ХРАМ стоит Вашего внимания. 

**Увидеть это собственными глазами и потргать собственными руками такой интересный продукт - очень крутой опыт!**

## **5. Что говорят кураторы**
### **Никита Евгеньевич**
> Блин, круто! Очень круто. Прекрасно.
### **Павел Викторович**
> Неплохо-неплохо. :godmode:
### **Дмитрий Скоробогатов**
> Я ЖДАЛ ХРАМ ДВА ГОДА! :rage1:

## **6. Системные требования и установка**
**:computer: Кратко о системных требованиях**: ХРАМ не требователен к ресурам. Игра запуститься на любом компьютере под управлением Windows с установленным [Python](https://www.python.org/downloads/release/python-3104/) (>= 3.7), если следовать нашей простой инструкции. :trollface:

**:computer: Установка.** Игра выгружена на сервер [PyPi.org](https://pypi.org/project/TEMPLECMD/#files) (ссылка ведет на страницу загрузки архива пакета).

> ***Убедитесь, что Python добавлен в PATH!***

### **1. Устновка через ```CMD```.**

1. Вы можете загрузить пакет архивом ```.tar.gz``` и установить его при помощи ```pip```: 

```
> pip install ~/TEMPLECMD-1.0.tar.gz
```
2. Или же установить пакет без загрузки из терминала, если Вам, конечно, так удобнее:
```
> pip install TEMPLECMD
```
3. Команда ```pip install``` помимо игры установит и все необходимые зависимости.

> ***ВАЖНО:*** Вышеупомянутый ```pip install``` не установит один важный форк библиотеки ```npyscreen```, который обеспечивает корректную работу этой библиотеки на ```Windows```, поэтому, вслед за установкой пакета установите и форк, находящийся по адресу <https://github.com/shasoka/npyscreen>. Для этого воспользуйтесь командной:
```
> pip install git+https://github.com/shasoka/npyscreen
```
4. После установки для запуска игры Вам всего лишь необходимо запустить ```CMD``` в любом каталоге на вашем компьютере и:
```
> temple!
```

### **2. Запуск с помощью ```.bat``` файла**
Вы можете загрузить исходный код проекта и найти в корневой папке файл ```run.bat```. Он не устанавливает необходимых зависимостей, но запускает игру по вашему нажатию. Если Вы обладаете достаточным опытом, или если пакет не устанавливается корректно, этот способ для Вас.

Не забудьте прочесть справку перед игрой (а еще чекбокс Свойства консоли -> Терминал -> Отключить прокрутку вперед должен быть пустым :smile:)

**Готово! Добро пожаловать в ХРАМ!**

![](https://media.giphy.com/media/jKn6YLna9uF846ocGH/giphy.gif)

## **7. Разработчики**
+ **:bust_in_silhouette: Мочалов Семен. КИ21-17/1Б. (<https://vk.com/semen397>)** Ответственный за работу нейронной сети и основных игровых механик.
+ **:bust_in_silhouette: Шенберг Аркадий. КИ21-17/1Б. (<https://vk.com/shxnbxrg>)** Ответственный за текстовый интерфейс и визульную составляющую.
