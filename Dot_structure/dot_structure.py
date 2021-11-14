import os
import io
import re
import graphviz


def list_files_dot(startpath, rankdir, desc):
    """ Метод для создания dot файла: построение nodes и edges по всем папкам, файлам, классам

    Args:
        startpath: стартовый путь
        rankdir: направление графа
        desc (bool): флаг включения описания
    Returns:
        Digraph object
    """

    dot = graphviz.Digraph(comment='')

    # Создание легенды
    create_legend(dot)

    dot.graph_attr['rankdir'] = rankdir
    dot.graph_attr['rank'] = 'min'
    for root, dirs, files in os.walk(startpath):
        if '__' in os.path.basename(root):
            continue
        # Получаем отнсительный путь
        root_path = os.path.relpath(root, start=startpath)
        # Поправка для корректного определения узла
        if root_path == '.':
            root_path = ''
        # Добавление корневой папки в качестве узла с описанием из init файла
        root_description = create_folder_description(root, desc)
        dot.node(root_path, root_description, shape='none')

        # Проход по папкам в корневой папке для создания узлов и связей
        for dir_name in dirs:
            if '__' in dir_name:
                continue
            dir_path = os.path.join(root_path, dir_name)
            dir_description = create_folder_description(os.path.join(root, dir_name), desc)
            dot.node(dir_path, dir_description, shape='none')
            dot.edge(root_path, dir_path)

        # Проход по файлам в корневой папке для создания узлов и связей
        for file_name in files:
            if '__' in file_name:
                continue
            file_path = os.path.join(root_path, file_name)
            dot.node(file_path, file_name, shape='box', style='filled', fillcolor='#A6DDF3')
            dot.edge(root_path, file_path)

            # Проход по классам внутри файла для создания узла в виде таблицы
            class_descriptions = search_classes(os.path.join(root, file_name), desc)
            node_string = ''
            node_string += '<<TABLE BORDER = "0" CELLBORDER = "1" CELLSPACING = "0">'
            for class_ in class_descriptions:
                node_string += f'<TR><TD>{class_descriptions[class_]}</TD></TR>'
            node_string += '</TABLE>>'
            if class_descriptions:
                dot.node(os.path.join(file_path, 'class'), label=node_string, shape='none', fillcolor='#F99973',
                         style='filled')
                dot.edge(file_path, os.path.join(file_path, 'class'))
    return dot


def create_folder_description(root, desc):
    """ Метод создания описания папки по вложенному файлу __init__.py

    Args:
        root: путь папки
        desc (bool): флаг включения описания
    Returns:
        folder_description: строку описание папки
    """

    folder_description = os.path.basename(root)
    if not desc:
        return folder_description
    init_file = f'{root}\__init__.py'
    if not os.path.isfile(init_file):
        return folder_description
    with io.open(init_file, encoding='utf-8') as ifile:
        reading_file = ifile.readlines()
        for line in reading_file:
            if 'def ' in line or 'class ' in line:
                break
            init_desc = re.search(r'"""(.*)', line)
            if init_desc is not None:
                folder_full_desc='<<TABLE BORDER = "1" CELLBORDER = "0" CELLSPACING = "0">' +\
                                 f'<TR><TD BGCOLOR="#E9D2A0">{folder_description}'
                init_desc = init_desc.group(1).replace('"""', '')
                folder_full_desc += '<BR/>'
                folder_full_desc += f'<FONT POINT-SIZE="12">{init_desc}</FONT></TD></TR></TABLE>>'
    return folder_full_desc


def search_classes(current_file, desc):
    """ Метод поиска всех классов в файле

    Args:
        current_file: файл, в котором производится поиск классов
        desc (bool): флаг включения описания
    Returns:
        class_desc: словарь, ключи - названия классов, значения - их описание
    """

    with io.open(current_file, encoding='utf-8') as ifile:
        reading_file = ifile.read()
        classes = re.findall(r'\bclass\b .*:', reading_file)
        class_desc = {}
        for class_ in classes:
            class_name = class_.replace(':', '')
            class_desc[class_name] = create_class_description(reading_file, class_, desc)
        return class_desc


def create_class_description(reading_file, class_, desc):
    """ Метод создания описания класса по doc в нем

    Args:
        reading_file: прочитанный файл
        class_: название класса
        desc (bool): флаг включения описания
    Returns:
        class_description: строка описание класса
    """

    class_description = '<B>' + class_.replace(':', '') + '</B>'
    if not desc:
        return class_description
    class_name = re.search(r'class [^(:]*', class_)
    necessary_string = re.compile(rf'{class_name.group(0)}[^\s]*:\s*"""(.*)')
    class_desc = re.search(necessary_string, reading_file)
    if class_desc is not None:
        class_description += '<BR/>'
        class_description += '<FONT POINT-SIZE="12">'+class_desc.group(1).replace('"""', "")+'</FONT>'
        return class_description
    return class_description


def create_legend(dot):
    """ Метод создания легенды

    Args:
        dot: объект Digraph
    Returns:
        class_description: строка описание класса
    """

    with dot.subgraph(name='cluster') as legend:
        legend.attr(rank='min')
        legend.attr(label='<<B>ЛЕГЕНДА</B>>')
        legend.node('folder',
                    '<<TABLE BORDER = "1" CELLBORDER = "0" CELLSPACING = "0">' +\
                    '<TR><TD BGCOLOR="#E9D2A0">папка<BR/><FONT POINT-SIZE="12">Описание папки</FONT></TD></TR></TABLE>>',
                    shape='none')
        legend.node('file', 'название_файла.py', shape='box', style='filled', fillcolor='#A6DDF3')
        legend.node('class_', 'class Название_класса(Родительский_класс)', shape='box', style='filled',
                    fillcolor='#F99973')
        legend.node('class_',
                    label='<<TABLE BORDER = "0" CELLBORDER = "1" CELLSPACING = "0">' +\
                          '<TR><TD><B>class НазваниеКласса(РодительскийКласс)</B><BR/>' +\
                          '<FONT POINT-SIZE="12">Описание класса (может отсутствовать)</FONT></TD></TR></TABLE>>',
                    shape='none', fillcolor='#F99973',
                    style='filled')

        legend.edge('folder', 'file')
        legend.edge('file', 'class_')

    create_invisible_subcluster(dot)


def create_invisible_subcluster(dot):
    """ Метод создания пустого сабкластера (своего рода костыль для создания пространства между графом и легендой)

    Args:
        dot: объект Digraph
    """
    with dot.subgraph(name='cluster_2') as invisible_cluster:

        invisible_cluster.attr(label='<<B>НЕ СМОТРИ</B>>', fontcolor='white')
        invisible_cluster.attr(color='white')
        invisible_cluster.node('invisible_node', 'СЮДА', shape='box', style='filled', fillcolor='white',
                               fontcolor='white', color='white')


if __name__ == '__main__':
    dot = list_files_dot(r'C:\Users\dengina_e\Documents\Projects\Equipment\commutators\commutators', 'LR', desc=True)
    dot.save('Commutators', r'C:\Users\dengina_e\Documents\Projects\WorkFlow_structure')
    dot.render(format='svg')
