
import os,sys
from MpGlobalDefines import *
from MpFileAccess import *
from SystemPathMethods import *
#TODO abstract the following functions and move to the ./module/ folder

# ######################################################
# Style Theme CSS
# ######################################################     

def load_css(style_name,object,dict=None,secondary=False):
    """
        
    """
    fpath = os.path.join( MpGlobal.installPath,"style",style_name,""); 

    if not os.path.exists(fpath):
        #object.setStyleSheet("")  # clear the style sheet
        return None;

    dict = read_css_dict(fpath+"theme.dict",dict)
    # when secondary is set to true update the main dictionary with user defined values
    if secondary:  
        dict = read_css_dict(fpath+"user.dict",dict)
        
    # provide the list of default variables.
    # image is the location for custom images for the theme
    dict["IMAGE"       ] =  os.path.join( MpGlobal.installPath,"style",style_name,"images","");
    # default image provides a way of accessing the default texture pack
    dict["IMAGE_DEFAULT"] = os.path.join( MpGlobal.installPath,"style","default", "images","");
    # global image provides a way of accessing the images directory
    dict["IMAGE_GLOBAL"] = os.path.join(  MpGlobal.installPath,"images","");
    #image blank is the location of a blank image
    dict["IMAGE_BLANK" ] = os.path.join(  MpGlobal.installPath,"images","blank.png");
    # style is the location of the directory containing the style
    dict["STYLE"       ] = os.path.join( MpGlobal.installPath,"style",style_name,"");

    # URLS are funny in that they require foward slashes, even on windows
    dict["IMAGE"       ] = dict["IMAGE"       ].replace("\\","/");
    dict["IMAGE_GLOBAL"] = dict["IMAGE_GLOBAL"].replace("\\","/");
    dict["IMAGE_BLANK" ] = dict["IMAGE_BLANK" ].replace("\\","/");
    dict["STYLE"       ] = dict["STYLE"       ].replace("\\","/");
    
    # after loading the dictionary, check for any definitions which contain
    # other definitions
    
    # the following replace is now done while the dict is being read
    #for key in dict: # replace all %key% in the text with value
    #    for sub in dict: # replace all %key% in the text with value
    #        dict[key] = dict[key].replace("%%%s%%"%sub,dict[sub])
    
    R = os.listdir(fpath)

    css = ""

    # load the main css file first, if one exists
    
    if "Main.css" in R:
        css += read_css_file(dict, fpath,"Main") 
        R.remove("Main.css")
    # load all remaining css files    
    for file in R:
        if fileGetExt(file) == "css":
            fname = fileGetName(file)
            if fname[:1] != 'x':
                css += read_css_file(dict, fpath,fname) 

    debugPreboot("Style Sheet: %s Size: %d bytes"%(style_name,len(css)))

    if object != None:
        object.setStyleSheet(css)

    return dict

def read_css_dict(fpath,dict=None):
    """
       reads a css theme color dictionary
       a color dictionary stores color information for the theme    

       a dictionary can be passed to this function with initial values
       that will be overwritten if they exist in the file
    """
    #TODO: redo how dict key values are replaced
    # replace valuesa as they are read in, and prevent infinite loops
    if dict == None:
        dict = {}
    
    
    
    if os.path.exists(fpath):
        l = " "

        rf = open(fpath,"r")
        
        while len(l) != 0:
            l  = rf.readline()
            e = l.strip()
            try:
                if len(e) > 0: # not empty
                    if e[0] != "#": # not a comment

                        # allow continuation to a new line by having the last character in a line
                        # a back slash '\'
                        while e[-1] == '\\':
                            l = rf.readline().strip();
                            e = e[:-1]+" "+l
                            
                        (k,v) = e.split('=>')
                        k = k.strip()
                        v = v.strip()
                        # replace variables that have already been defined in the new variables
                        # as they are read. this allows among other features, the ability to define
                        # one variable use it to expand into others, then redefine it to expand into other
                        # variables. , also the construct, a=red; a=%a%,%a%,%a%; 
                        #   a now equals "red,red,red"
                        for key in dict:
                            v = v.replace("%%%s%%"%key,dict[key]);
                        dict[k] = v
            except:
                pass
            
        rf.close()

    
    return dict
    
def read_css_file(dict,fpath,name):
    """
        reads in a css file into a string buffer
        comments ( /* ... */ ) are removed, as well
        as empty lines
    """
    fname = name + ".css"
    
    css = ""    
    l = " "

    rf = open(os.path.join(fpath,fname),"r")
    lc = 0
    while len(l) != 0:
        l  = rf.readline()
        e = l.strip()
        # allow for comments, ignore empty lines
        if len(e) > 0: # not empty
            if e[:2] != "/*": # not a comment
                # intelligently replace the image url's
                # with the path to a known image
                
                if "%IMAGE%" in e:
                    image = e[e.find("%IMAGE%")+7:e.rfind('.')+4]   # with this, only 3 letter extensions are allowed
                    
                    if image[0] == '/' or image[0] == '\\': # a slash following %IMAGE% is optional
                        image=image[1:]
                        
                    url="%IMAGE%"+image
                    
                    a = (dict["IMAGE"        ]+image).replace('\\','/')  # do i need UnixPathCorrect?           
                    b = (dict["IMAGE_DEFAULT"]+image).replace('\\','/')  # only if the user does not type the resource with  
                    c = (dict["IMAGE_GLOBAL" ]+image).replace('\\','/')  # the corrct case    

                    newurl=dict["IMAGE_BLANK"]                 # default option if none of the next three exist
                    if   os.path.exists( a ): newurl = a       # the resource file from the current style
                    elif os.path.exists( b ): newurl = b       # resource from default stylr
                    elif os.path.exists( c ): newurl = c       # resource from global image folder
                        
                    e = e.replace(url,newurl.replace('\\','/'));
                        
                for key in dict: # replace all %key% in the text with value
                    e = e.replace("%%%s%%"%key,dict[key])
                lc += 1    
                css += e+"\n"
    #print "lc: %d"%lc;            
    rf.close()

    return css

def css_dict_value(key,cdict,rdict):
    """
        rdict: dictionary loaded from a styles dictionary file
        cdcit: a new dictionary
        key:   key to test against
        if rdict contains the key, set convert that value to a QColor
        and store in cdict
    """
    #TODO this lloks like a oneliner that can be inlined somewhere
    if key in rdict:
        cdict[key] = color_stringToQColor(rdict[key])
    return cdict

def color_stringToQColor(string):
    #TODO this function looks un-neccessary
    hex = {'0':0, '1':1, '2':2, '3':3, '4':4,
           '5':5, '6':6, '7':7, '8':8, '9':9,   
           'A':10, 'B':11,'C':12, 'D':13, 'E':14, 'F':15,
           'a':10, 'b':11,'c':12, 'd':13, 'e':14, 'f':15 }
    hex_template = "#XXXXXX" 
    r=0;
    g=0;
    b=0;
    a=1;
    if len(string) == len(hex_template):
        r = hex[string[1]]*16 + hex[string[2]]
        g = hex[string[3]]*16 + hex[string[4]]
        b = hex[string[5]]*16 + hex[string[6]] 
    elif string[:4] == 'rgba':   #rgb(YYX,YYX,YYX)
        # for css alpha is in range 0 to 1.
        (i,j,k,a) = string[5:-1].split(',')
        r = int(i)
        g = int(j)
        b = int(k)
        a = float(a)
    elif string[:3] == 'rgb':   #rgb(YYX,YYX,YYX)
        (i,j,k) = string[4:-1].split(',')
        r = int(i)
        g = int(j)
        b = int(k)
        #string is now YYX,YYX,YYX
    return QColor(r,g,b,255*a);   

def css_save_dict(style_name,fname,dict):
    """
        save a color dictionary 
        sort the values for user convenience
        it is not recommeneded to use this for theme.dict
        the default themes may contain values beyond the standard set
    """
    fpath = os.path.join(MpGlobal.installPath,"style",style_name,fname+".dict")
    
    k = lambda x: x[0]
    R = sorted(dict.items(), key = k)
    
    wf = open(fpath,"w")
    for key,value in R :
        wf.write( "%-20s=> %s\n"%(key,value) )
    wf.close()

    