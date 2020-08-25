# Project Proposal: Generating Ideal Cycling Routes

As an avid cyclist, I'm often confronted with the tedious task of designing new routes to ride.
There are several factors that go into this decision making process including but not limited to mileage, elevation change, destination type (if any), overall difficulty, scenery, path type, etc.
I personally enjoy biking around 40-80 miles a trip and visiting the various breweries, wineries, and state parks around the Finger Lakes.
I'm also not always in the mood to tackle the steepest hills that NY has to offer.
Finding a route aligned with these preferences ultimately amounts to some solving some optimization problem.
Furthermore, since riding the same paths becomes boring, the details of this optimization problem should change with each trip in order to promote diversity in route selection.
Since I often I want to forgo the planning process and just go ride, for this project I'd like to formally set up and solve this problem.

Thus the goal of this proposal is two-fold:
1) To generate ideal bike routes based on user preferences and constraints while diversifying routes between trips
2) To alter subsequent routes generation based on user feed-back

# The Model

For this project, I would use the OpenStreetMap API via the OSMnx package in conjuction with elevation and place data from the Google Maps API.
OpenStreetMaps is essentially an open source version of Google Maps and OSMnx is a Python package for simplifying OpenStreetMap API calls and constructing street networks.
Together they allow you to build undirected graphical models of roads that can be used for route planning.
As suggested by its name, the Elevation API from Google Maps provides detailed elevation data for given locations allowing us to compute net elevation changes and route difficulty.
Similarly, the Place API from Google Maps contains the detailed information about points of interest including user reviews.
Note that Google does not offer graphical models of road networks and scraping this is against their terms of service. Hence our use of OSMnx.

Given this information, it's straightforward to find the shortest path between two points using Dijkstra's algorithm or A^{\*} search algorithm.
By upweighting edges by hill grade, we can also introduce impedence factors to account for route difficulty.
Thus a naive model might propose several destinations based on user preferences, calculate the associated shortest path with impedence, and rank the associated paths.

A more sophisticated model would more properly view this problem in the context of multicriteria networks. 
Here the idea is that there is not just a simple distance to minimize as in the standard shortest path case but rather a collection of criteria that must be optimized together.
This is the so-called multiobjective shortest path problem.
While exact solutions are NP-hard, algorithms exist for finding Pareto optimal solutions known as skylines.[^1][^2]
Such algorithms are able to compute skylines for more than 170,000 nodes and edges and are viable for our system size.

# Exploratory Data Analysis

As a first step, I generated a road map of Ithaca, NY (where I live) and the surrounding region using OSMnx see Fig ![fig1](Figures/ithaca_roadmap.svg). I then 


The preliminary work above already provides interesting insight into the political landscape and the existence of author bias in polical media. It suggests that this project is certainly viable and is something I would be excited to pursue this summer.

Notable topics from the LDA clustering can be found below. Note that topic labels have been provided by me.
![fig1](Figures/wordcloud.svg)

[^1]: https://arxiv.org/abs/1410.0205
[^2]: H. Kriegel, M. Renz and M. Schubert, "Route skyline queries: A multi-preference path planning approach," 2010 IEEE 26th International Conference on Data Engineering (ICDE 2010), Long Beach, CA, 2010, pp. 261-272.
