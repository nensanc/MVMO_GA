
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
    for elm in dict_sets.get("Cond").GetContents():
        if (elm.obj_id.loc_name=="Gen_0003"):
            if not(PQmin<=elm.obj_id.GetAttribute("qgini")<=PQmax2):
                return False
        else:
            if not(PQmin<=elm.obj_id.GetAttribute("qgini")<=PQmax):
                return False
    for elm in dict_sets.get("Barras").GetContents():
        if not(VGmin<=elm.obj_id.GetAttribute("m:u")<=VGmax):
            return False
    return True
def function(X):
    # Set control variables
    set_attribut('Trf_0004_0007', 'nntap', int(X[0]))
    set_attribut('Trf_0004_0009', 'nntap', int(X[1]))
    set_attribut('Trf_0005_0006', 'nntap', int(X[2]))
    set_attribut('Trf_0007_0008', 'nntap', int(X[3]))
    set_attribut('Trf_0007_0009', 'nntap', int(X[4]))

    set_attribut('Gen_0002', 'usetp', X[5])

    set_attribut('Gen_0003', 'qgini', X[6])
    set_attribut('Gen_0006', 'qgini', X[7])
    set_attribut('Gen_0008', 'qgini', X[8])
    # set_attribut('Slack', 'usetp', X[5])
    return get_var("Lines", "c:Losses")
def run(optimizer, function, bds, constr, X0):
    # optimizador
    res = optimizer.optimize(obj_fun=function, bounds=bds, constraints=constr, x0=X0, integer=[0, 1])
    app.PrintPlain('Total Losses: %s\n'%str(res['convergence'][-1]))

##------ límites 
TAPmin = 9100
TAPmax = 11100
PQmin = 0.1
PQmax = 20
PQmax2 = 30
VGmin = 0.9
VGmax = 1.1

# run MVMO
bds = [
    (TAPmin, TAPmax), # para el Tap Trf_0004_0007
    (TAPmin, TAPmax), # para el Tap Trf_0004_0009
    (TAPmin, TAPmax), # para el Tap Trf_0005_0006
    (TAPmin, TAPmax), # para el Tap Trf_0007_0008
    (TAPmin, TAPmax), # para el Tap Trf_0007_0009

    (VGmin, VGmax), # tensión nodos de Gen_0002 

    (PQmin, PQmax), # para el Gen_0003
    (PQmin, PQmax), # para el Gen_0006
    (PQmin, PQmax), # para el Gen_0008
]
# constain
constr = {'func':constr}
X0 = [11100, 11100, 11100, 11100, 11100, 1.0, 0, 0, 0] # vector inicial

population = 30 # población inicial
n_iter_mvmo = 2000 # número de iteraciones
mutations = 5 # número de mutaciones

# create optimizer
optimizer = MVMO(iterations=n_iter_mvmo, num_mutation=mutations, population_size=population)
# run optimizer
run(optimizer, function, bds, constr, X0)