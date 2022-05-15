
##----- import libraries
import powerfactory 
from MVMO import MVMO

##----- configuraciones iniciales DigSilent
app=powerfactory.GetApplication()
app.ClearOutputWindow() # se limpia el output window
app.EchoOff()
script_fold = app.GetCurrentScript() #to call the current script
active_prj = app.GetActiveProject() # Get Active Project
ldf=app.GetFromStudyCase('ComLdf') # Get low flow calculation 

dict_sets = {} # diccionario de Sets
for e in script_fold.GetContents(): # se guardan los Sets en el diccionario
    dict_sets[e.loc_name] = e
# diccionario de todos los elementos
dict_all_elm = dict(
    (elm.obj_id.loc_name, elm.obj_id) 
    for elm in dict_sets.get('Stage').Get()
)

##----- main -----
def get_var(set_name, var):
    ldf.Execute()
    result = 0
    for elm in dict_sets.get(set_name).GetContents():
        result += elm.obj_id.GetAttribute(var)
    return result
def set_attribut(name, var, value):
    # set attribute at Power Factory
    elm = dict_all_elm.get(name)
    elm.SetAttribute(var, value)
def constr(X):
    # evaluate constraints
    # return False if one constraint is violated else return True
    for elm in dict_sets.get("Trafos").GetContents():
        if not(TAPmin<=elm.obj_id.GetAttribute("nntap")<=TAPmax):
            return False
    for elm in dict_sets.get("Gen").GetContents():
        if not(VGmin<=elm.obj_id.bus1.cterm.GetAttribute("m:u")<=VGmax):
            return False
    for elm in dict_sets.get("Barras").GetContents():
        if not(VGmin<=elm.obj_id.GetAttribute("m:u")<=VGmax):
            return False
    for elm in dict_sets.get("Cond").GetContents():
        if not(PQmin<=elm.obj_id.GetAttribute("qgini")<=PQmax):
            return False
    return True
def function(X):
    # Set control variables
    set_attribut('TRAFO_B3_B5', 'nntap', int(X[0]))
    set_attribut('TRAFO_B4_B1', 'nntap', int(X[1]))
    set_attribut('GENERADOR_B2', 'usetp', X[2])
    set_attribut('B_CONDENSADORES_B3', 'qgini', X[3])
    set_attribut('B_CONDENSADORES_B4', 'qgini', X[4])
    # set_attribut('Slack', 'usetp', X[5])
    return get_var("Lines", "c:Losses")
def run(optimizer, function, bds, constr, X0):
    # optimizador
    res = optimizer.optimize(obj_fun=function, bounds=bds, constraints=constr, x0=X0, integer=[0, 1])
    app.PrintPlain('Total Losses: %s\n'%str(res['convergence'][-1]))

##------ variables de control 
TAPmin = 9100
TAPmax = 11100
PQmin = 0.1
PQmax = 5
VGmin = 0.9
VGmax = 1.1

# run MVMO
bds = [
    (TAPmin, TAPmax), # para el Tap TRAFO_B3_B5
    (TAPmin, TAPmax), # para el Tap TRAFO_B4_B1
    (VGmin, VGmax), # tensión nodos de GENERADOR_B2 
    (PQmin, PQmax), # para el B_CONDENSADORES_B3
    (PQmin, PQmax), # para el B_CONDENSADORES_B4
    # (VGmin, VGmax)# tensión nodos de generación SLACK
]
# constain
constr = {'func':constr}
X0 = [9100, 9100, 1.0, 0, 0] # vector inicial

population = 30 # población inicial
n_iter_mvmo = 2000 # número de iteraciones
mutations = 5 # número de mutaciones

# create optimizer
optimizer = MVMO(iterations=n_iter_mvmo, num_mutation=mutations, population_size=population)
# run optimizer
run(optimizer, function, bds, constr, X0)