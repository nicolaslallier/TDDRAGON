# Documentation – Plateforme v0.3.0 (Nginx + PostgreSQL + Time Series Logs + UI de consultation)

- **Nom du système** : (à définir) – Plateforme applicative  
- **Version** : `v0.3.0`  
- **Baseline** :  
  - **v0.1.0** : Nginx + Application + PostgreSQL (socle minimal).  
  - **v0.2.0** : Logs Nginx (accès + uptime) historisés dans des tables time series PostgreSQL (`nginx_access_logs_ts`, `nginx_uptime_ts`).  
- **Nouveauté v0.3.0** :  
  - Interface utilisateur (UI) pour **interroger les tables de logs** et visualiser les résultats.

---

## 0. Hypothèses (Assumptions)

1. Les tables time series `nginx_access_logs_ts` et `nginx_uptime_ts` sont déjà en production (v0.2.0).  
2. L’interface de consultation sera :
   - soit intégrée à l’application existante,  
   - soit sous forme de petit module web dédié (interne).  
3. L’UI est destinée à des **utilisateurs internes** (Ops, Dev, QA…) – aucun accès client externe.  
4. L’authentification et le contrôle d’accès sont gérés par un mécanisme existant ou basique (login/mot de passe, SSO simple, etc. – détail à préciser).  
5. L’UI n’est pas un outil de BI complet, mais un **outil de consultation et filtrage** pour diagnostic rapide.

---

## 1. Contexte & Objectifs (Context & Goals) – v0.3.0

### 1.1 Contexte

- Les logs Nginx sont désormais stockés dans PostgreSQL (v0.2.0).  
- Les équipes doivent actuellement passer par des **requêtes SQL** pour analyser les logs (peu accessible aux profils non techniques).  
- Besoin d’une **interface simple** pour :
  - Filtrer par période, code HTTP, URI.  
  - Visualiser les logs et les mesures d’uptime.  
  - Exporter au besoin un sous-ensemble de résultats.

### 1.2 Problème

- L’accès direct à la BD est :
  - Réservé aux profils techniques (SQL).  
  - Potentiellement risqué (requêtes lourdes, erreurs de manipulation).  
- Il est difficile pour les Ops / QA / support de :
  - **Diagnostiquer rapidement** un incident.  
  - Visualiser les **pannes / périodes DOWN**.  

### 1.3 Objectifs v0.3.0

- Mettre à disposition une **UI de consultation** des logs :  
  - Accessible via Nginx (portail interne).  
  - Simple, filtrable, paginée.  
- Permettre aux utilisateurs internes de :  
  - Rechercher des logs sur une période donnée.  
  - Filtrer les résultats (code HTTP, URI, IP, statut uptime).  
  - Télécharger les résultats (CSV ou autre format simple).  

### 1.4 Périmètre v0.3.0

**Inclus (In Scope)**

- UI web (interface interne) pour interroger :
  - `nginx_access_logs_ts`.  
  - `nginx_uptime_ts`.  
- Fonctions de filtrage basiques :
  - Période temporelle.  
  - Code HTTP / statut.  
  - URI, IP (pour les access logs).  
- Pagination, tri simple, export de résultats.  

**Exclus (Out of Scope)**

- Dashboards avancés (graphiques complexes, heatmaps, etc.).  
- Alerting et notifications automatiques.  
- Gestion fine des rôles et permissions (RBAC avancé) – v0.3.0 se limite à un **niveau d’accès interne simple**.

---

## 2. Parties prenantes / Stakeholders – v0.3.0

En plus de celles déjà identifiées en v0.1.0–0.2.0 :

- **Ops / SRE** : utilise l’UI pour diagnostiquer des incidents.  
- **Support / Helpdesk** : peut utiliser l’UI pour vérifier des requêtes utilisateurs (ex. “j’ai eu une erreur 500 à 14h10”).  
- **QA / Testeurs** : valide que les scénarios de test génèrent les logs attendus.  
- **Développeurs** : utilisent l’UI pour vérifier les comportements de l’application en environnement de test.

---

## 3. Processus & Scénarios (BPMN-like)

### 3.1 Processus principal – Consultation des logs d’accès

> Start → Utilisateur se connecte à l’UI → Sélectionne les critères → L’UI interroge la BD → Affiche les résultats → (Optionnel) Export des résultats → End

**Étapes**

1. **Start** – L’utilisateur interne accède à l’UI de consultation via une URL interne (ex. `https://app.example.com/logs`).  
2. L’utilisateur s’authentifie si requis (login, SSO…).  
3. L’utilisateur sélectionne :
   - Intervalle de temps (date/heure début–fin).  
   - Facultatif : code HTTP, URI, IP client.  
4. L’UI envoie une requête à l’API backend pour interroger `nginx_access_logs_ts`.  
5. Le backend exécute la requête SQL avec pagination (limit/offset ou équivalent).  
6. Le backend renvoie la page de résultats (liste de logs).  
7. L’UI affiche les logs dans un tableau (timestamp, méthode, URI, code, IP…).  
8. Optionnel : l’utilisateur demande un **export** (CSV) des résultats filtrés.  
9. **End** – L’utilisateur a les informations nécessaires pour son diagnostic.

### 3.2 Processus – Consultation de l’uptime

> Start → Utilisateur ouvre l’onglet Uptime → Choisit la période → L’UI interroge `nginx_uptime_ts` → Affiche liste ou résumé → End

---

## 4. Exigences fonctionnelles (Functional Requirements) – v0.3.0

> Numérotation **FR-3XX**

### 4.1 UI – Accès général

- **FR-301** – Le système doit fournir une interface web accessible via Nginx pour consulter les logs Nginx stockés en base de données.  
- **FR-302** – L’accès à l’UI doit être **restreint aux utilisateurs internes autorisés** (un mécanisme d’authentification minimal doit être en place).  

### 4.2 UI – Consultation des logs d’accès

- **FR-303** – L’UI doit permettre de sélectionner un **intervalle de temps** (date et heure de début et de fin) pour filtrer les enregistrements de `nginx_access_logs_ts`.  
- **FR-304** – L’UI doit permettre de filtrer les logs par **code HTTP** (par exemple, tous les 5xx, ou un code spécifique).  
- **FR-305** – L’UI doit permettre de filtrer par **URI / path** (recherche par préfixe ou sous-chaîne, ex. `/api/claims`).  
- **FR-306** – L’UI doit permettre de filtrer par **adresse IP client**.  
- **FR-307** – Les logs sélectionnés doivent être présentés dans un **tableau paginé** contenant au minimum :
  - Timestamp.  
  - IP client.  
  - Méthode HTTP.  
  - URI.  
  - Code HTTP.  
  - Temps de réponse (si disponible).  

- **FR-308** – L’utilisateur doit pouvoir **trier** les résultats par au moins :
  - Timestamp.  
  - Code HTTP.  

### 4.3 UI – Consultation de l’uptime

- **FR-309** – L’UI doit proposer une section dédiée à la consultation de l’uptime, basée sur la table `nginx_uptime_ts`.  
- **FR-310** – L’UI doit permettre de sélectionner une **période d’analyse** (ex. dernières 24h, 7 jours, période personnalisée).  
- **FR-311** – L’UI doit afficher :
  - La liste des mesures UP/DOWN sur la période.  
  - Un **résumé** (ex. pourcentage d’uptime sur la période sélectionnée).  

### 4.4 Export des résultats

- **FR-312** – L’UI doit permettre d’exporter au minimum les **logs d’accès filtrés** au format CSV (ou équivalent) pour un usage externe (analyse plus poussée, partage).  
- **FR-313** – L’export doit respecter les filtres actifs (période, code HTTP, URI, IP).  

### 4.5 Gestion des erreurs et feedback

- **FR-314** – En cas de requête trop volumineuse ou d’erreur BD, l’UI doit afficher un **message d’erreur clair** sans exposer de détails techniques sensibles.  
- **FR-315** – L’UI doit indiquer lorsque aucun résultat n’est trouvé (ex. message “Aucun log trouvé pour ces critères”).  

---

## 5. Exigences non fonctionnelles (NFRs) – v0.3.0

> Numérotation **NFR-3XX**

### 5.1 Performance & UX

- **NFR-301** – Le temps de réponse de la consultation (affichage d’une page de résultats paginés) doit être **≤ 3 secondes** pour une plage de 24h sur un volume normal de logs.  
- **NFR-302** – La pagination doit limiter le nombre de lignes retournées par requête (ex. 50–100 lignes par page) pour éviter les temps de réponse excessifs.  

### 5.2 Sécurité

- **NFR-303** – L’UI de consultation ne doit être accessible que depuis le **réseau interne** ou via VPN (aucune exposition publique).  
- **NFR-304** – Les utilisateurs doivent être authentifiés et autorisés avant d’accéder aux données de logs.  
- **NFR-305** – Les logs de la BD ne doivent pas pouvoir être modifiés via l’UI (lecture seule).  

### 5.3 Disponibilité & Maintenabilité

- **NFR-306** – Les erreurs d’UI et d’API liées à la consultation doivent être journalisées pour permettre le diagnostic par les équipes techniques.  
- **NFR-307** – Le code de l’UI doit être structuré pour permettre l’ajout futur de nouveaux filtres ou de nouveaux types de logs (extensibilité).  

---

## 6. Règles d’affaires / Règles techniques (BR) – v0.3.0

> Numérotation **BR-3XX**

- **BR-301** – Les requêtes SQL générées par l’interface doivent obligatoirement appliquer un **intervalle de temps** (pas de requête “full history” sans filtre de période).  
- **BR-302** – L’interface ne doit pas permettre l’exécution de requêtes SQL arbitraires (pas de “console SQL” ouverte).  
- **BR-303** – La consultation doit se faire uniquement en **lecture** sur les tables `nginx_access_logs_ts` et `nginx_uptime_ts` (aucun UPDATE/DELETE via l’UI).  
- **BR-304** – Les timestamps doivent être présentés à l’utilisateur dans le **fuseau horaire local** prévu (ex. Amérique/Toronto), même s’ils sont stockés en UTC en base.  

---

## 7. Données & Modèle d’information – Vue UI

L’UI repose sur les tables existantes **v0.2.0** :

- `nginx_access_logs_ts`  
- `nginx_uptime_ts`  

Optionnellement, l’implémentation peut introduire des **vues SQL** pour simplifier les requêtes UI (ex. `vw_nginx_access_logs_ui`, `vw_nginx_uptime_ui`), mais au niveau fonctionnel les champs restent ceux déjà définis.

---

## 8. Cas de tests d’acceptation (Acceptance Criteria) – v0.3.0

> Numérotation **AT-3XX**

### 8.1 Test – Filtrage des logs d’accès

- **AT-301 – Filtre par période et code HTTP**
  - **Étant donné** que des logs d’accès existent dans `nginx_access_logs_ts` pour la journée J,  
  - **Lorsque** l’utilisateur sélectionne l’intervalle J 00:00 → J 23:59 et filtre sur `status_code = 500`,  
  - **Alors** l’UI doit afficher uniquement les logs 500 générés ce jour-là, paginés.

### 8.2 Test – Filtre par URI et IP

- **AT-302 – Filtre URI/IP**
  - **Étant donné** qu’il existe des logs pour l’URI `/api/test` appelés depuis une IP donnée,  
  - **Lorsque** l’utilisateur applique un filtre sur cette URI et cette IP,  
  - **Alors** seuls les enregistrements correspondants doivent s’afficher.

### 8.3 Test – Consultation de l’uptime

- **AT-303 – Résumé d’uptime**
  - **Étant donné** que `nginx_uptime_ts` contient des entrées UP et DOWN sur les dernières 24h,  
  - **Lorsque** l’utilisateur sélectionne “dernières 24 heures” dans la section uptime,  
  - **Alors** l’UI doit afficher :
    - La liste des points UP/DOWN.  
    - Un pourcentage d’uptime cohérent avec les données.  

### 8.4 Test – Export CSV

- **AT-304 – Export filtré**
  - **Étant donné** des logs filtrés (période + code HTTP + URI),  
  - **Lorsque** l’utilisateur clique sur le bouton d’export,  
  - **Alors** un fichier CSV est généré et téléchargé contenant uniquement les enregistrements correspondant aux filtres appliqués.  

### 8.5 Test – Sécurité (lecture seule)

- **AT-305 – Lecture seule**
  - **Étant donné** un utilisateur authentifié,  
  - **Lorsque** celui-ci utilise l’UI pour consulter les logs,  
  - **Alors** aucune opération de modification ou de suppression des logs ne doit être possible via l’interface.  

---

## 9. Questions ouvertes – v0.3.0

1. Quel mécanisme d’authentification sera utilisé pour l’UI (SSO d’entreprise, login simple, autre) ?  
2. Quels profils / rôles exacts auront accès à l’interface (Ops, Dev, QA, Support…) ?  
3. Faut-il prévoir dès v0.3.0 des graphiques simples (ex. histogramme de codes HTTP) ou rester strictement sur des tableaux filtrables ?  
4. Quelle limite mettre sur le volume exportable (ex. max N lignes par export) pour éviter un usage abusif ?  
5. Souhaite-t-on loguer les **actions des utilisateurs** sur l’UI (qui a consulté quoi et quand) pour audit interne ?

---