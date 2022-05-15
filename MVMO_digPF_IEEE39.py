
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
    for elm in dict_sets.get("Cond").GetContents():
        if not(PQmin<=elm.obj_id.GetAttribute("qgini")<=PQmax):
            return False
    for elm in dict_sets.get("Barras").GetContents():
        if not(VGmin<=elm.obj_id.GetAttribute("m:u")<=VGmax):
            return False
    return True
def function(X):
    # Set control variables
    set_attribut('Trf 02 - 30', 'nntap', int(X[0]))
    set_attribut('Trf 06 - 31', 'nntap', int(X[1]))
    set_attribut('Trf 10 - 32', 'nntap', int(X[2]))
    set_attribut('Trf 11 - 12', 'nntap', int(X[3]))
    set_attribut('Trf 13 - 12', 'nntap', int(X[4]))
    set_attribut('Trf 19 - 20', 'nntap', int(X[5]))
    set_attribut('Trf 19 - 33', 'nntap', int(X[6]))
    set_attribut('Trf 20 - 34', 'nntap', int(X[7]))
    set_attribut('Trf 22 - 35', 'nntap', int(X[8]))
    set_attribut('Trf 23 - 36', 'nntap', int(X[9]))
    set_attribut('Trf 25 - 37', 'nntap', int(X[10]))
    set_attribut('Trf 29 - 38', 'nntap', int(X[11]))

    set_attribut('G 01', 'usetp', X[12])
    set_attribut('G 03', 'usetp', X[13])
    set_attribut('G 04', 'usetp', X[14])
    set_attribut('G 05', 'usetp', X[15])
    set_attribut('G 06', 'usetp', X[16])
    set_attribut('G 07', 'usetp', X[17])
    set_attribut('G 08', 'usetp', X[18])
    set_attribut('G 09', 'usetp', X[19])
    set_attribut('G 10', 'usetp', X[20])
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
VGmin = 0.8999
VGmax = 1.1001

# fronteras
bds = [
    (TAPmin, TAPmax), # para el Tap Trf 02 - 30
    (TAPmin, TAPmax), # para el Tap Trf 06 - 31
    (TAPmin, TAPmax), # para el Tap Trf 10 - 32
    (TAPmin, TAPmax), # para el Tap Trf 11 - 12
    (TAPmin, TAPmax), # para el Tap Trf 13 - 12
    (TAPmin, TAPmax), # para el Tap Trf 19 - 20
    (TAPmin, TAPmax), # para el Tap Trf 19 - 33
    (TAPmin, TAPmax), # para el Tap Trf 20 - 34
    (TAPmin, TAPmax), # para el Tap Trf 22 - 35
    (TAPmin, TAPmax), # para el Tap Trf 23 - 36
    (TAPmin, TAPmax), # para el Tap Trf 25 - 37
    (TAPmin, TAPmax), # para el Tap Trf 29 - 38

    (VGmin, VGmax), # tensión nodos de G 01 
    (VGmin, VGmax), # tensión nodos de G 03 
    (VGmin, VGmax), # tensión nodos de G 04 
    (VGmin, VGmax), # tensión nodos de G 05 
    (VGmin, VGmax), # tensión nodos de G 06 
    (VGmin, VGmax), # tensión nodos de G 07 
    (VGmin, VGmax), # tensión nodos de G 08 
    (VGmin, VGmax), # tensión nodos de G 09 
    (VGmin, VGmax), # tensión nodos de G 10 
]
# constain
constr = {'func':constr}
X0 = [
        9100, 9100, 9100, 9100, 9100, 9100, 9100, 9100, 9100, 9100, 9100, 9100,
        1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0
    ] # vector inicial

population = 30 # población inicial
n_iter_mvmo = 2000 # número de iteraciones
mutations = 5 # número de mutaciones

# create optimizer
optimizer = MVMO(iterations=n_iter_mvmo, num_mutation=mutations, population_size=population)
# run optimizer
run(optimizer, function, bds, constr, X0)