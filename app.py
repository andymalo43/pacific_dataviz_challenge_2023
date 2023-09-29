
import streamlit as st


#st.set_page_config(layout="wide")

st.title("Evolution des imports de Fruits et Légumes en Nouvelle-Calédonie de 2012 à 2018")

st.header("Description")
st.markdown("""
L'objectif de ce dashboard est d'avoir un état des lieux des imports et des productions de Fruits et Légumes en Nouvelle-Calédonie. 

Nous n'avons pas pu descendre niveau comparaison fruit et légume exacte. Nous avons conservé les noms des regroupements définis dans datasets de la CPS et de l'ADRAF : 
        
- Edible fruit, nuts, peel of citrus fruit, melons
- Oil seed, oleagic fruits, grain, seed, fruit, etc, ne
- Vegetable, fruit, nut, etc food preparations
- TOTAL FRUITS (HORS VANILLE)
- TOTAL LEGUMES

Vous pourrez trouver dans l'onglet dashboard : 
- un onglet Annuel avec :
    - un sélecteur sur une année
    - des informations de volumétries générales
    - une carte avec la provenance des imports par continent et volume
    - une répartition des fruits et légums par provenance et regroupement
    - une répartition des regroupements de produits le plus importé sur l'année
- un onglet Général avec :
    - un graphique mixte montrant l'évolution des volumes des fruits et légumes par continent de provenance et le ratio volume LOCAL / (LOCAL + IMPORT)
    - une répartition des fruits et légumes par continent de provenance et par regroupement
    - Evolution du Volume des fruits et légumes par regroupement (classification CPS et ADRAF)
    - Volume des fruits et légumes par regroupement (classification CPS et ADRAF) et continent de provenance
                    
""")
st.header("Sources de données")
st.markdown(""" 
            - Données de la CPS - TRADE FOOD sur tous les pays de 2012 à 2018
                - Filtré sur : 
                ` "COMMODITY: Commodity" like '%fruit%'		or "COMMODITY: Commodity" like '%legume%')	and "IMPORTER: Importer" like 'NC:%'	and "TIME_PERIOD: Time" between 2012 and 2023 `
            - Données de l'ADRAF sur les productions locales de 2012 à 2023
            """)

st.header("Objectif caché")
st.markdown(""" 
Pour ceux qui feront le Ocean Hackathon 8, un exemple d'application web orientée données basé sur streamlit
                        """)

