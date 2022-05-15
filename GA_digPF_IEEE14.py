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
        set_attribut('Trf_0004_0007', 'nntap', int(X[0]))
        set_attribut('Trf_0004_0009', 'nntap', int(X[1]))
        set_attribut('Trf_0005_0006', 'nntap', int(X[2]))
        set_attribut('Trf_0007_0008', 'nntap', int(X[3]))
        set_attribut('Trf_0007_0009', 'nntap', int(X[4]))

        set_attribut('Gen_0002', 'usetp', X[5])

        set_attribut('Gen_0003', 'qgini', X[6])
        set_attribut('Gen_0006', 'qgini', X[7])
        set_attribut('Gen_0008', 'qgini', X[8])
        losses.append(get_var("Lines", "c:Losses"))
    return np.array(losses)

class MyProblem(Problem):
    def __init__(self):
        super().__init__(
            n_var=5,
            n_obj=1,
            n_constr=0,
            xl=anp.array([
                    TAPmin,  # para el Tap Trf_0004_0007
                    TAPmin,  # para el Tap Trf_0004_0009
                    TAPmin,  # para el Tap Trf_0005_0006
                    TAPmin,  # para el Tap Trf_0007_0008
                    TAPmin,  # para el Tap Trf_0007_0009
                    VGmin,  # tensión nodos de Gen_0002 
                    PQmin,  # para el Gen_0003
                    PQmin,  # para el Gen_0006
                    PQmin,  # para el Gen_0008
                ]),
            xu=anp.array([
                    TAPmax, # para el Tap Trf_0004_0007
                    TAPmax, # para el Tap Trf_0004_0009
                    TAPmax, # para el Tap Trf_0005_0006
                    TAPmax, # para el Tap Trf_0007_0008
                    TAPmax, # para el Tap Trf_0007_0009
                    VGmax, # tensión nodos de Gen_0002 
                    PQmax, # para el Gen_0003
                    PQmax, # para el Gen_0006
                    PQmax, # para el Gen_0008
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
PQmax2 = 30
VGmin = 0.9
VGmax = 1.1001

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
