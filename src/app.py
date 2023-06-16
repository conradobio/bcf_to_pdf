import streamlit as st
import os
from stqdm import stqdm
import xml.dom.minidom
import json
import jinja2
from xhtml2pdf import pisa 
from pypdf import PdfMerger

from main_file import create_directory_extract_files, read_extracted_files, get_xml_topic_element,get_xml_images_element, get_xml_comments_element 
from generate_pdf import open_json, read_json_files, convertHtmlToPdf

st.title('Gerador de Mapa de Ocorrências')

DIRECTORY_PATH = './app/bcf_to_pdf/tempDir/'

uploaded_file  = st.file_uploader('Selecione o arquivo com extensão .bcf')
if uploaded_file is not None:
    BCF_FILE_NAME = uploaded_file.name
    st.write(os.getcwd())

    os.makedirs(f'{DIRECTORY_PATH}', exist_ok=True)
    list_files = BCF_FILE_NAME.split('.')
    if len(list_files) > 1:
        if 'bcf' not in BCF_FILE_NAME.split('.')[1]:
            pass
        else:
            new_name = f"{BCF_FILE_NAME.split('.')[0]}.zip"

            with open(os.path.join(DIRECTORY_PATH, BCF_FILE_NAME),"wb") as f:
                f.write(uploaded_file.getbuffer())
            os.rename(f"{DIRECTORY_PATH}{BCF_FILE_NAME}", f"{DIRECTORY_PATH}{new_name}") 
            st.write(f"{DIRECTORY_PATH}{new_name}")
            st.success("Saved File")
    
    create_directory_extract_files(DIRECTORY_PATH, new_name)
    st.success('Extração de arquivos finalizado.')

    file_paths = read_extracted_files(DIRECTORY_PATH, new_name)
    st.info(f'Total arquivos bcf - {len(file_paths)}')

    st.info('Salvando arquivos com o resumo das informações em json')
    for file_path in stqdm(file_paths):
        xml_doc = xml.dom.minidom.parse(file_path)
        topic_dict = get_xml_topic_element(xml_doc)
        image_dict = get_xml_images_element(xml_doc, file_path, new_name, DIRECTORY_PATH)
        comment_dict = get_xml_comments_element(xml_doc)
        topic_dict.update({'comentarios':comment_dict})
        topic_dict.update({'images':image_dict})

        json_path = f'{DIRECTORY_PATH}{BCF_FILE_NAME.split(".")[0]}/json/'
        json_file = file_path.split('/')[6]
        if not os.path.isdir(json_path):
            os.mkdir(json_path)
        with open(f'{json_path}{json_file}.json', 'w') as f:
            json.dump(topic_dict, f, indent=4)

    st.info('Arquivos json salvos')

    templateLoader = jinja2.FileSystemLoader(searchpath="./")
    templateEnv = jinja2.Environment(loader=templateLoader)
    TEMPLATE_FILE = "./src/ocorrencias_report.html"
    template = templateEnv.get_template(TEMPLATE_FILE)
    pisa.showLogging()

    pdf_path = f'{DIRECTORY_PATH}{BCF_FILE_NAME.split(".")[0]}/pdf/'
    st.write(pdf_path)
    os.makedirs(pdf_path, exist_ok=True)

    json_paths = read_json_files(DIRECTORY_PATH, BCF_FILE_NAME)
    st.write(f'Total arquivos bcf - {len(json_paths)}')

    st.info('Salvando arquivos em pdf...')
    for json_path in stqdm(json_paths):
        data = open_json(json_path)
        st.write(json_paths)
        json_file = json_path.split('/')[6]#json_path.split('\\')[1].split('.')[0]
        st.write(json_file)

        sourceHtml = template.render(json_data=data) 
        outputFilename = f"{pdf_path}/ocorrencias_report_{json_file}.pdf"
        convertHtmlToPdf(sourceHtml, outputFilename)
    
    st.info('Juntando pdfs')
    pdf_files = []
    for root, directories, files in os.walk(f'{DIRECTORY_PATH}{BCF_FILE_NAME.split(".")[0]}/pdf'):
        for filename in files:
            pdf_files.append(f'{DIRECTORY_PATH}{BCF_FILE_NAME.split(".")[0]}/pdf/{filename}')

    merger = PdfMerger()
    for pdf in pdf_files:
        merger.append(pdf)
    
    st.write(len(pdf_files))

    merger.write(f'{DIRECTORY_PATH}{BCF_FILE_NAME.split(".")[0]}/result.pdf')
    st.success('Arquivo Montado com Sucesso')

    with open(f'{DIRECTORY_PATH}{BCF_FILE_NAME.split(".")[0]}/result.pdf') as f:
        st.download_button('Download PDF Ocorrências', f)