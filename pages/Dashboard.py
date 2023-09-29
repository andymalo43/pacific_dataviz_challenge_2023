import folium
import streamlit as st
import duckdb
from streamlit_folium import st_folium
import pandas as pd
import plotly.express as px
from millify import millify
from folium.plugins import AntPath

import plotly.graph_objects as go



st.set_page_config(layout="wide")



#conn = duckdb.connect("pdc.db")
conn = duckdb.connect()

query_local = """
with 
	source_local as (
SELECT
	'local' as pays_exporter,
	regroupement1,
	regroupement2,
	strptime(annee || lpad(mois,
	2,
	'0')|| '01',
	'%Y%m%d') as date_releve,
	'-21.3019905' as latitude,
	'165.4880773' as longitude,
	poids_enquete_kg as volume_commercialise
FROM
	pdc.main.ADRAF_regroupement1)
    select
	pays_exporter,
    regroupement2,
	year(date_releve) as date_releve,
	latitude,
	longitude,
	sum(volume_commercialise/1000) as total
from
	source_local
where year(date_releve) <= 2018 and pays_exporter <> 'Antarctica'
group by
	1,
	2,
	3,
	4,
    5
"""

query_import = """
with source_import as (
SELECT
	b.continent as pays_exporter,
	'' as regroupement1,
	string_split("COMMODITY: Commodity" ,
	':')[2] as regroupement2,
	YEAR(strptime("TIME_PERIOD: Time" || '0101',
	'%Y%m%d')) as date_releve,
	b.latitude_country as latitude,
	b.longitude_country as longitude,
	OBS_VALUE as volume_importé
FROM
	pdc.main.CPS_Trade_food a
inner join main.CPS_countries_coordinates b on
	a."EXPORTER: Exporter" like ('%' || b.pays_norme || '%')
where
	("COMMODITY: Commodity" like '%fruit%'
		or "COMMODITY: Commodity" like '%legume%')
	and "IMPORTER: Importer" like 'NC:%'
	and "TIME_PERIOD: Time" between 2012 and 2023)
	select
	pays_exporter,
    regroupement2,
	date_releve,
	latitude,
	longitude,
	sum(volume_importé) as total
from
	source_import
where date_releve <= 2018 and pays_exporter <> 'Antarctica'
group by
	1,
	2,
	3,
	4,
    5
"""

query_local= "select * from read_parquet('./local.parquet')"
query_import= "select * from read_parquet('./import.parquet')"

df_local = conn.execute(query=query_local).df()
df_import = conn.execute(query=query_import).df()


df_all = pd.concat([df_local,df_import])

annee_select = 2015

tab2, tab1 = st.tabs(["Annuel","Global"])

with tab1 :
	import_total = conn.execute(f"select date_releve,  sum(total) as total_import from df_all where trim(pays_exporter) <> 'local' group by 1").df()
	production_locale = conn.execute(f"select date_releve, sum(total) as total_local from df_all where trim(pays_exporter) = 'local' group by 1").df()

	synthese_import_production = conn.execute(f"""
											select p.date_releve, (total_local/(total_local + total_import)*100) as ratio
											from import_total i inner join production_locale p on i.date_releve=p.date_releve
	""").df()


	evolotion_import_local = conn.execute(f"select date_releve, case when trim(pays_exporter) <> 'local' then pays_exporter else 'local' end as type_production,sum(total) as total from df_all where date_releve <= 2018 and regroupement2 is not null group by 1,2").df()

	all_date_type_production = conn.execute(f"select 'import' as type_production,date_releve, sum(total) as total from df_all where trim(pays_exporter) <> 'local' and date_releve <= 2018 group by 1,2 UNION ALL select 'local' as type_production, date_releve, sum(total) as total from df_all where trim(pays_exporter) = 'local' and date_releve <= 2018 group by 1,2" ).df()

	fig = go.Figure(
		data=go.Bar(
			x=evolotion_import_local["date_releve"],
			y=evolotion_import_local["total"],
			name="Produit par",
		)
	)

	fig = px.bar(evolotion_import_local, x="date_releve",y="total", color="type_production")

	fig.add_trace(
		go.Scatter(
			x=synthese_import_production["date_releve"],
			y=synthese_import_production["ratio"],
			yaxis="y2",
			name="Ratio Import / Local"
		)
	)

	fig.update_layout(
		legend=dict(orientation="h"),
		yaxis=dict(
			title=dict(text="Total importé"),
			side="left",
			range=[0, 150000],
		),
		yaxis2=dict(
			title=dict(text="Ratio LOCAL / IMPORT"),
			side="right",
			range=[0, 30],
			overlaying="y",
			tickmode="sync",
		),
	)


	st.header("Evolution du volume des fruits et légumes par continent de provenance")
	st.plotly_chart(fig, use_container_width=True)

	st.header("Volume des fruits et légumes par continent de provenance et par regroupement (classification CPS et ADRAF)")
	produit_par_pays = conn.execute("select pays_exporter, regroupement2, sum(total) as total from df_all where 1=1 and regroupement2 is not null group by 1,2 ").df()
	st.bar_chart(data=produit_par_pays, x="pays_exporter", y="total", color="regroupement2")

	st.header("Evolution du Volume des fruits et légumes par regroupement (classification CPS et ADRAF)")
	produit_par_pays = conn.execute("select date_releve, regroupement2, sum(total) as total from df_all where 1=1 and regroupement2 is not null group by 1,2 ").df()
	st.bar_chart(data=produit_par_pays, x="date_releve", y="total", color="regroupement2")

	st.header("Volume des fruits et légumes par regroupement (classification CPS et ADRAF) et continent de provenance ")
	produit_par_pays = conn.execute("select pays_exporter, regroupement2, sum(total) as total from df_all where 1=1 and regroupement2 is not null group by 1,2 ").df()
	st.bar_chart(data=produit_par_pays, x="regroupement2", y="total", color="pays_exporter")


with tab2:

	annee_select = st.slider("Choix de l'année",2012,2018,2015)


	import_total = conn.execute(f"select sum(total) as total from df_all where trim(pays_exporter) <> 'local' and date_releve={annee_select}").df()
	production_locale = conn.execute(f"select sum(total) as total from df_all where trim(pays_exporter) = 'local' and date_releve={annee_select}").df()

	st.header("Informations de volumétries générales")

	metric4,metric1,metric2,metric3 = st.columns(4)

	metric4.metric("IMPORT + LOCALE", millify(float(import_total['total'].iloc[0])+float(production_locale['total'].iloc[0])))
	metric1.metric("IMPORT TOTAL",millify(float(import_total['total'].iloc[0]))) 
	metric2.metric("PRODUCTION LOCALE", millify(float(production_locale['total'].iloc[0])))
	metric3.metric("RATIO LOCAL/TOTAL", f"{millify(float(production_locale['total'].iloc[0]/(production_locale['total'].iloc[0]+import_total['total'].iloc[0]))*100, precision=2)} %")



	m = folium.Map(location=[-21.3019905,165.4880773], zoom_start=1)
	m = folium.Map(location=[-21,120], zoom_start=3)

	folium.Marker(
		[-21.3019905,165.4880773], popup="New Caledonia", tooltip="Nouvelle-Calédonie"
	).add_to(m)



	lines_map_import = conn.execute(f"select latitude,longitude,pays_exporter,sum(total) as total from df_import where date_releve ={annee_select} group by 1,2,3").df()



	for row in lines_map_import.itertuples():
		#folium.PolyLine(smooth_factor=100,locations=[[row.latitude,row.longitude],[-21.3019905,165.4880773]], weight=int(row.total/production_locale['total'].iloc[0])*10, tooltip=f"{row.total/production_locale['total'].iloc[0]}",).add_to(m)
		AntPath([[row.latitude,row.longitude],[-21.3019905,165.4880773]], delay=400, dash_array=[30,15], color="red", weight=5, tooltip=f"Origine = {row.pays_exporter} \n {row.total} T", popup=f"ratio IMPORT/(IMPORT+LOCAL) = {millify((row.total/(production_locale['total'].iloc[0]+import_total['total'].iloc[0]))*100, precision=2)}").add_to(m)

	folium.CircleMarker(
		location=[-21.3019905,165.4880773],
		radius= 50,
		color = "cornflowerblue",
		stroke=False,
		fill=True
	).add_to(m)


	st.header("Provenance des imports par volume")

	st_data = st_folium(m,width='100%', height='400')

	#import_par_pays=

	#st.dataframe(df_all[df_all.date_releve == annee_select])


	col_reg1, col_reg2 = st.columns(2)




	date_type_production = conn.execute(f"select pays_exporter as type_production,regroupement2, date_releve, sum(total) as total from df_all where trim(pays_exporter) <> 'local' and date_releve ={annee_select} and regroupement2 is not null group by 1,2,3 UNION ALL select 'local' as type_production, regroupement2, date_releve, sum(total) as total from df_all where trim(pays_exporter) = 'local' and regroupement2 is not null and date_releve ={annee_select} group by 1,2,3" ).df()

	#st.dataframe(all_date_type_production)

	col_reg1.header("Volume des fruits et légumes par continent de provenance et par regroupement (classification CPS et ADRAF)")
	col_reg1.bar_chart(date_type_production, x="type_production",y="total",color="regroupement2")

	le_plus_importe = conn.execute(f"select regroupement2, date_releve, sum(total) as total from df_all where trim(pays_exporter) <> 'local' and date_releve ={annee_select} and regroupement2 is not null group by 1,2").df()


	col_reg2.header("Répartition des regroupements de produits le plus importé (classification CPS)")
	fig = px.pie(le_plus_importe, values='total', names='regroupement2')
	col_reg2.plotly_chart(fig)