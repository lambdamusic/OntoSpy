
import time, optparse, os, sys, webbrowser
import rdflib	 # so we have it available as a namespace

from .. import ontospy 
from ..core.util import *
import render

MODULE_VERSION = 0.2
USAGE = "exporter [graph-uri-or-location] [options]"

# 2016-02-04: launched with 'ontospy -e'



# manually edited
RENDER_OPTIONS = [
	(1, "HTML, basic"), 
	(2, "Expandable tree (class hierarchy) [experimental]"), 
	(3, "Expandable tree (property hierarchy) [experimental]"), 
	(4, "Expandable tree (skos hierarchy) [experimental]"), 
	(5, "Expandable tree [all, experimental]"), 
]





def _askVisualization():
	"""
	ask user which viz output to use
	"""
	while True:
		text = "Please select an output format: (q=quit)\n"
		for viz in RENDER_OPTIONS:
			text += "%d) %s\n" % (viz[0], viz[1])
		var = raw_input(text)
		if var == "q":
			return None
		else:
			try:
				n = int(var)
				test = RENDER_OPTIONS[n-1]  #throw exception if number wrong
				return n
			except:
				printDebug("Invalid selection. Please try again.", "important")
				continue



def saveVizLocally(contents, filename = "index.html"):
	filename = ontospy.ONTOSPY_LOCAL_VIZ + "/" + filename 

	f = open(filename,'w')
	f.write(contents) # python will convert \n to os.linesep
	f.close() # you can omit in most cases as the destructor will call it
	
	url = "file:///" + filename
	return url 
	



def saveVizGithub(contents):
	title = "Ontology documentation"
	files = {
	    'index.html' : {
	        'content': contents
	        },
	    'readme.txt' : {
	        'content': "Ontology documentation automatically generated by OntoSPy (https://github.com/lambdamusic/OntoSPy)"
	        }	
	    }
	urls = save_anonymous_gist(title, files)
	return urls






def generateViz(graph, visualization):
	""" 
	<visualization>: an integer mapped to the elements of RENDER_OPTIONS
	"""
	
	if visualization == 1:
		contents = render.htmlBasicTemplate(graph)
	
	elif visualization == 2:
		contents = render.interactiveD3Tree(graph)
	
	elif visualization == 3:
		contents = render.interactiveD3Tree(graph, "properties")
	
	elif visualization == 4:
		contents = render.interactiveD3Tree(graph, "skos")	

	elif visualization == 5:
		contents = render.interactiveD3TreeAll(graph)	
				
	return contents
	





def parse_options():
	"""
	parse_options() -> opts, args

	Parse any command-line options given returning both
	the parsed options and arguments.
	
	https://docs.python.org/2/library/optparse.html
	
	"""
	
	parser = optparse.OptionParser(usage=USAGE, version=ontospy.VERSION)

	parser.add_option("-l", "--library",
			action="store_true", default=False, dest="lib",
			help="Select an ontology from local library.")

	parser.add_option("-g", "--gist",
			action="store_true", default=False, dest="gist",
			help="Save output as a Github Gist.")			
	#
	# parser.add_option("-q", "",
	# 		action="store", type="string", default="", dest="query",
	# 		help="A query string used to match the catalog entries.")
			
	opts, args = parser.parse_args()

	if not args and not opts.lib:
		parser.print_help()
		sys.exit(0)

	return opts, args



	
def main():
	""" command line script """
	eTime = time.time()
	print "OntoSPy " + ontospy.VERSION
	
	ontospy.get_or_create_home_repo() 	
	opts, args = parse_options()
					
	# select from local ontologies:
	if opts.lib:
		ontouri = ontospy.actionSelectFromLocal()
		if ontouri:	
			islocal = True		
		else:	
			raise SystemExit, 1
	else:
		ontouri = args[0]
		islocal = False

	
	# select a visualization
	viztype = _askVisualization()
	if not viztype:
		raise SystemExit, 1
	
	
	# get ontospy graph
	if islocal:
		g = ontospy.get_pickled_ontology(ontouri)
		if not g:
			g = ontospy.do_pickle_ontology(ontouri)	
	else:
		g = ontospy.Graph(ontouri)
	
	
	# viz dispatcher
	contents = generateViz(g, viztype)

	
	# once viz contents are generated, save file locally or on github
	if opts.gist:
		urls = saveVizGithub(contents)
		printDebug("Documentation saved on github", "comment")
		printDebug("Gist: " + urls['gist'], "important")
		printDebug("Blocks Gist: " + urls['blocks'], "important")
		printDebug("Full Screen Blocks Gist: " + urls['blocks_fullwin'], "important")
		url = saveVizGithub(contents)['blocks_fullwin'] # defaults to full win
	else:
		url = saveVizLocally(contents)
		printDebug("Documentation generated", "comment")

	# open browser	
	webbrowser.open(url)

	# finally: print some stats.... 
	sTime = time.time()					
	tTime = eTime - sTime
	printDebug("Time:	   %0.2fs" %  tTime, "comment")




				
	
if __name__ == '__main__':
	
	# from .. import ontospy
	try:
		main()
		sys.exit(0)
	except KeyboardInterrupt, e: # Ctrl-C
		raise e
