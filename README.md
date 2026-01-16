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


Modèle utilisé et raisons des mauvaises réponses
1️⃣ Modèle utilisé dans le projet

Dans ce projet, nous avons initialement utilisé le modèle :

EleutherAI / GPT-Neo 125M

Caractéristiques du modèle

Modèle open-source

Environ 125 millions de paramètres

Taille ≈ 500 MB

Modèle de génération de texte brute (language model)

Non instruction-tuned (pas entraîné pour suivre des consignes)

👉 Ce modèle est conçu pour continuer un texte, pas pour répondre correctement à des questions.

2️⃣ Comment fonctionne notre système RAG

Notre système est basé sur une architecture RAG (Retrieval-Augmented Generation) :

Étape 1 – Retrieval (recherche)

Les documents clients sont chargés depuis des fichiers .txt

Ils sont transformés en vecteurs via TF-IDF

La similarité entre la question et les documents est calculée avec cosine similarity

Le document le plus pertinent est sélectionné

✅ Cette partie fonctionne correctement

Étape 2 – Generation (génération de réponse)

Le document trouvé est injecté dans un prompt

Le modèle GPT-Neo génère une réponse à partir de ce contexte

❌ C’est ici que le problème apparaît

3️⃣ Pourquoi le modèle répond mal
🔴 1. Modèle trop petit

GPT-Neo 125M est :

Trop limité en capacité

Incapable de comprendre des consignes complexes

Mauvais pour le raisonnement et l’extraction d’information

🔴 2. Pas entraîné pour répondre à des questions

Le modèle :

N’a pas été entraîné avec des prompts du type
“Réponds à la question à partir du document”

Ne sait pas qu’il doit extraire une information précise

Peut produire des réponses aléatoires comme :

« Pourquoi ? »

des phrases incomplètes

du texte sans rapport

🔴 3. Hallucinations

Le modèle peut :

Inventer une réponse

Ignorer le contenu réel du document

Générer du texte qui semble cohérent mais est faux

C’est un problème classique avec les LLM non contrôlés.

4️⃣ Pourquoi ce problème est critique dans un contexte SaaS / métier

Dans un contexte professionnel (assurance, procédures, contrats) :

❌ Une réponse inventée est inacceptable

❌ Une mauvaise information peut avoir un impact légal

❌ La fiabilité est plus importante que la créativité

5️⃣ Solution adoptée
✅ Suppression de la génération LLM

Au lieu de demander au modèle de reformuler :

👉 Le système renvoie directement le passage du document le plus pertinent

Avantages

✅ Réponses 100% factuelles

✅ Basées uniquement sur les documents clients

✅ Zéro hallucination

✅ Plus rapide et plus stable

✅ Adapté à un vrai usage SaaS