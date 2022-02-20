import os
import time

from networkx.algorithms import community
import networkx as nx
import pandas as pd
from matplotlib import pyplot as plt
import openpyxl as pxl

anime1 = pd.read_csv("anime.csv")
Score = 4
Splitgenre = []
# 100 environ 48sec 200 environ 10 min
Longueur = 100


def fichierexcel(data, data2):
    excel_book = pxl.Workbook()
    excel_book.save("Communauté.xlsx")
    excel_book2 = pxl.load_workbook('Communauté.xlsx')
    write = pd.ExcelWriter('Communauté.xlsx', engine='openpyxl')
    write.book = excel_book2
    data.to_excel(write, "Communautés", index=False)
    data2.to_excel(write, "Lien", index=False)
    reSheet = excel_book2.get_sheet_by_name('Sheet')
    excel_book2.remove(reSheet)
    write.save()
    write.close()


def tableauName():
    Name = anime1.head(Longueur)["Name"]
    return Name


def tableauGenre():
    Genre = anime1.head(Longueur)["Genres"]
    return Genre


def splittab():
    for i in range(Longueur - 1):
        Splitgenre.append(tableauGenre()[i].split(","))
    return Splitgenre


def comparaison():
    writeoncsv = []
    i = 0
    j = Longueur - 1
    while i < j:
        s1 = set(splittab()[i])
        while j > i:
            s2 = set(splittab()[j])
            count = list(s1.intersection(s2))
            print("Commons: ", count)
            if len(count) >= Score:
                print("Higher")
                newtuple = {"Nompremier": [tableauName()[i]], "Nomdeux": [tableauName()[j]], "Score": len(count),
                            "Genre": count}
                writeoncsv.append(newtuple)
            else:
                print("Under the Score")
            j = j - 1
        j = Longueur - 1
        i = i + 1
    writeoncsvdf = pd.DataFrame(writeoncsv)
    writeoncsvdf.to_csv("newanime.csv")


# Association des communautés
def set_node_community(G, communities):
    for c, v_c in enumerate(communities):
        for v in v_c:
            G.nodes[v]['community'] = c + 1


# Couleur des noeuds (Sommets)
def get_color(i, r_off=1, g_off=1, b_off=1):
    rO, gO, bO = 0, 0, 0
    n = 16
    low, high = 0.1, 0.9
    span = high - low
    r = low + span * (((i + r_off) * 3) % n) / (n - 1)
    g = low + span * (((i + g_off) * 5) % n) / (n - 1)
    b = low + span * (((i + b_off) * 7) % n) / (n - 1)
    return r, g, b


def graph():
    tabGroupe = []
    tablist = []
    df = pd.read_csv("newanime.csv")
    # Partie Graph
    G = nx.from_pandas_edgelist(df, source="Nomdeux", target="Nompremier", edge_key="Genre", edge_attr="Score",
                                create_using=nx.MultiGraph())
    communities = sorted(community.greedy_modularity_communities(G), key=len, reverse=True)
    set_node_community(G, communities)
    node_color = [get_color(G.nodes[v]['community']) for v in G.nodes]
    pos = nx.spring_layout(G, None, None, None, 50, scale=None)
    plt.rcParams.update({'figure.figsize': (10, 5)})
    nx.draw_networkx(G, pos=pos, node_size=0, edge_color="silver", with_labels=False)
    nx.draw_networkx(G, pos=pos, node_color=node_color, with_labels=False)
    print(f"On a  {len(communities)} communautés ")
    # Prendre les groupes et les liens des animes dans le graphes et les mettre dans un fichier excel
    # Liens d'attributs
    for j in range(len(G.edges)):
        lien = str(list(nx.get_edge_attributes(G, "Score").items())[j:j + 1])
        new = {"Lien": lien[3:len(lien)].replace('"', "").replace("(", "").replace(")", "").replace("[", "").replace("]", "").replace(",", "|")}
        tablist.insert(j, new)
    # Communautés
    for i in range(len(communities)):
        com = str(communities.__getitem__(i))
        count = len(communities.__getitem__(i))
        newtuple = {"Numéro": i + 1, "Nombre d'éléments": count, "Communautés": com.replace('"', "").replace("(", "").replace(")", "").replace("[", "").replace("]", "").replace("}", "")[10:len(com)]}
        tabGroupe.insert(i, newtuple)
    writecsv = pd.DataFrame(tabGroupe)
    write = pd.DataFrame(tablist)
    # Création du fichier excel
    fichierexcel(writecsv, write)
    print(f"On a {len(G.edges)} arêtes et {len(G.nodes)} sommets")
    print("Fichiers Faits")
    plt.show()


if __name__ == '__main__':
    if os.path.exists("newanime.csv"):
        print("Le fichier existe déjà.\n")
    else:
        start = time.time()
        comparaison()
        end = time.time()
        print((end - start) / 60, "minutes.\n")
    print("Voulez vous supprimer ces fichiers? yes = y no = n\n")
    c = input()
    if c == 'y':
        print("Les fichiers ont été supprimés\n")
        os.remove("newanime.csv")
        os.remove("Communauté.xlsx")
    else:
        print("Voici le graphe")
        print("Fichier excel créé")
        graph()
