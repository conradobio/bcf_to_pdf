import os
from zipfile import ZipFile
import json
import xml.dom.minidom
import logging
from tqdm import tqdm
import streamlit as st

DIRECTORY_PATH = './data/'
#BCF_FILE_NAME = 'Smart-Tarumã-Arquitetura.zip'

def replace_bcf_extension(DIRECTORY_PATH):
    for file in os.listdir(DIRECTORY_PATH):
        list_files = file.split('.')
        if len(list_files) > 1:
            if 'bcf' not in file.split('.')[1]:
                pass
            else:
                new_name = f"{file.split('.')[0]}.zip"
                os.rename(f"{DIRECTORY_PATH}{file}", f"{DIRECTORY_PATH}{new_name}")

def create_directory_extract_files(DIRECTORY_PATH, BCF_FILE_NAME):
    root_dirs = set()
    with ZipFile(f'{DIRECTORY_PATH}{BCF_FILE_NAME}', 'r') as zip:
        # save directory names inside zip
        for filename in zip.namelist():
            r_dir = filename.split('/')
            r_dir = r_dir[0]
            root_dirs.add(r_dir)
        
        # create a directory for each folder inside zip file
        for filename in zip.namelist():
            for dirs in list(root_dirs):
                path_dir = f'{DIRECTORY_PATH}{BCF_FILE_NAME.split(".")[0]}/bcf/{dirs}'
                if dirs in filename and 'bcf.version' not in filename: # and not os.path.isdir(path_dir) 
                    os.makedirs(path_dir, exist_ok=True)
                if dirs in filename and 'bcf.version' not in filename:
                    #logging.info(dirs)
                    zip.extract(filename, path_dir)

def read_extracted_files(DIRECTORY_PATH, BCF_FILE_NAME):
    file_paths = []

    for root, directories, files in os.walk(f'{DIRECTORY_PATH}{BCF_FILE_NAME.split(".")[0]}/bcf'):
        for filename in files:
            if filename.endswith('.bcf'):
                filepath = os.path.join(root, filename)
                file_paths.append(filepath)
    return file_paths

def get_xml_topic_element(xml_doc):
    topics = xml_doc.getElementsByTagName('Topic')

    for topic in topics:
        guid = topic.getAttribute('Guid')
        type = topic.getAttribute('TopicType')
        status = topic.getAttribute('TopicStatus')
        prioridade = topic.getElementsByTagName('Priority')[0].childNodes[0].data
        title = topic.getElementsByTagName('Title')[0].childNodes[0].data
        index = topic.getElementsByTagName('Index')[0].childNodes[0].data
        labels = topic.getElementsByTagName('Labels')[0].childNodes[0].data
        creationdate = topic.getElementsByTagName('CreationDate')[0].childNodes[0].data
        creationauthor = topic.getElementsByTagName('CreationAuthor')[0].childNodes[0].data
        modifieddate = topic.getElementsByTagName('ModifiedDate')[0].childNodes[0].data
        modifiedauthor = topic.getElementsByTagName('ModifiedAuthor')[0].childNodes[0].data
        try:
            duedate = topic.getElementsByTagName('DueDate')[0].childNodes[0].data
        except:
            duedate = 'sem data'
        assignedto = topic.getElementsByTagName('AssignedTo')[0].childNodes[0].data
        try:
            stage = topic.getElementsByTagName('Stage')[0].childNodes[0].data
        except:
            stage = 'sem estágio'
        try:
            description = topic.getElementsByTagName('Description')[0].childNodes[0].data
        except:
            description = 'sem descrição'

        topic_dict = {'codigo':guid, 'titulo':title, 'status':status,  
                                'descricao':description, 'tipo':type, 'fase': stage,
                                'prioridade':prioridade, 'abertura':creationdate, 'categoria': None,
                                'disciplinas_resp':labels, 'vencimento': duedate, 
                                'sub_categoria': None, 'usuarios_resp':assignedto,
                                'autor':creationauthor, 'local': None
                                }
    return topic_dict

def get_xml_images_element(xml_doc, file_path, BCF_FILE_NAME, DIRECTORY_PATH):
    images = xml_doc.getElementsByTagName('Viewpoints')

    root_path = f'{DIRECTORY_PATH}{BCF_FILE_NAME.split(".")[0]}/bcf/'
    st.write(root_path)
    #root_path = f'C:/Users/cbio/Documents/repos/autodoc/autodoc/project 10 - projetos/data/{BCF_FILE_NAME.split(".")[0]}/bcf/'
    #foto_path_1 = file_path.split('\\')[1]
    foto_path = f'{root_path}{foto_path_1}/{foto_path_1}/'

    image_dict = []
    for i, image in enumerate(images):
        guid = image.getAttribute('Guid')
        foto = image.getElementsByTagName('Snapshot')[0].childNodes[0].data
        #image_dict[f'im_{i}'] = {'guid': guid,'foto': foto}
        image_dict.append(dict(guid=guid, foto=f'{foto_path}/{foto}'))

    return image_dict

def get_xml_comments_element(xml_doc):
    comments = xml_doc.getElementsByTagName('Comment')

    comment_dict = []
    for num, comment in enumerate(comments):
        if len(comment.getAttribute('Guid')) > 1:
            guid = comment.getAttribute('Guid')
            date = comment.getElementsByTagName('Date')[0].childNodes[0].data
            autor = comment.getElementsByTagName('Author')[0].childNodes[0].data
            b = comment.getElementsByTagName('Comment')
            for i in b:
                if len(i.childNodes) > 0:
                    cmts = i.childNodes[0].data
                else:
                    cmts = 'sem comentários'
            modautor = comment.getElementsByTagName('ModifiedAuthor')[0].childNodes[0].data
            
            # comment_dict[f'com_{num}'] = {'guid':guid, 'descricao':cmts, 'data_acao':date, 
            #             'novo_autor':autor,  'realizado_por': modautor}  
            comment_dict.append(dict(guid=guid, descricao=cmts, data_acao=date, 
                    novo_autor=autor,  realizado_por= modautor))
    return comment_dict

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
    logging.info('Início Script')
    replace_bcf_extension(DIRECTORY_PATH)

    logging.info('Início extração de arquivos.')
    create_directory_extract_files(DIRECTORY_PATH, BCF_FILE_NAME)
    logging.info('Extração de arquivos finalizado.')

    file_paths = read_extracted_files(DIRECTORY_PATH, BCF_FILE_NAME)
    logging.info(f'Total arquivos bcf - {len(file_paths)}')

    for file_path in tqdm(file_paths):
        xml_doc = xml.dom.minidom.parse(file_path)
        topic_dict = get_xml_topic_element(xml_doc)
        image_dict = get_xml_images_element(xml_doc, file_path, BCF_FILE_NAME)
        comment_dict = get_xml_comments_element(xml_doc)
        topic_dict.update({'comentarios':comment_dict})
        topic_dict.update({'images':image_dict})

        json_path = f'{DIRECTORY_PATH}{BCF_FILE_NAME.split(".")[0]}/json/'
        json_file = file_path.split('\\')[1]
        if not os.path.isdir(json_path):
            os.mkdir(json_path)
        with open(f'{json_path}{json_file}.json', 'w') as f:
            json.dump(topic_dict, f, indent=4)
    