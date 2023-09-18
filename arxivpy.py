import subprocess
import sys
from os import path, mkdir
import logging

import arxiv

logger = logging.getLogger(__file__)
logger.setLevel(logging.WARNING)

# TODO logging

arg = sys.argv[1]

DEFAULT_BIB_PATH = path.join(path.dirname(__file__), "references.bib")
DEFAULT_PDF_PATH = path.join(path.dirname(__file__), "pdfs")

try:
    mkdir(DEFAULT_PDF_PATH)
except FileExistsError:
    pass

try:
    with open(DEFAULT_BIB_PATH, "r") as f:
        data = f.read()
except FileNotFoundError:
    with open(DEFAULT_BIB_PATH, "a") as f:
        f.write("")



def main(id):

    search = arxiv.Search(
        id_list=[id],
        sort_by=arxiv.SortCriterion.LastUpdatedDate,
        sort_order=arxiv.SortOrder.Ascending,
    )
    result = next(search.results())
    identifier = result.entry_id.rsplit("/")[-1]

    proc = subprocess.run(["arxiv2bib", identifier], capture_output=True)
    if not proc.returncode == 0:
        raise ValueError(f"Identifier {id} has not yielded a publication.")

    with open(DEFAULT_BIB_PATH, "r") as f:
        if identifier in f.read():
            print("Reference has already been added to bibtex file.")
            add = False
        else:
            print("Reference not found, adding to list.")
            add = True

    if add:
        with open(DEFAULT_BIB_PATH, "ba") as f:
            f.write(proc.stdout)

    filename = identifier+".pdf"

    if not path.isfile(path.join(DEFAULT_PDF_PATH, filename)):
        result.download_pdf(
            dirpath=DEFAULT_PDF_PATH,
            filename=filename,
        )
    else:
        logger.info("File has been downloaded previously")

if __name__ == "__main__":
    main(arg)
