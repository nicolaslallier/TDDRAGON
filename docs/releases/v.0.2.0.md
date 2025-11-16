# Documentation – Plateforme v0.2.0 (Nginx + PostgreSQL + Time Series Logs)

- **Nom du système** : (à définir) – Plateforme applicative  
- **Version** : `v0.2.0`  
- **Baseline** : Tout ce qui est défini en **v0.1.0** demeure valide (Nginx en reverse proxy, application backend, PostgreSQL comme BD).  
- **Nouveauté v0.2.0** :  
  - Stockage **historique** des logs Nginx (uptime et accès) dans des **tables time series PostgreSQL**.

---

## 0. Hypothèses (Assumptions)

1. L’architecture de base v0.1.0 est déjà opérationnelle :
   - Nginx en front.
   - Application backend.
   - PostgreSQL accessible uniquement depuis le réseau applicatif.
2. Nginx produit déjà des **logs d’accès** (access logs) et éventuellement des logs d’erreur / statut.
3. Un **composant collecteur** sera mis en place pour ingérer les logs Nginx vers PostgreSQL :
   - Soit un **service technique** (microservice, job scheduled, sidecar).
   - Soit une extension de l’application existante.
4. Le stockage “time series” sera implémenté via :
   - Des tables PostgreSQL structurées autour d’un **timestamp**, avec indexation et éventuelle partition (pas figé au niveau fonctionnel).
5. Les logs ne contiendront pas de **données sensibles** (PII) au-delà des IP / user-agent standard (à confirmer si nécessaire).

---

## 1. Contexte & Objectifs (Context & Goals) – v0.2.0

### 1.1 Contexte

- Nginx sert de point d’entrée au système (v0.1.0).
- Les logs Nginx sont actuellement exploités surtout **en local** (fichiers sur le serveur / container).
- Les équipes souhaitent :
  - Pouvoir **analyser l’historique** des accès.
  - Suivre la **disponibilité / uptime** via des indicateurs basés sur les logs.
  - Préparer à terme des **tableaux de bord** (monitoring, capacity planning, sécurité).

### 1.2 Problème

- Sans stockage structuré des logs dans la BD :
  - Analyse historique limitée (rotation des fichiers, accès difficile).
  - Corrélation compliquée avec d’autres données (événements app, incidents).
  - Peu de visibilité sur la **disponibilité réelle** (uptime observé) du service.

### 1.3 Objectifs v0.2.0

- Mettre en place un **flux de collecte** des logs Nginx vers PostgreSQL.
- Structurer les logs dans des **tables time series** :
  - Une table pour les **logs d’accès**.
  - Une ou plusieurs tables pour les **indicateurs d’uptime / statut**.
- Permettre des **requêtes simples** pour :
  - Filtrer par période, URL, code HTTP, etc.
  - Calculer un **pourcentage d’uptime** sur une période donnée.

### 1.4 Périmètre v0.2.0

**Inclus (In Scope)**

- Collecte régulière des logs Nginx (ou flux quasi temps réel) vers PostgreSQL.
- Création des tables time series pour :
  - **Logs d’accès Nginx**.
  - **Mesures d’uptime** (ex. “Nginx/endpoint up/down à t instant T”).
- Endpoints / scripts minimaux permettant de **vérifier** le bon stockage et de faire quelques requêtes de base.

**Exclus (Out of Scope)**

- Plateforme de monitoring complète (Grafana, Kibana, etc.).
- Alerting automatisé (emails, Slack, etc.).
- Agrégations complexes (statistiques avancées, machine learning).

---

## 2. Parties prenantes / Stakeholders (spécifique v0.2.0)

En plus des parties prenantes de v0.1.0 :

- **Ops / SRE / Support** : utilise les données de logs pour diagnostic et suivi uptime.
- **Sécurité / SecOps** : peut utiliser les logs pour détecter des patterns d’accès anormaux (usage futur).
- **Data / BI (éventuel)** : s’intéressera aux données pour reporting.

---

## 3. Processus & Scénarios (BPMN-like) – Logging Nginx → PostgreSQL

### 3.1 Processus principal – Ingestion des logs Nginx

> Start → Nginx écrit un log → Collecteur lit le log → Transformation en enregistrement structuré → Insertion dans PostgreSQL (time series) → Logs disponibles pour requêtes → End

**Étapes**

1. **Start** – Nginx reçoit une requête et produit une ligne de log (access log).
2. La ligne de log est écrite dans un fichier ou envoyée vers un flux (stdout, pipe…).
3. Un **collecteur de logs** (service dédié ou module de l’application) lit régulièrement les nouvelles lignes.
4. Le collecteur **parse** chaque ligne et :
   - Extrait la date/heure, IP, méthode, URI, code HTTP, user-agent, temps de réponse, etc.
   - Génère un enregistrement structuré.
5. Le collecteur insère l’enregistrement dans la table `nginx_access_logs_ts` (time series).
6. En parallèle ou par agrégation périodique, le collecteur calcule ou déduit un **statut d’uptime** (UP/DOWN) et insère dans `nginx_uptime_ts`.
7. Les données sont désormais requêtables via PostgreSQL (requêtes SQL, vues, etc.).
8. **End** – Les équipes peuvent analyser les logs et l’uptime par période.

---

## 4. Exigences fonctionnelles (Functional Requirements) – v0.2.0

> Numérotation spécifique v0.2.0 : **FR-2XX**

### 4.1 Collecte et stockage des logs Nginx

- **FR-201** – Le système doit collecter les logs d’accès générés par Nginx et les stocker dans une table PostgreSQL de type time series nommée (par exemple) `nginx_access_logs_ts`.  
- **FR-202** – Chaque ligne de log Nginx doit être convertie en enregistrement structuré comprenant au minimum :
  - Timestamp de la requête.
  - Adresse IP du client.
  - Méthode HTTP (GET, POST, etc.).
  - URI / path demandé.
  - Code de réponse HTTP.
  - Temps de réponse (si disponible).
- **FR-203** – La collecte des logs doit s’exécuter de manière **continue ou quasi continue** (ex. job périodique toutes les X secondes / minutes) afin que le décalage entre la génération du log et son stockage en BD reste maîtrisé.

### 4.2 Suivi d’uptime (Nginx / Application)

- **FR-204** – Le système doit maintenir une table time series `nginx_uptime_ts` permettant de suivre l’**état de disponibilité** (UP/DOWN, ou code équivalent) sur une base temporelle.  
- **FR-205** – Pour chaque point de mesure d’uptime, l’enregistrement doit inclure au minimum :
  - Timestamp de la mesure.
  - Statut (UP / DOWN ou équivalent).
  - Source de la mesure (ex. test interne, résultat d’un appel `/health`).  
- **FR-206** – Le système doit permettre de calculer, via une requête SQL, un **pourcentage d’uptime** (ex. sur les dernières 24 heures) à partir des données de `nginx_uptime_ts`.

### 4.3 Consultation des données

- **FR-207** – Il doit être possible d’interroger la table `nginx_access_logs_ts` par intervalle de temps (ex. `WHERE timestamp BETWEEN t1 AND t2`).  
- **FR-208** – Il doit être possible de filtrer les logs par code HTTP (ex. 2xx, 4xx, 5xx) et par URI pour identifier les points de terminaison problématiques.  
- **FR-209** – Il doit être possible d’interroger `nginx_uptime_ts` pour obtenir la liste des périodes de **panne** (statut DOWN) et leur durée approximative.

---

## 5. Exigences non fonctionnelles (NFRs) – v0.2.0

> Numérotation : **NFR-2XX**

### 5.1 Performance & Volume

- **NFR-201** – Le système doit supporter l’insertion d’au moins **X logs par minute** (valeur à confirmer selon charge attendue) sans dégradation significative de la performance globale.  
- **NFR-202** – Les requêtes sur les tables time series (filtrage par période + code HTTP) doivent répondre en **≤ 2 secondes** pour un intervalle de 24 heures, sur un volume courant (environnement cible à préciser).

### 5.2 Sécurité & Confidentialité

- **NFR-203** – Les logs stockés ne doivent pas contenir de données sensibles en clair autres que les informations techniques standard (IP, user-agent, URL).  
- **NFR-204** – Les droits d’accès aux tables de logs (`nginx_access_logs_ts`, `nginx_uptime_ts`) doivent être limités aux rôles techniques autorisés (Ops, Dev, etc.) et ne pas être exposés directement à des utilisateurs finaux.

### 5.3 Rétention & Archivage

- **NFR-205** – Une **période de rétention** doit être définie (ex. 90 jours, 180 jours) pour les logs, après laquelle les données pourront être archivées ou purgées (valeur à confirmer avec les parties prenantes).  
- **NFR-206** – Le mécanisme d’archivage/purge doit être automatisable (job SQL, script, etc.), même s’il n’est pas entièrement livré en v0.2.0.

---

## 6. Règles d’affaires / Règles techniques (BR) – v0.2.0

> Numérotation : **BR-2XX**

- **BR-201** – Les tables de logs doivent être construites autour d’une colonne de **timestamp** servant de clé d’ordonnancement principal (time series).  
- **BR-202** – Les tables de logs peuvent être partitionnées par **jour** ou **mois** (décision d’implémentation technique) afin de faciliter la purge et les performances ; au niveau fonctionnel, cette partition doit être transparente pour les requêtes business.  
- **BR-203** – L’heure des logs doit être stockée en **UTC** pour éviter les problèmes de fuseau horaire ; l’affichage local (ex. heure de Montréal) est géré au niveau reporting.  
- **BR-204** – Toute modification de structure (ajout de colonnes dans les tables de logs) doit être versionnée (scripts de migration, comme pour le reste du schéma).

---

## 7. Données & Modèle d’information – Logs Nginx (Time Series)

### 7.1 Table `nginx_access_logs_ts` (exemple fonctionnel)

| Champ            | Type (indicatif) | Description                                      |
|------------------|------------------|--------------------------------------------------|
| `id`             | BIGSERIAL / UUID | Identifiant unique (clé primaire)                |
| `timestamp_utc`  | TIMESTAMP        | Date/heure de la requête (UTC)                   |
| `client_ip`      | TEXT             | Adresse IP du client                             |
| `http_method`    | TEXT             | Méthode HTTP (GET, POST…)                        |
| `request_uri`    | TEXT             | URI / path demandé                               |
| `status_code`    | INTEGER          | Code HTTP de réponse                             |
| `response_time`  | NUMERIC          | Temps de réponse (ms ou s, à préciser)           |
| `user_agent`     | TEXT             | User-Agent du client (optionnel)                 |
| `raw_line`       | TEXT             | Ligne brute du log (optionnel pour diagnostic)   |

> Types et longueurs à ajuster au design technique / DBA.

### 7.2 Table `nginx_uptime_ts` (exemple fonctionnel)

| Champ            | Type (indicatif) | Description                                      |
|------------------|------------------|--------------------------------------------------|
| `id`             | BIGSERIAL / UUID | Identifiant unique                               |
| `timestamp_utc`  | TIMESTAMP        | Date/heure de la mesure (UTC)                    |
| `status`         | TEXT             | Statut (ex. `UP`, `DOWN`)                        |
| `source`         | TEXT             | Source de la mesure (ex. “healthcheck_nginx”)    |
| `details`        | TEXT             | Détails éventuels (message d’erreur, etc.)       |

---

## 8. Cas de tests d’acceptation (Acceptance Criteria) – v0.2.0

> Numérotation : **AT-2XX**

### 8.1 Test – Ingestion des logs d’accès

- **AT-201 – Ingestion Nginx → PostgreSQL**
  - **Étant donné** que Nginx génère des logs d’accès,  
  - **Lorsque** plusieurs requêtes HTTP sont envoyées via Nginx (ex. 10 requêtes sur `/health`),  
  - **Alors** les enregistrements correspondants doivent être visibles dans la table `nginx_access_logs_ts` avec les bons champs (timestamp, méthode, URI, status_code, etc.).

### 8.2 Test – Filtrage par période et code HTTP

- **AT-202 – Requête par intervalle**
  - **Étant donné** que des logs sont stockés sur une période de temps,  
  - **Lorsque** une requête SQL filtre `nginx_access_logs_ts` entre `t1` et `t2` pour `status_code = 500`,  
  - **Alors** seuls les logs correspondant à des réponses 500 dans l’intervalle doivent être retournés.

### 8.3 Test – Mesure d’uptime

- **AT-203 – Calcul de l’uptime**
  - **Étant donné** que des mesures d’uptime sont insérées régulièrement dans `nginx_uptime_ts` (ex. toutes les minutes),  
  - **Lorsque** une requête SQL agrège les mesures sur les dernières 24 heures,  
  - **Alors** il doit être possible de calculer un pourcentage d’uptime (nombre de points UP / total de points).

### 8.4 Test – Rétention (fonctionnelle)

- **AT-204 – Période de rétention**
  - **Étant donné** une politique de rétention (ex. 90 jours),  
  - **Lorsque** la date d’un log excède la durée de rétention et que le processus de purge/archivage est exécuté,  
  - **Alors** les logs plus anciens que la période définie ne doivent plus être présents dans les tables actives (ou doivent être déplacés dans une table d’archive, selon la solution retenue).

---

## 9. Questions ouvertes (v0.2.0)

1. **Fréquence d’ingestion** : temps réel, toutes les X secondes, 1 minute, 5 minutes ?  
2. **Volume attendu** : nombre moyen/maximal de requêtes par seconde / minute pour estimer la taille des tables ?  
3. **Période de rétention** à confirmer (30, 90, 180 jours ?) et contraintes légales éventuelles.  
4. **Niveau de détail** : conserve-t-on le `user_agent` et la ligne brute (`raw_line`) ou limite-t-on le stockage aux informations techniques minimales ?  
5. Les données de logs pourront-elles être utilisées ultérieurement pour la **détection d’incidents de sécurité** (ce qui pourrait influer sur la rétention et le détail conservé) ?

---