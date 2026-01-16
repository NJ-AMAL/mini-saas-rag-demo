Mini SaaS – Démo RAG Multi-Client
=================================

Ceci est une mini-application SaaS simulant un système RAG multi-client.  
Chaque client possède son propre espace de documents et ne peut interroger que ses propres documents.  
Les réponses sont strictement limitées aux documents du client.

------------------------------------------------------------
1. Backend
------------------------------------------------------------

Prérequis :
- Python 3.12+
- Installer les dépendances :

    pip install -r requirements.txt

Démarrer le backend :

    uvicorn app:app --reload

Le backend sera accessible sur http://127.0.0.1:8000

------------------------------------------------------------
2. Frontend (Streamlit)
------------------------------------------------------------

Démarrer l’interface Streamlit :

    streamlit run ui.py

Le frontend s’ouvrira dans votre navigateur.  
Vous pourrez entrer votre clé API et poser des questions sur vos documents.

------------------------------------------------------------
3. Clés API (pour tests)
------------------------------------------------------------

Client   | Clé API
---------|---------
clientA  | tenantA_key
clientB  | tenantB_key

> Utilisez le champ "API Key" dans l’interface Streamlit. Cela simule l’en-tête `X-API-KEY`.

------------------------------------------------------------
4. Tests par client
------------------------------------------------------------

1. Saisir la clé API du client.
2. Poser une question.
3. Le système renverra des réponses **uniquement à partir des documents de ce client**.
4. Essayer une clé client sur les documents d’un autre client renverra une erreur 404.

------------------------------------------------------------
5. Notes
------------------------------------------------------------

- Le backend utilise **FAISS + SentenceTransformer** pour intégrer et rechercher dans les documents.
- Les réponses sont directement extraites des documents — aucun LLM externe n’est utilisé.
- Si un client n’a pas de documents ou si la requête ne correspond à rien, le système renvoie un message approprié.

------------------------------------------------------------
6. Méthodologie
------------------------------------------------------------

1. **Séparation des clients**  
   Chaque client est identifié par un en-tête `X-API-KEY`. Le backend associe les clés aux clients et n’accède qu’aux documents du client. Cela garantit une séparation stricte entre locataires.

2. **Récupération de documents**  
   Les documents de chaque client sont intégrés à l’aide du modèle `SentenceTransformer` (`all-MiniLM-L6-v2`) et stockés dans un index FAISS.

3. **Génération de réponses**  
   Les requêtes sont intégrées et le document le plus pertinent est récupéré.  
   > Les réponses sont strictement limitées aux documents du client.

4. **Frontend**  
   Streamlit est utilisé pour une interface simple. Les utilisateurs saisissent leur clé API et leur question ; les résultats sont renvoyés instantanément.

5. **Pas de LLM externe**  
   Pour rester gratuit, aucune clé OpenAI n’est nécessaire. Le système fonctionne entièrement hors ligne, produisant des réponses strictement à partir des documents.

------------------------------------------------------------
Structure des dossiers
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
