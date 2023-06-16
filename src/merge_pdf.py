from pypdf import PdfMerger
import os

pdf_files = []
for root, directories, files in os.walk('../data/Smart-Tarumã-Arquitetura/pdf'):
    for filename in files:
        pdf_files.append(f'../data/Smart-Tarumã-Arquitetura/pdf/{filename}')

merger = PdfMerger()

for pdf in pdf_files:
    merger.append(pdf)

merger.write("../data/Smart-Tarumã-Arquitetura/result.pdf")
