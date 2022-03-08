import os
import time
import re
from networkx.algorithms import community
import networkx as nx
import pandas as pd
from matplotlib import pyplot as plt
import openpyxl as pxl

anime1 = pd.read_csv("anime.csv", sep=";")
Score = 4
Splitgenre = []
# Echantillons sur les animés
# 100 environ 48sec
Longueur = 150


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
                newtuple = {"Nompremier": tableauName()[i], "Nomdeux": tableauName()[j], "Score": len(count),
                            "Genre": count}
                writeoncsv.append(newtuple)
            else:
                print("Under the Score")
            j = j - 1
        j = Longueur - 1
        i = i + 1
    writeoncsvdf = pd.DataFrame(writeoncsv)
    writeoncsvdf.to_csv("graphe.csv")


# Association des communautés
def set_node_community(G, communities):
    for c, v_c in enumerate(communities):
        for v in v_c:
            G.nodes[v]['community'] = c + 1


def set_edge_community(G):
    """Find internal edges and add their community to their attributes"""
    for v, w, in G.edges:
        if G.nodes[v]['community'] == G.nodes[w]['community']:
            G.edges[v, w]['community'] = G.nodes[v]['community']
        else:
            G.edges[v, w]['community'] = 0


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
    k, l = 0, 0
    tabGroupe, tablist, tabcomm = [], [], []
    df = pd.read_csv("graphe.csv")
    # Partie Graph
    G = nx.from_pandas_edgelist(df, source="Nomdeux", target="Nompremier", edge_key="Genre", edge_attr="Score",
                                create_using=nx.Graph)
    communities = sorted(community.greedy_modularity_communities(G), key=len, reverse=True)
    set_node_community(G, communities)
    set_edge_community(G)
    external = [(v, w) for v, w in G.edges if G.edges[v, w]['community'] == 0]
    internal = [(v, w) for v, w in G.edges if G.edges[v, w]['community'] > 0]
    internal_color = [get_color(G.edges[e]['community']) for e in internal]
    node_color = [get_color(G.nodes[v]['community']) for v in G.nodes]
    pos = nx.spring_layout(G, k=0.1)
    plt.rcParams.update(plt.rcParamsDefault)
    plt.rcParams.update({'figure.figsize': (15, 10)})
    plt.style.use('dark_background')
    plt.title(f"Communautés d'animés en fonction du Score de Tags. ({len(G.nodes)} animés)", loc='left')
    nx.draw_networkx(G, pos=pos, node_size=0, edgelist=external, edge_color="silver", node_color=node_color, with_labels=False)
    nx.draw_networkx(G, pos=pos, node_color=node_color, edgelist=internal, edge_color=internal_color, with_labels=False)
    print(f"On a  {len(communities)} communautés ")
    # Prendre les groupes et les liens des animes dans le graphes et les mettre dans un fichier excel
    # Liens d'attributs
    for j in range(len(G.edges)):
        lien = str(list(nx.get_edge_attributes(G, "Score").items())[j:j + 1])
        digit = [int(s) for s in re.findall(r"-?\d+\.?\d*", lien[len(lien) - 3:len(lien)])]
        new = {"Score": digit,
               "Lien": lien[3:len(lien) - 3].replace('"', "").replace("(", "").replace(")", "").replace("[",
                                                                                                        "").replace("]",
                                                                                                                    "").replace(
                   ",", "|")}
        tablist.insert(j, new)
    # Communautés
    for i in range(len(communities)):
        com = str(communities.__getitem__(i))
        count = len(communities.__getitem__(i))
        newtuple = {"Numéro": i + 1, "Nombre d'éléments": count,
                    "Communautés": com.replace('"', "").replace("(", "").replace(")", "").replace("[", "").replace("]",
                                                                                                                   "").replace(
                        "}", "")[10:len(com)]}
        tabGroupe.insert(i, newtuple)
    # Réarranger les communautés avec les noms d'animés dans une DATAFRAME pour créer un Histogramme
    while k < len(anime1.head(Longueur)):
        first = anime1.head(Longueur)["Name"][k]
        while l < len(communities):
            comu = str(communities.__getitem__(l))
            if comu.__contains__(first):
                ajout = {"Nom": anime1.head(Longueur)["Name"][k], "Note": anime1.head(Longueur)["Score"][k],
                         "Rang": anime1.head(Longueur)["Ranked"][k], "Communauté": l + 1}
                tabcomm.append(ajout)
            l = l + 1
        k = k + 1
        l = 0
    data = pd.DataFrame(tabcomm)
    # Création du csv Histogramme pour une étude de cas
    data.to_csv("Histogramme.csv")
    writecsv = pd.DataFrame(tabGroupe)
    write = pd.DataFrame(tablist)
    print(f"On a {len(G.edges)} arêtes et {len(G.nodes)} sommets")
    # Création du fichier excel pour avoir les communautés et les liens des noeuds
    fichierexcel(writecsv, write)
    print("Fichiers Faits")
    plt.show()


def histo():
    view = pd.read_csv("Histogramme.csv")
    df = pd.DataFrame(view)
    x = df.Note
    z = df.Rang
    y = df.Communauté
    fig = plt.figure(figsize=(12, 8), dpi=80)
    ax = fig.gca(projection="3d")
    plo = ax.plot_trisurf(x, y, z, cmap=plt.cm.coolwarm_r)
    cbar = fig.colorbar(plo, shrink=0.5, aspect=5)
    cbar.ax.invert_yaxis()
    cbar.set_label("Rangs", color="peachpuff")
    ax.set_title("Les Communautés d'Animés en fonction de leurs Notes et des Rangs.")
    ax.view_init(30, 65)
    fig.set_facecolor("grey")
    ax.set_facecolor("grey")
    ax.set_xlabel("Note", color='peachpuff')
    ax.set_ylabel("Communauté", color='peachpuff')
    ax.set_zlabel("Rang", color='peachpuff')
    plt.show()


if __name__ == '__main__':
    if os.path.exists("graphe.csv"):
        print("Le fichier existe déjà.\n")
        print("Voulez vous supprimer ces fichiers? yes = y no = n\n")
        c = input()
        if c == 'y':
            print("Les fichiers ont été supprimés\n")
            os.remove("graphe.csv")
            os.remove("Communauté.xlsx")
            os.remove("Histogramme.csv")
            start = time.time()
            comparaison()
            end = time.time()
            print((end - start) / 60, "minutes.\n")
            graph()
            histo()
        else:
            print("Voici le graphe")
            print("Fichier excel créé")
            graph()
            histo()
    else:
        start = time.time()
        comparaison()
        end = time.time()
        print((end - start) / 60, "minutes.\n")
        graph()
        histo()
