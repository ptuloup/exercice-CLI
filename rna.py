import click
import requests
import csv

#Exercice réalisé par Pierre T. et Victor M. dans le cadre du Master TNAH de l'Ecole des chartes
#Outil CLI (command line interface) permettant d'interagir avec l'API RNA (registre national des associations)

RNA = "https://entreprise.data.gouv.fr/api/rna/v1/full_text"

def parser_reponse_association(data):
    """ Fait une recherche sur RNA

    :param data: JSON Parsed Data
    :type q: dict
    :returns: Tuple (
        Nombre de Résultats,
        Nombre de Pages,
        Liste de résultat sous forme de dictionnaire {id, titre, date_creation}
    )
    """
    # On récupère le nombre de résultats
    nb_items = int(data["total_results"])
    # On récupère le nombre de résultats par page
    items_per_page = int(data["per_page"])
    # Le nombre total de page est l'arrondi supérieur de la division nb_items / items_per_page
    total_pages = int(data["total_pages"])

    # On crée une liste vide dans laquelle on enregistrera les données
    items = []
    # Pour chaque réponse
    for item in data["association"]:
        # On ajoute à items un nouvel objet
        items.append({
            "id": item["id"],
            "titre": item["titre"],
            "date_creation": item["date_creation"],
            "commune": item["adresse_libelle_commune"],
            # Récupération des 2 premiers chiffres du code postal pour indiquer le département
            "département" : str(item["adresse_gestion_code_postal"])[:2],
            "objet": item["objet"],
        })

    return nb_items, total_pages, items


def cherche_association(q, page=1, per_page=20):
    """ Chercher sur RNA en faisant une requête

    :param q: Chaine de recherche
    :type q: str
    :param full: Recherche complète (itère sur toutes les pages)
    :type full: bool
    :param page: Page à récupérer
    :type page: int
    :returns: Tuple (
        Nombre de Résultats,
        Nombre de Pages,
        Liste de résultat sous forme de dictionnaire {id, titre, date_creation...}
    )
    """

    # On exécute la requête
    req = requests.get(RNA + "/{a}?per_page={b}&page={c}".format(a=q, b=per_page, c=page))

    # On la parse
    nb_items, total_pages, items = parser_reponse_association(req.json())


    return nb_items, total_pages, items

@click.group()
def mon_groupe():
    """ Groupes de commandes pour communiquer avec RNA"""


@mon_groupe.command("search")
@click.argument("query", type=str)
@click.argument("per_page", type=int, default=20)
#L'API RNA ne permet pas de passer automatiquement à la page suivante. Il faut indiquer le numéro de page
@click.argument("num", type=int, default=1)
@click.option("-o", "--output", "output_file", type=click.File(mode="w"), default=None,
              help="Fichier CSV dans lequel écrire le résultat")
def run(query, output_file, per_page, num):
    """ Exécute une recherche sur RNA en utilisant [QUERY] dans le libellé des associations
    Syntaxe : python(3) rna.py search [query] [res_par_page (max=100, def=20)] [num_page (def=1)]
    En cas de query à plusieurs mots, les mettre entre guillemets. Exemple : 'football association'
    """
    nb_items, total_pages, items = cherche_association(query)
    #Cas où l'utilisateur indique un numéro de page
    if num:
        nb_items, total_pages, items = cherche_association(query, page=num)
    #Affichage d'informations globales pour l'utilisateur
    print("Nombre total de résultats : {}".format(nb_items))
    print("Nombre de résultats affichés par page : {}".format(per_page))
    print("Nombre total de pages : {}".format(total_pages))
    print("Affichage de la page n°"+str(num))

    #Gestion de l'affichage affichage (l'affichage via Terminaltables ne fonctionne pas à cause des objets trop longs
    for element in items:
        print("============================================================================================================================================================================")
        for key, value in element.items():
            print(str(key) + " : " + str(value))
    #Création du fichier CVS output
    if output_file:
        writer = csv.writer(output_file)
        writer.writerow(["id", "titre", "date de création", "commune", "département", "objet"])
        for item in items:
            writer.writerow([item["id"], item["titre"], item["date_creation"], item["commune"], item["département"], item["objet"]])

# Si ce fichier est le fichier executé directement par python

# Alors on exécute la commande
if __name__ == "__main__":
    mon_groupe()
