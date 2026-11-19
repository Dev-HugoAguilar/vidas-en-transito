import json, csv, glob, os, re, math, collections, urllib.parse, urllib.request
from pathlib import Path
import xlrd
BASE=Path(__file__).resolve().parent
RAIZ=BASE.parent
WEB=RAIZ/'web'
# Carpeta de insumos excluidos: XLS/CSV que no se versionan. Se indica con la
# variable de entorno MIGRATION_SOURCE_DIR o, por defecto, pipeline/insumos_fuente.
src=os.environ.get('MIGRATION_SOURCE_DIR',str(BASE/'insumos_fuente'))
out=str(WEB)
def workbook(name): return xlrd.open_workbook(os.path.join(src,name),on_demand=True).sheet_by_index(0)
def v(s,r,c):
 try:return s.cell_value(r,c)
 except:return ''
def num(x):
 try:return int(float(x))
 except:return 0
def clean(x):return re.sub(r'\s+',' ',str(x or '').strip())
# UPMRIP historical
hist=workbook('upmrip_cuadro_2.2.xls'); label_col=2; years=[]
for c in range(hist.ncols):
 x=v(hist,4,c)
 if str(x).strip().replace('.0','').isdigit() and 2016<=int(float(x))<=2025: years.append((c,int(float(x))))
annual=[]; type_rows=[]
for r in range(7,hist.nrows):
 label=clean(v(hist,r,label_col))
 if not label: continue
 vals=[]
 for c,y in years:
  vals.append({'year':y,'n':num(v(hist,r,c+2))}) # subtotal col
 if label.lower() in ('total','total general'):
  annual=vals
 elif label not in ('Notas','Nota'):
  total=sum(x['n'] for x in vals)
  if total: type_rows.append({'label':label,'total':total,'series':vals})
# Nationality history 2016–2025
nh=workbook('upmrip_cuadro_2.1.xls'); nationality_hist=[]
for r in range(7,nh.nrows):
 label=clean(v(nh,r,2))
 if not label: continue
 vals=[{'year':y,'n':num(v(nh,r,c+2))} for c,y in years]
 total=sum(z['n'] for z in vals)
 if total:nationality_hist.append({'label':label,'series':vals,'total':total})
# monthly 2026 based 1.2 total row and monthly category rows
m=workbook('upmrip_cuadro_1.2.xls');months=[]; monthly_types=[]
month_names=['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
for c in range(m.ncols):
 name=clean(v(m,4,c))
 if name in month_names and c+2<m.ncols and clean(v(m,5,c+2)).lower()=='subtotal':
  months.append((c,name))
for r in range(7,m.nrows):
 label=clean(v(m,r,1))
 if not label:continue
 series=[{'month':mn,'n':num(v(m,r,c+2))} for c,mn in months]
 if label.lower()=='total': monthly_total=series
 elif sum(x['n'] for x in series): monthly_types.append({'label':label,'total':sum(x['n'] for x in series),'series':series})
# state annual hist table 2.3
s=workbook('upmrip_cuadro_2.3.xls'); state_years=[]
for c in range(s.ncols):
 x=v(s,4,c)
 if str(x).strip().replace('.0','').isdigit() and 2016<=int(float(x))<=2025: state_years.append((c,int(float(x))))
state_totals=collections.Counter()
for r in range(8,s.nrows):
 name=clean(v(s,r,1))
 if name and name.lower() not in ('total','total general'):
  for c,y in state_years: state_totals[name]+=num(v(s,r,c+2))
# Gender totals by year from historical table 2.2 total row
sex_hist=[]
for gender_idx,gender_label in [(0,'Hombres'),(1,'Mujeres')]:
 vals=[]
 for c,y in years: vals.append({'year':y,'n':num(v(hist,7,c+gender_idx))})
 sex_hist.append({'label':gender_label,'series':vals,'total':sum(a['n'] for a in vals)})
# Monthly gender totals in 2026 from total row
sex_month=[]
for gender_idx,gender_label in [(0,'Hombres'),(1,'Mujeres')]:
 vals=[{'month':mn,'n':num(v(m,7,c+gender_idx))} for c,mn in months]
 sex_month.append({'label':gender_label,'series':vals,'total':sum(a['n'] for a in vals)})
# Nationality totals 2026 from table 1.1
n26=workbook('upmrip_cuadro_1.1.xls'); nationality_month=[]
for r in range(7,n26.nrows):
 label=clean(v(n26,r,1))
 if not label:continue
 vals=[{'month':mn,'n':num(v(n26,r,c+2))} for c,mn in months]
 total=sum(z['n'] for z in vals)
 if total:nationality_month.append({'label':label,'series':vals,'total':total})
# age series
ag=workbook('upmrip_cuadro_2.4.xls'); age_series=[]
age_years=[]
for c in range(ag.ncols):
 x=v(ag,4,c)
 if str(x).strip().replace('.0','').isdigit() and 2016<=int(float(x))<=2025: age_years.append((c,int(float(x))))
for r in range(8,10):
 label=clean(v(ag,r,1)); vals=[]
 for c,y in age_years: vals.append({'year':y,'n':num(v(ag,r,c+2))})
 age_series.append({'label':label,'series':vals,'total':sum(z['n'] for z in vals)})
# Monthly age data 2026 table 1.4
am=workbook('upmrip_cuadro_1.4.xls'); age_month=[]
for r in range(8,10):
 label=clean(v(am,r,1)); vals=[]
 for c,mn in months: vals.append({'month':mn,'n':num(v(am,r,c+2))})
 age_month.append({'label':label,'series':vals,'total':sum(z['n'] for z in vals)})
# ICIJ incident dataset
rows=list(csv.DictReader(open(os.path.join(src,'icij_clip_cases.csv'),encoding='utf-8-sig')))
yr=collections.Counter(); states=collections.Counter(); detection=collections.Counter(); accuracy=collections.Counter(); points=[]; totals={'incidents':len(rows),'migrants_reported':0,'deaths_reported':0,'rows_with_death_value':0,'rows_with_coordinates':0,'rows_exact_coordinates':0,'children_reported':0,'vehicles_reported':0}
for row in rows:
 date=clean(row.get('Fecha / Date')); year=date[:4] if re.match(r'^\d{4}',date) else 'Sin fecha'
 yr[year]+=1; states[clean(row.get('Estado / State')) or 'Sin estado']+=1
 detection[clean(row.get('Detección / Detection')) or 'Sin dato']+=1;accuracy[clean(row.get('Precisión / Accuracy')) or 'Sin dato']+=1
 for field,key in [('Migrantes / Migrants','migrants_reported'),('Muertes / Deaths','deaths_reported'),('Menores / Minors','children_reported'),('Vehículos / Vehicles','vehicles_reported')]:
  val=row.get(field,'').strip()
  if val:
   totals[key]+=num(val)
   if key=='deaths_reported':totals['rows_with_death_value']+=1
 lat=row.get('Latitud / Latitude','').strip();lon=row.get('Longitud / Longitude','').strip()
 if lat and lon:
  totals['rows_with_coordinates']+=1
  if clean(row.get('Precisión / Accuracy')).lower()=='exacta':totals['rows_exact_coordinates']+=1
  points.append({'date':date,'year':year,'state':clean(row.get('Estado / State')),'lat':float(lat),'lon':float(lon),'precision':clean(row.get('Precisión / Accuracy')) or 'Sin dato','migrants':num(row.get('Migrantes / Migrants')) if row.get('Migrantes / Migrants','').strip() else None,'deaths':num(row.get('Muertes / Deaths')) if row.get('Muertes / Deaths','').strip() else None})
# IOM aggregates from ArcGIS summarized counts. Confirm aggregate total matches layer count.
# ArcGIS aggregate queries; only aggregates are retained, not a list of service coordinates.
iom={}
service='https://gisportal.iom.int/arcgis/rest/services/DTM_LAC/Shelter_Service/MapServer/0/query'
for key,fields in [('country','COUNTRY'),('type','Site_Type'),('status','Status'),('country_type','COUNTRY,Site_Type'),('state','COUNTRY,ADM1_NAME')]:
 params={'where':'1=1','outStatistics':json.dumps([{'statisticType':'count','onStatisticField':'OBJECTID','outStatisticFieldName':'n'}]),'groupByFieldsForStatistics':fields,'orderByFields':'n DESC','f':'json'}
 req=urllib.request.Request(service+'?'+urllib.parse.urlencode(params),headers={'User-Agent':'Mozilla/5.0'})
 with urllib.request.urlopen(req,timeout=45) as response: payload=json.load(response)
 iom[key]=[f['attributes'] for f in payload.get('features',[])]
layer_count=sum(x.get('n',0) for x in iom.get('country',[]))
type_named=sum(x.get('n',0) for x in iom.get('type',[]) if str(x.get('Site_Type') or '').strip())
status_named=sum(x.get('n',0) for x in iom.get('status',[]) if str(x.get('Status') or '').strip())
iom_field_completeness=[{'field':'Tipo legible','n':type_named,'missing':layer_count-type_named},{'field':'Estado legible','n':status_named,'missing':layer_count-status_named},{'field':'Coordenadas lat/lon presentes','n':layer_count,'missing':0}]
# sort output and footnotes
outdata={
 'source_cutoffs':{'upmrip_historical':'2016–2025','upmrip_monthly':'enero–septiembre de 2026 (preliminar)','icij_clip':'2018–2023','iom_dtm':'consulta del servicio en 2026-11-12'},
 'upmrip':{'unit':'Personas extranjeras en situación migratoria irregular que manifestaron haber sido víctimas de delito en territorio mexicano; tablas administrativas UPMRIP/INM.','annual_total':annual,'monthly_2026_total':monthly_total,'annual_by_sex':sex_hist,'monthly_2026_by_sex':sex_month,'annual_by_crime':sorted([x for x in type_rows if x['label'] not in ['Actos relacionados con la migración','Actos bajo jurisdicción universal','Trata de personas','Actos contra la libertad','Violencia sexual','Agresiones y amenazas','Coacción','Negligencia','Robo']],key=lambda x:x['total'],reverse=True),'monthly_2026_by_crime':sorted(monthly_types,key=lambda x:x['total'],reverse=True),'age_annual':age_series,'age_monthly_2026':age_month,'nationality_annual':nationality_hist,'nationality_monthly_2026':nationality_month,'state_annual_totals':sorted([{'state':k,'n':v} for k,v in state_totals.items()],key=lambda x:x['n'],reverse=True),'definitions':{'state':'entidad de registro, no necesariamente lugar del hecho','zero':'(-) significa cero en las tablas; ausencia de fila no se convierte en cero','cutoff':'cuadros 2026 consultados: enero-septiembre; valores preliminares'}},
 'icij_clip':{'unit':'Incident/case row in the ICIJ/CLIP investigation database; incidents are not unique persons.','points':points,'totals':totals,'by_year':[{'year':k,'incidents':v} for k,v in sorted(yr.items())],'by_state':[{'state':k,'incidents':v} for k,v in states.most_common()],'by_detection':[{'label':k,'incidents':v} for k,v in detection.most_common()],'by_coordinate_precision':[{'label':k,'incidents':v} for k,v in accuracy.most_common()]},
 'iom_shelters':{'service_layer_record_count':layer_count,'aggregates':iom,'field_completeness':iom_field_completeness,'extent':'Capa parcial con alcance geográfico del servicio; no demuestra directorio exhaustivo ni cobertura homogénea de la región.','unit':'feature de servicio publicado en ArcGIS; vigencia/contacto/capacidad deben comprobarse antes de orientación práctica.'}
}
# Consistency diagnostics
outdata['diagnostics']={'annual_upmrip_total_sum':sum(x['n'] for x in annual),'annual_years':[x['year'] for x in annual],'monthly_upmrip_sum':sum(x['n'] for x in monthly_total),'monthly_labels':[x['month'] for x in monthly_total],'icij_death_sum_reported':totals['deaths_reported'],'icij_incident_count':len(rows),'iom_groupby_country_total':sum(x.get('n',0) for x in iom.get('country',[]))}
json.dump(outdata,open(os.path.join(out,'fuentes_ampliadas.json'),'w'),ensure_ascii=False,indent=2)
print(json.dumps(outdata['diagnostics'],ensure_ascii=False,indent=2));print('ICIJ',totals);print('UPMRIP annual',annual);print('monthly',monthly_total);print('IOM country rows',len(iom.get('country',[])),iom.get('country',[])[:5])
