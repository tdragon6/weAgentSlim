'''
    长期记忆，向量化嵌入和查询示例
    pip install chromadb
'''
from config import embed_api_base, embed_api_key, embed_model
from chromadb import EmbeddingFunction, Documents, Embeddings, PersistentClient
import requests
import random
import string
import pprint


class OpenAICompatibleEmbeddingFunction(EmbeddingFunction):
    '''
        嵌入函数占位，防止chroma使用默认的嵌入函数
    '''
    def __call__(self, input: Documents) -> Embeddings:
        return [[] for _ in input]


def init_chromadb(path, collection_name="test"):
    '''
        初始化chroma数据库
    '''
    client = PersistentClient(path)
    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=OpenAICompatibleEmbeddingFunction()
    )
    return collection


def get_embed_array(text_list):
    '''
        获取文本列表的嵌入向量 
    '''
    headers = {
        "Authorization": f"Bearer {embed_api_key}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "model": embed_model,
        "input": text_list,
    }
    
    response = requests.post(embed_api_base, headers=headers, json=payload)
    data = response.json()
    
    return [ ele['embedding'] for ele in data["data"] ]


def query_from_db(collection, query, num):
    '''
        从向量数据库中查询最相似的文本
        query为单文本字符串
        num为返回最相似的文本数量
    '''
    embed_query= get_embed_array([query])
    results = collection.query(
        query_embeddings=embed_query,
        n_results=num
    )
    return results


if __name__ == '__main__':
    characters = string.ascii_letters + string.digits

    # 初始化chroma数据库
    collection = init_chromadb('./db')
    
    # 嵌入文本
    text_list = ['Hello World!', 'Hello Python!', 'Hello Chroma!']
    embed_array = get_embed_array(text_list)
    collection.add(
        documents=text_list,
        embeddings=embed_array,
        ids= [''.join(random.choices(characters, k=16)) for i in range(len(text_list))]
    )

    # 查询最相似的文本
    query = 'Hi World!'
    results = query_from_db(collection, query, 10)

    # 打印结果
    pprint.pprint(results)

    '''
    响应预览:
    {'data': None,
    'distances': [[0.34125104546546936, 0.5618022680282593, 0.5698094367980957]],
    'documents': [['Hello World!', 'Hello Python!', 'Hello Chroma!']],
    'embeddings': None,
    'ids': [['a0fFJH9LPTuAmA57', 'u9lWT2RfzPH3DNoc', 'OfxTDvcaUWkFXQU1']],
    'included': ['metadatas', 'documents', 'distances'],
    'metadatas': [[None, None, None]],
    'uris': None}
    '''