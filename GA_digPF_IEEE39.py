##----- import libraries
import powerfactory 
import numpy as np
import autograd.numpy as anp
from pymoo.core.problem import Problem

##----- Initial Settings DigSilent Power Factory
app=powerfactory.GetApplication()
app.ClearOutputWindow() # clear output window
app.EchoOff()
script_fold = app.GetCurrentScript() #to call the current script
active_prj = app.GetActiveProject() # Get Active Project
ldf=app.GetFromStudyCase('ComLdf') # Get low flow calculation 


dict_sets = {} # dictionary of Sets
for e in script_fold.GetContents(): 
    dict_sets[e.loc_name] = e
dict_all_elm = dict(
                    (elm.obj_id.loc_name, elm.obj_id)
                    for elm in dict_sets.get('Get_Ref').Get()
                )

def set_attribut(name, var, value):
    # set attribute at Power Factory 
    elm = dict_all_elm.get(name)
    elm.SetAttribute(var, value)
def constr():
    # evaluate constraints
    # return False if one constraint is violated else return True
    for elm in dict_sets.get("Trafos").GetContents():
        if not(TAPmin<=elm.obj_id.GetAttribute("nntap")<=TAPmax):
            return False
    for elm in dict_sets.get("Gen").GetContents():
        if not(VGmin<=elm.obj_id.bus1.cterm.GetAttribute("m:u")<=VGmax):
            return False
    for elm in dict_sets.get("Capacitors").GetContents():
        if not(PQmin<=elm.obj_id.GetAttribute("qgini")<=PQmax):
            return False
    for elm in dict_sets.get("Barras").GetContents():
        if not(VGmin<=elm.obj_id.GetAttribute("m:u")<=VGmax):
            return False
    return True
def get_var(set_name, var):
    #load flow is executed and loss data is obtained, 
    # if a constraint is violated a value of 1e9 is assigned.
    ldf.Execute()
    result = 0
    for elm in dict_sets.get(set_name).GetContents():
        result += elm.obj_id.GetAttribute(var)
    return result if constr() else 1e9 
def fitness_func(s_x):
    # Set control variables
    losses = []
    for X in s_x:
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
        losses.append(get_var("Lines", "c:Losses"))
    return np.array(losses)

class MyProblem(Problem):
    def __init__(self):
        super().__init__(
            n_var=21,
            n_obj=1,
            n_constr=0,
            xl=anp.array([
                    TAPmin, # para el Tap Trf 02 - 30
                    TAPmin, # para el Tap Trf 06 - 31
                    TAPmin, # para el Tap Trf 10 - 32
                    TAPmin, # para el Tap Trf 11 - 12
                    TAPmin, # para el Tap Trf 13 - 12
                    TAPmin, # para el Tap Trf 19 - 20
                    TAPmin, # para el Tap Trf 19 - 33
                    TAPmin, # para el Tap Trf 20 - 34
                    TAPmin, # para el Tap Trf 22 - 35
                    TAPmin, # para el Tap Trf 23 - 36
                    TAPmin, # para el Tap Trf 25 - 37
                    TAPmin, # para el Tap Trf 29 - 38

                    VGmin, # tensión nodos de G 01 
                    VGmin, # tensión nodos de G 03 
                    VGmin, # tensión nodos de G 04 
                    VGmin, # tensión nodos de G 05 
                    VGmin, # tensión nodos de G 06 
                    VGmin, # tensión nodos de G 07 
                    VGmin, # tensión nodos de G 08 
                    VGmin, # tensión nodos de G 09 
                    VGmin # tensión nodos de G 10 
                    # (VGmin, VGmax)# tensión nodos de generación SLACK
                ]),
            xu=anp.array([
                    TAPmax, # para el Tap Trf 02 - 30
                    TAPmax, # para el Tap Trf 06 - 31
                    TAPmax, # para el Tap Trf 10 - 32
                    TAPmax, # para el Tap Trf 11 - 12
                    TAPmax, # para el Tap Trf 13 - 12
                    TAPmax, # para el Tap Trf 19 - 20
                    TAPmax, # para el Tap Trf 19 - 33
                    TAPmax, # para el Tap Trf 20 - 34
                    TAPmax, # para el Tap Trf 22 - 35
                    TAPmax, # para el Tap Trf 23 - 36
                    TAPmax, # para el Tap Trf 25 - 37
                    TAPmax, # para el Tap Trf 29 - 38

                    VGmax, # tensión nodos de G 01 
                    VGmax, # tensión nodos de G 03 
                    VGmax, # tensión nodos de G 04 
                    VGmax, # tensión nodos de G 05 
                    VGmax, # tensión nodos de G 06 
                    VGmax, # tensión nodos de G 07 
                    VGmax, # tensión nodos de G 08 
                    VGmax, # tensión nodos de G 09 
                    VGmax, # tensión nodos de G 10 
                ])
            )
    def _evaluate(self, x, out, *args, **kwargs):
        f1 = fitness_func(x)
        out["F"] = anp.column_stack([f1])

##------ control variables----- 
TAPmin = 9100
TAPmax = 11100
PQmin = 0.1
PQmax = 20
VGmin = 0.9
VGmax = 1.1

# create MVMO
from pymoo.algorithms.soo.nonconvex.ga import GA
algorithm = GA(
    pop_size=30,
    eliminate_duplicates=True)
# run optimzer
from pymoo.optimize import minimize
res = minimize(MyProblem(),
                algorithm,
                seed=1,
                verbose=True)
# print best solution
app.PrintPlain("Best solution found: \nX = %s\nF = %s" % (res.X, res.F))
