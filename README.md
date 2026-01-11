# 🚁 SkyHub: eVTOL Vertiport Optimization

**SkyHub** est un outil d'ingénierie système et de Data Science conçu pour optimiser l'infrastructure des futurs aéroports de drones taxis (eVTOL). Le projet utilise des simulations Monte Carlo pour trouver l'équilibre parfait entre rentabilité financière et sécurité aérienne absolue.



## 🎯 Objectif du Projet
Déterminer la configuration optimale (**Nombre de Chargeurs** + **Capacité du Garage**) pour un Vertiport urbain. L'enjeu est de maximiser le profit mensuel tout en garantissant **zéro accident**, malgré les variations massives de trafic entre les heures de pointe et les week-ends.

## 🧠 Architecture & Algorithme

Le projet repose sur une approche modulaire en trois couches :

### 1. Couche Physique (`evtol.py`)
Simulation réaliste des paramètres d'un drone électrique :
* Consommation dynamique de la batterie en vol ($2.5\% / min$).
* Vitesse de recharge via Superchargeurs ($5\% / min$).
* Gestion des priorités de mission (Standard, Business, Urgence Médicale).

### 2. Couche Logicielle : ATC Prédictif (`vertiport.py`)
Le système intègre un contrôleur aérien intelligent. Contrairement à une file d'attente classique, il calcule en temps réel le **Temps d'Attente Estimé** basé sur la capacité actuelle de traitement.
* **Refus d'accès :** Si le temps d'attente estimé dépasse l'autonomie de sécurité du drone entrant, l'accès au Vertiport est refusé. 
* **Zéro Crash :** Cette approche proactive élimine tout risque de panne sèche en vol.

### 3. Couche Data Science : Auto-Scaling (`config.py`)
Le projet utilise le concept de **Grid Search** (recherche par grille), mais de manière prédictive :
* **Analyse de Flux :** Le script analyse les profils de probabilité de trafic pour calculer le flux moyen et de pointe.
* **Pré-dimensionnement :** Il utilise la **Loi de Little** pour déduire mathématiquement l'espace de recherche optimal autour du point d'équilibre.
* **Scalabilité :** Les bornes de test se déplacent automatiquement si la demande du marché ou les performances des chargeurs changent.



## 📊 Résultat du Benchmark (Paris)
Sur une simulation de 28 jours avec un trafic de pointe à 95%, la configuration optimale identifiée est :

| Paramètre | Valeur Optimale |
| :--- | :--- |
| **Chargeurs (Pads)** | **6** |
| **Places de Garage** | **30** |
| **Bénéfice Net Mensuel** | **~568,902 €** |
| **Taux de Sécurité** | **100% (0 Crash)** |



## 🚀 Installation & Utilisation

### Prérequis
* Python 3.x
* Pygame (pour la visualisation graphique)



## 🚀 Installation & Lancement

1.  Installer les dépendances :
    ```bash
    pip install pygame
    ```

2.  Lancer l'optimiseur (Recherche de solution) :
    ```bash
    python3 optimizer.py
    ```

3.  Lancer la démo visuelle (Configuration gagnante) :
    ```bash
    python3 simulation.py
    ```

## 📂 Structure

* `config.py` : Paramètres globaux et algorithme d'auto-scaling de l'espace de recherche.

* `evtol.py` : Logique physique (batterie, consommation) des drones.

* `vertiport.py` : Cœur du système (ATC prédictif et gestion de flotte).

* `optimizer.py` : Moteur de simulation Monte Carlo et analyse financière.

* `visualizer.py` : Interface graphique Pygame pour le monitoring.