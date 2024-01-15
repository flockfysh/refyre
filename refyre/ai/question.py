from refyre.config import env

from langchain.chains import RetrievalQA
from langchain.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import TextLoader
from langchain.prompts import PromptTemplate
from langchain import HuggingFaceHub, HuggingFacePipeline
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain



#Link: https://kleiber.me/blog/2023/02/25/question-answering-using-langchain/
#https://python.langchain.com/docs/modules/model_io/models/llms/integrations/gpt4all
#https://gpt4all.io/index.html
def answer_with_context(question, context_db):


    repo_id = "Writer/palmyra-small"  # See https://huggingface.co/models?pipeline_tag=text-generation&sort=downloads for some other options
    llm = HuggingFacePipeline.from_model_id(
        model_id=repo_id,
        task="text-generation",
        model_kwargs={"temperature": 0.2, 'max_length' : max(200, len(question) * 10)},
    )
    qa_chain = load_qa_chain(llm, chain_type="stuff")
    qa = RetrievalQA(combine_documents_chain=qa_chain, retriever=context_db.as_retriever())

    return qa({'query': question}, return_only_outputs=True)
