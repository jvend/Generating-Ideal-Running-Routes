#include <Python.h>
#include <iostream>
#include <cmath>

#include <dijkstra.hpp>

static PyObject* print_list(PyObject* self, PyObject* args) {
    
    int Number_of_Nodes;
    int source;
    double target_meters;
    PyObject* lobj;

    // Type checking done below...
    if (!PyArg_ParseTuple(args, "iidO!", &Number_of_Nodes, &source, &target_meters, &PyList_Type, &lobj)) {
        exit(1);
        return NULL;
    }

    /* Convert python object to a "natural C++ object" */
    int V = Number_of_Nodes;
    Graph g(V);

    for (unsigned int i = 0; i < PyList_Size(lobj); ++i) {
        PyObject* lobj_inner = PyList_GetItem(lobj, i);
        PyObject* pyObj_u = PyTuple_GetItem(lobj_inner, 0);
        PyObject* pyObj_v = PyTuple_GetItem(lobj_inner, 1);
        PyObject* pyObj_l = PyTuple_GetItem(lobj_inner, 2);
        PyObject* pyObj_w = PyTuple_GetItem(lobj_inner, 3);
        int u = (int) PyLong_AsLong(pyObj_u);
        int v = (int) PyLong_AsLong(pyObj_v);
        double l = PyFloat_AsDouble(pyObj_l);
        double w = PyFloat_AsDouble(pyObj_w);
        g.addEdge(u,v,l,w);
    }

    std::vector<std::vector<double> > dists_from_source(V);
    std::vector<std::vector<double> > costs_from_source(V);
    std::vector<std::vector<int> > preds_from_source(V);
    for (int dijkstra_source = 0; dijkstra_source < V; dijkstra_source ++){
    g.shortestPath(dijkstra_source);
    dists_from_source[dijkstra_source] = g.dist;
    costs_from_source[dijkstra_source] = g.cost;
    preds_from_source[dijkstra_source] = g.predecessor;
    g.reset_obj();
    }
 
    //double target_meters = 8047.; // about 5 miles
    //double target_meters = 9334.2;
    //double target_meters = 10000;
    double min_cost = 1e307;
    int min_i = -1; int min_j = -1;
    
    // Make loops
    // eventually use a heap to store these
    for (int i=0; i < V; i++){
    for (int j=i; j < V; j++){
        double cost = costs_from_source[source][i] + costs_from_source[source][j] + costs_from_source[i][j];
        double length = dists_from_source[source][i] + dists_from_source[source][j] + dists_from_source[i][j];
        cost += 10*std::abs(target_meters - length); // maybe use std::abs instead
        
        if (cost < min_cost){
            min_cost = cost;
            min_i = i; min_j = j;
        }
    }}

    std::cout << source << " " << min_i << " " << min_j << std::endl;
//    for (unsigned long i=0; i<costs_from_source[3].size(); i++)
//    { std::cout << costs_from_source[3][i] << " "; } std::cout << std::endl << std::endl;
//
//    for (unsigned long i=0; i<dists_from_source[3].size(); i++)
//    { std::cout <<  dists_from_source[3][i] << " "; } std::cout << std::endl << std::endl;
//
//    for (unsigned long i=0; i<preds_from_source[3].size(); i++)
//    { std::cout <<  preds_from_source[3][i] << " "; } std::cout << std::endl << std::endl;

    // Get min cost path 
    // Check ordering of predecessors... 
    std::vector<int> path     = get_shortest_path(source, min_i, preds_from_source[source]);
    std::vector<int> subpath2 = get_shortest_path(min_i,  min_j, preds_from_source[min_i]);
    std::vector<int> subpath3 = get_shortest_path(min_j, source, preds_from_source[min_j]);
    path.pop_back(); subpath2.pop_back();
    path.insert(path.end(),subpath2.begin(),subpath2.end());
    path.insert(path.end(),subpath3.begin(),subpath3.end());
    double length = dists_from_source[source][min_i] + dists_from_source[min_i][min_j] + dists_from_source[min_j][source];
    std::cout << "Length: " << length << std::endl;
    


// Eventually need list of lists of top results stored in heap
    PyObject* list = PyList_New(path.size());
    for (unsigned long i=0; i < path.size(); i++){
        PyObject* node_py  = Py_BuildValue("i", path[i]);
        PyList_SetItem(list,i,node_py);
    }

    
    //return NULL;
    return list;
}   

static PyMethodDef DijkstraMethods[] = {
    {"print_list", print_list, METH_VARARGS,
     "A function that prints a list of strings."},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

static struct PyModuleDef dijkstra_module = {
    PyModuleDef_HEAD_INIT,
    "dijkstra",   /* name of module */
    "dijkstra module", /* module documentation */
    -1,
    DijkstraMethods
};

PyMODINIT_FUNC
PyInit_dijkstra(void) {
    PyObject* m = PyModule_Create(&dijkstra_module);
    if (m == NULL) {
        return NULL;
    }
    return m;
}
