Mini SaaS – Multi-Client RAG Demo
=================================

This is a mini SaaS application simulating a multi-client RAG system. 
Each client has their own document space and can only query their own documents. 
Answers are strictly limited to the client’s documents.

------------------------------------------------------------
1. Backend
------------------------------------------------------------

Requirements:
- Python 3.12+
- Install dependencies:

    pip install -r requirements.txt

Start the backend:

    uvicorn app:app --reload

The backend will run on http://127.0.0.1:8000

------------------------------------------------------------
2. Frontend (Streamlit)
------------------------------------------------------------

Start the Streamlit interface:

    streamlit run ui.py

The frontend will open in your browser. You can enter your API key 
and ask questions about your documents.

------------------------------------------------------------
3. API Keys (for testing)
------------------------------------------------------------

Client   | API Key
---------|---------
clientA  | tenantA_key
clientB  | tenantB_key

> Use the "API Key" field in the Streamlit UI. This simulates the `X-API-KEY` header.

------------------------------------------------------------
4. Testing per client
------------------------------------------------------------

1. Enter the API Key for the client.
2. Ask a question.
3. The system will return answers **only from that client’s documents**.
4. Trying a client key on the other client’s documents will return a 404 error.

------------------------------------------------------------
5. Notes
------------------------------------------------------------

- The backend uses **FAISS + SentenceTransformer** to embed and search documents.
- Answers are directly retrieved from documents — no external LLM is used.
- If a client has no documents or the query matches nothing, the system returns an appropriate message.

------------------------------------------------------------
6. Approach
------------------------------------------------------------

1. **Client Separation**  
   Each client is identified by an `X-API-KEY` header. The backend maps keys to clients and only accesses the client’s documents. This ensures strict multi-tenant separation.

2. **Document Retrieval**  
   Each client’s documents are embedded using the `SentenceTransformer` model (`all-MiniLM-L6-v2`) and stored in a FAISS index.  

3. **Answer Generation**  
   Queries are embedded and the top matching document is retrieved.  
   > Answers are limited strictly to the client’s documents.  

4. **Frontend**  
   Streamlit is used for a simple UI. Users input their API key and question; results are returned instantly.  

5. **No External LLM**  
   To stay free, no OpenAI key is required. The system is fully offline, producing answers strictly from documents.

------------------------------------------------------------
Folder Structure
------------------------------------------------------------

TestPython/
│
├─ app.py
├─ ui.py
├─ requirements.txt
├─ README.txt
└─ data/
   ├─ clientA/
   │   ├─ docA1_procedure_resiliation.txt
   │   └─ docA2_produit_rc_pro_a.txt
   └─ clientB/
       ├─ docB1_procedure_sinistre.txt
       └─ docB2_produit_rc_pro_b.txt
