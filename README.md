# BestFace

Projet du cours de traitement d'image sélectionnant la meilleure photo d'un visage passant devant un flux vidéo. Il est développé pour le travail de bachelor NIFFF 2019.

Ce module python utilise une caméra, lorsqu'il détecte un visage, prend une série de photo puis sélectionne la photo possèdant la meilleure qualité.

Il est développé par Mme. Kim Aurore Biloni, INF3DLM-b.

## Installation

1. Cloner le répertoire
2. Créer un environnement virtuel
3. Installer les dépendances `pip install -r requirements.txt`
4. Lancer le processus `python Bestface.py`

Le projet est en debug. Il est possible que vous deviez créer un dossier nommé "eyes" à la racine du projet.

## Utilisation

1. Lancer le processus `python Bestface.py`

L'application allume la caméra et commence la détection. Lorsqu'un visage est détecté, un dossier nommé "bestface_XXX" est créé à la racine du projet. Les clichés de la personne sont enregistrés dans ce dossier. Lorsqu'une nouvelle personne est détectée, un nouveau dossier est créé.

2. Quitter la détection et commencer la sélection `q`

Pressez `q` pour démarrer la sélection. L'application va sélectionner une photo par dossier et la placer dans un dossier nommé "bestfaces". Les images possèdent le nom des dossiers.

### P.S.

Il se peut que le programme se bloque. Pour ce faire, il faut fermer la console et redémarrer l'application. Le problème est un problème de concurrence qui n'a pas pu être résolu à temps.
