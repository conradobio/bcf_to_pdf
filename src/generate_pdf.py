import jinja2
import json
from xhtml2pdf import pisa 
import os
import logging
from tqdm import tqdm

DIRECTORY_PATH = './data/'
BCF_FILE_NAME = 'Smart-Tarumã-Arquitetura.bcf'

templateLoader = jinja2.FileSystemLoader(searchpath="./")
templateEnv = jinja2.Environment(loader=templateLoader)
TEMPLATE_FILE = "./src/ocorrencias_report.html"
template = templateEnv.get_template(TEMPLATE_FILE)

def open_json(path_file):
    with open(f'{path_file}') as f:
        return json.load(f)

def read_json_files(DIRECTORY_PATH, BCF_FILE_NAME):
    file_paths = []

    for root, directories, files in os.walk(f'{DIRECTORY_PATH}{BCF_FILE_NAME.split(".")[0]}/json'):
        for filename in files:
            if filename.endswith('.json'):
                filepath = os.path.join(root, filename)
                file_paths.append(filepath)
    return file_paths

def convertHtmlToPdf(sourceHtml, outputFilename):
    # open output file for writing (truncated binary)
    resultFile = open(outputFilename, "w+b")

    # convert HTML to PDF
    pisaStatus = pisa.CreatePDF(
            src=sourceHtml,            # the HTML to convert
            dest=resultFile,          
            )           # file handle to receive result

    # close output file
    resultFile.close()

    # return True on success and False on errors
    print(pisaStatus.err, type(pisaStatus.err))
    return pisaStatus.err

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
    logging.info('Início Script')

    pisa.showLogging()

    pdf_path = f'{DIRECTORY_PATH}{BCF_FILE_NAME.split(".")[0]}/pdf/'
    logging.info(pdf_path)
    os.makedirs(pdf_path, exist_ok=True)

    json_paths = read_json_files(DIRECTORY_PATH)
    #logging.info(json_paths)
    logging.info(f'Total arquivos bcf - {len(json_paths)}')

    for json_path in tqdm(json_paths[:2]):
        #logging.info(json_path)
        data = open_json(json_path)
        json_file = json_path.split('\\')[1].split('.')[0]
        logging.info(json_file)

        sourceHtml = template.render(json_data=data) 
        outputFilename = f"{pdf_path}/ocorrencias_report_{json_file}.pdf"
        convertHtmlToPdf(sourceHtml, outputFilename)